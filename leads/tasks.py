from celery import shared_task
import pandas as pd
import io
from decimal import Decimal, InvalidOperation
from .models import Lead, TempCSVImport
from accounts.models import Users

@shared_task
def process_csv_from_db(file_id, user_id):
    temp_file = None
    try:
        # 1. Fetch the binary data
        temp_file = TempCSVImport.objects.get(id=file_id)
        user = Users.objects.get(id=user_id)

        # 2. Convert binary -> Virtual File
        file_buffer = io.BytesIO(temp_file.file_content)

        # 3. Process with Pandas (Chunking for memory safety)
        # We read 5000 rows at a time so your server never crashes
        chunks = pd.read_csv(file_buffer, chunksize=5000)

        for chunk in chunks:
            leads_batch = []
            
            for _, row in chunk.iterrows():
                # Safe Decimal Logic (Handle empty or text values in 'value' column)
                try:
                    val = Decimal(str(row.get('value', 0)))
                except (InvalidOperation, ValueError):
                    val = Decimal(0)

                # Create the Lead Object (in memory)
                leads_batch.append(Lead(
                    name=row.get('name', 'Unknown Client'),
                    source=row.get('source', 'manual'),
                    status=row.get('status', 'inprogress'),
                    value=val,
                    # Handle Date parsing safely
                    expected_closure_date=pd.to_datetime(row.get('expected_closure_date'), errors='coerce'),
                    description=row.get('description', ''),
                    handler=user
                ))
            
            # 4. Bulk Insert to Real Database
            Lead.objects.bulk_create(leads_batch, batch_size=5000, ignore_conflicts=True)

        return f"Success: {temp_file.file_name} processed."

    except TempCSVImport.DoesNotExist:
        return "Error: File not found in buffer."
    except Exception as e:
        return f"Error: {str(e)}"
    
    finally:
        # 5. CRITICAL: Delete the temp data to free up space
        if temp_file:
            temp_file.delete()