import os
import django
from dotenv import load_dotenv


# Load environment variables from .env file (if you're using one)
load_dotenv()

# Set the DJANGO_SETTINGS_MODULE environment variable before initializing Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

# Initialize Django
django.setup()
from api.models import Transaction
import pandas as pd
from datetime import datetime

# File path and chunk size
csv_file_path = 'duc_results_gf.csv'  # Adjust path if necessary
chunk_size = 10000  # Adjust chunk size based on your available memory
all_transactions = []

# Process CSV in chunks
for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size):
    # Clean up column names
    chunk.columns = chunk.columns.str.strip().str.replace(' ', '_').str.lower()

    # Select only the desired columns
    desired_columns = ['transaction_date', 'business_facility', 'units', 'co2_item']
    chunk = chunk[desired_columns]

    # Process each row in the chunk
    for index, row in chunk.iterrows():
        try:
            # Convert date string to date object if necessary
            transaction_date = datetime.strptime(row['transaction_date'], '%d/%m/%y').date()

            # Create a list of Transaction instances
            transaction = Transaction(
                transaction_date=transaction_date,
                business_facility=row['business_facility'],
                units=row['units'],
                co2_item=row['co2_item'],
            )

            all_transactions.append(transaction)

        except Exception as e:
            print(f"Error processing row {index}: {e}")

    # After processing each chunk, save all transactions in bulk
    if all_transactions:
        try:
            # Bulk insert all transactions in the list
            Transaction.objects.bulk_create(all_transactions, batch_size=1000)
            all_transactions = []  # Reset the list after bulk insert
        except Exception as e:
            print(f"Error during bulk insert: {e}")

print("Data inserted successfully")
