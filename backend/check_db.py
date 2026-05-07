from app.database import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()
inspector = inspect(db.bind)

for table_name in inspector.get_table_names():
    print(f'\n=== {table_name} ===')
    for column in inspector.get_columns(table_name):
        pk = 'PK' if column['primary_key'] else ''
        fk = 'FK' if column.get('foreign_keys') else ''
        nullable = 'NULL' if column['nullable'] else 'NOT NULL'
        print(f'{column["name"]} {column["type"]} {pk} {fk} {nullable}')

db.close()