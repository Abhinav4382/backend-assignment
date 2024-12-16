import redis
import math
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from datetime import datetime, timedelta

# Connect to Redis
redis_client = redis.StrictRedis(
    host="redis-19016.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com",
    port=19016,
    db=0,
    password="SuqYNaB8x6Fqg926uQ41mupww9mLBysr",
    username="default",
    decode_responses=True,  # To decode responses as strings
)

def get_cache_key(facility, start_date, end_date):
    """Generate a Redis-compatible cache key."""
    return f"emissions:{facility}:{start_date.strftime('%Y-%m-%d')}:{end_date.strftime('%Y-%m-%d')}"

def get_transactions(start_date, end_date, business_facilities):
    return Transaction.objects.filter(
        transaction_date__range=(start_date, end_date),
        business_facility__in=business_facilities
    )

class TotalEmissionsAPI(APIView):
    def post(self, request):
        """Process a POST request to calculate total emissions."""
        start_date = request.data.get("startDate")
        end_date = request.data.get("endDate")
        business_facilities = request.data.get("businessFacilities")

        # Convert input dates to Python date objects
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        total_emissions_by_facility = {}

        # Process each facility
        for facility in business_facilities:
            total_emissions_by_facility[facility] = self.process_facility(
                facility, start_date_obj, end_date_obj
            )
        return Response(total_emissions_by_facility, status=status.HTTP_200_OK)

    def process_facility(self, facility, start_date, end_date):
        """Process emissions for a single facility using cached and uncached ranges."""
        total_emission = 0
        cached_ranges = []
        if end_date<start_date: return 0
        # Fetch cached ranges for the facility
        pattern = f"emissions:{facility}:*"
        matching_keys = redis_client.keys(pattern)

        for key in matching_keys:
            # Parse the key and extract cached date ranges
            key_parts = key.split(":")
            if len(key_parts) != 4:
                continue  # Skip malformed keys

            _,_, cached_start_date, cached_end_date = key_parts
            cached_start = datetime.strptime(cached_start_date, "%Y-%m-%d").date()
            cached_end = datetime.strptime(cached_end_date, "%Y-%m-%d").date()

            if cached_end >= start_date and cached_start <= end_date:
                # Determine the overlapping range
                overlap_start = max(start_date, cached_start)
                overlap_end = min(end_date, cached_end)

                # Retrieve the cached value
                cached_value = redis_client.get(key)
                if cached_value:
                    try:
                        cached_value = float(cached_value)  # Ensure the cached value is a float
                    except ValueError:
                        print(f"Invalid cached value for key {key}: {cached_value}")
                        cached_value = 0

                    # Subtract emissions for non-overlapping parts of the cached range
                    if cached_start < overlap_start:
                        # Calculate emissions for the portion before the overlap
                        left_excess_emission = self.calculate_emissions(facility, cached_start,
                                                                        overlap_start - timedelta(days=1))
                        cached_value -= left_excess_emission

                    if cached_end > overlap_end:
                        # Calculate emissions for the portion after the overlap
                        right_excess_emission = self.calculate_emissions(facility, overlap_end + timedelta(days=1),
                                                                         cached_end)
                        cached_value -= right_excess_emission

                    # Add the adjusted cached value for the overlapping range
                    total_emission += cached_value

                    # Add any uncovered ranges outside the cached data
                    if start_date < overlap_start:
                        total_emission += self.calculate_emissions(facility, start_date,
                                                                   overlap_start - timedelta(days=1))
                    if end_date > overlap_end:
                        total_emission += self.calculate_emissions(facility, overlap_end + timedelta(days=1), end_date)

                    # Track the overlapping range
                    cached_ranges.append({"start_date": overlap_start, "end_date": overlap_end})
                    key = get_cache_key(facility, start_date, end_date)
                    redis_client.set(key, total_emission)
        # Handle uncached parts by identifying gaps in cached ranges
        total_emission+=self.calculate_emissions(facility, start_date, end_date)
        key = get_cache_key(facility, start_date, end_date)
        redis_client.set(key, total_emission)
        """
        uncached_ranges = self.get_uncached_ranges(start_date, end_date, cached_ranges)

        for uncached_range in uncached_ranges:
            range_start = uncached_range["start_date"]
            range_end = uncached_range["end_date"]

            # Calculate emissions for this uncached range
            emissions = self.calculate_emissions(facility, range_start, range_end)
            total_emission += emissions

            # Cache the newly calculated range
            small_range_key = get_small_range_cache_key(facility, range_start, range_end)
            redis_client.set(small_range_key, emissions)
        """
        return total_emission

    def calculate_emissions(self, facility, start_date, end_date):
        """Calculate emissions for a given facility and date range."""
        total_emission = 0
        transactions = get_transactions(start_date, end_date, [facility])
        for transaction in transactions:
            try:
                co2_item = transaction.co2_item if transaction.co2_item is not None and not math.isnan(
                    transaction.co2_item) else 0
                units = transaction.units if transaction.units is not None and transaction.units > 0 else 0
                total_emission += round(units * co2_item, 2) if co2_item and units else 0
            except (ValueError, TypeError):
                total_emission += 0
        return total_emission

    def get_uncached_ranges(self, start_date, end_date, cached_ranges):
        """Identify uncached date ranges given a list of cached ranges."""

        uncached_ranges = []
        current_start = start_date

        for cached_range in sorted(cached_ranges, key=lambda x: x["start_date"]):
            if current_start < cached_range["start_date"]:
                uncached_ranges.append({
                    "start_date": current_start,
                    "end_date": cached_range["start_date"] - timedelta(days=1)
                })
            current_start = max(current_start, cached_range["end_date"] + timedelta(days=1))

        if current_start <= end_date:
            uncached_ranges.append({"start_date": current_start, "end_date": end_date})

        return uncached_ranges
