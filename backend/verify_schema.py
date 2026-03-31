from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print('=== TABLES IN DATABASE ===')
for table in sorted(tables):
    print(f'✓ {table}')

print('\n=== DRIVERS TABLE COLUMNS ===')
drivers_columns = inspector.get_columns('drivers')
for col in drivers_columns:
    col_type = str(col['type'])
    print(f'  - {col["name"]}: {col_type}')

print('\n=== DRIVER_DOCUMENTS TABLE ===')
if 'driver_documents' in tables:
    doc_columns = inspector.get_columns('driver_documents')
    print('✓ Table exists with columns:')
    for col in doc_columns:
        col_type = str(col['type'])
        print(f'  - {col["name"]}: {col_type}')
else:
    print('✗ Table not found')

print('\n=== VERIFICATION FIELDS IN DRIVERS ===')
verification_fields = ['verification_status', 'verification_notes', 'verified_at', 'verified_by']
for field in verification_fields:
    exists = any(col['name'] == field for col in drivers_columns)
    status = '✓' if exists else '✗'
    print(f'{status} {field}')
