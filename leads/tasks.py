

from celery import shared_task
from celery.utils.log import get_task_logger
import pandas as pd
import io
import math
from decimal import Decimal, InvalidOperation
from .models import Lead, TempCSVImport
from accounts.models import Users

# 1. Setup the Logger (So you see errors in your terminal)
logger = get_task_logger(__name__)

@shared_task
def process_csv_from_db(file_id, user_id):
    temp_file = None
    try:
        logger.info(f"Starting task for file_id: {file_id}")

        # 1. Fetch the binary data
        try:
            temp_file = TempCSVImport.objects.get(id=file_id)
            user = Users.objects.get(id=user_id)
        except (TempCSVImport.DoesNotExist, Users.DoesNotExist) as e:
            logger.error(f"Setup Error: {e}")
            return f"Failed: {e}"

        # 2. Convert binary -> Virtual File
        file_buffer = io.BytesIO(temp_file.file_content)

        # 3. Process with Pandas
        chunks = pd.read_csv(file_buffer, chunksize=5000)
        total_created = 0

        for chunk in chunks:
            leads_batch = []
            
            for _, row in chunk.iterrows():
                # --- SAFE DECIMAL PARSING ---
                try:
                    raw_val = row.get('value', 0)
                    # Handle "NaN" or empty strings which crash Decimal
                    if pd.isna(raw_val) or str(raw_val).strip() == '':
                        val = Decimal(0)
                    else:
                        val = Decimal(str(raw_val))
                except (InvalidOperation, ValueError):
                    val = Decimal(0)

                # --- SAFE DATE PARSING (CRITICAL FIX) ---
                raw_date = row.get('expected_closure_date')
                closure_date = pd.to_datetime(raw_date, errors='coerce')
                
                # Check for NaT (Not a Time) - This crashes Django if not fixed
                if pd.isna(closure_date):
                    closure_date = None

                # --- Create Object ---
                leads_batch.append(Lead(
                    name=row.get('name', 'Unknown Client'),
                    source=row.get('source', 'manual'),
                    status=row.get('status', 'inprogress'),
                    value=val,
                    expected_closure_date=closure_date,  # Uses the cleaned None or Date
                    description=row.get('description', ''),
                    handler=user
                ))
            
            # 4. Bulk Insert
            if leads_batch:
                Lead.objects.bulk_create(leads_batch, batch_size=5000, ignore_conflicts=True)
                total_created += len(leads_batch)

        logger.info(f"SUCCESS: Created {total_created} leads from {temp_file.file_name}")
        return f"Success: {total_created} leads imported."

    except Exception as e:
        # 5. Log the full crash to the terminal
        logger.error(f"CRITICAL FAILURE processing file {file_id}: {e}", exc_info=True)
        return f"Error: {str(e)}"
    
    finally:
        # 6. Cleanup
        if temp_file:
            temp_file.delete()
            logger.info(f"Cleanup: Temporary file {file_id} deleted.")