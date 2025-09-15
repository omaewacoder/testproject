from src.database.db_connection import db
from src.database.models import create_tables, insert_sample_data

print("🛠️ Preparing database for DBeaver...")
create_tables()
insert_sample_data()

# Добавим больше тестовых данных
extra_data = [
    ('2024-01-04', 107.8),
    ('2024-01-05', 110.2),
    ('2024-01-06', 108.5)
]

for date, value in extra_data:
    db.execute_command(
        "INSERT INTO time_series_data (date, value) VALUES (%s, %s)",
        (date, value)
    )

print("✅ Database ready for DBeaver connection")
db.close()
