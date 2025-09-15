from src.database.db_connection import db
from src.database.models import create_tables, insert_sample_data


def test_models():
    """Тестируем КОНКРЕТНО models.py"""
    print("🏗️ Testing models.py...")

    # Проверяем функцию create_tables из models.py
    create_tables()
    print("✅ models.py: create_tables() works")

    # Проверяем функцию insert_sample_data из models.py
    insert_sample_data()
    print("✅ models.py: insert_sample_data() works")

    # Проверяем, что данные действительно inserted
    results = db.execute_query("SELECT COUNT(*) FROM time_series_data")
    if results and results[0][0] > 0:
        print(f"✅ models.py: Data inserted correctly ({results[0][0]} records)")
    else:
        print("❌ models.py: No data found")


if __name__ == "__main__":
    test_models()
    db.close()