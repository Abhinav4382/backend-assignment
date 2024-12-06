from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from datetime import datetime
import hashlib
import math  

class TotalEmissionsAPI(APIView):
    def get_cache_key(self, start_date, end_date, business_facilities):
        sorted_business_facilities = sorted(business_facilities)
        
        business_facilities_string = '-'.join(sorted_business_facilities)

        cache_key = f"{start_date}-{end_date}-{business_facilities_string}"

        return hashlib.md5(cache_key.encode()).hexdigest()

    def post(self, request):
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        business_facilities = request.data.get('businessFacilities')
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        cache_key = self.get_cache_key(start_date, end_date, business_facilities)

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        transactions = self.get_transactions(start_date_obj, end_date_obj, business_facilities)

        emissions_by_facility = {}
        for transaction in transactions:
            # Check for invalid or missing data and handle accordingly
            try:
                # Ensure that co2_item is a valid number and units is a positive number
                co2_item = transaction.co2_item if transaction.co2_item is not None and not math.isnan(transaction.co2_item) else 0
                units = transaction.units if transaction.units is not None and transaction.units > 0 else 0
                
                # Calculate total emission only if co2_item and units are valid
                total_emission = round(units * co2_item, 2) if co2_item and units else 0

            except (ValueError, TypeError):
                # Handle cases where data is invalid, default to 0 if error occurs
                total_emission = 0

            emissions_by_facility[transaction.business_facility] = (
                emissions_by_facility.get(transaction.business_facility, 0) + total_emission
            )


        response_data = [
            {"business_facility": facility, "total_emissions": emissions}
            for facility, emissions in emissions_by_facility.items()
        ]

      
        merged_data = self.merge_cache_data(start_date_obj, end_date_obj, business_facilities, emissions_by_facility)

        cache.set(cache_key, merged_data, timeout=3600)

        return Response(merged_data, status=status.HTTP_200_OK)

    def merge_cache_data(self, start_date, end_date, business_facilities, new_data):
    
        merged_data = new_data

        for facility in business_facilities:
            partial_cache_key = self.get_cache_key(start_date, end_date, [facility])

            partial_cached_data = cache.get(partial_cache_key)
            if partial_cached_data:
                for cached_facility_data in partial_cached_data:
                    if cached_facility_data["business_facility"] == facility:
                        merged_data[facility] = (
                            merged_data.get(facility, 0) + cached_facility_data["total_emissions"]
                        )

        return merged_data

    def get_transactions(self, start_date, end_date, business_facilities):
        return Transaction.objects.filter(
            transaction_date__range=(start_date, end_date),
            business_facility__in=business_facilities
        )
