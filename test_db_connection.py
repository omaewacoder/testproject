from src.database.db_connection import Database


def test_connection():
    """Тестируем КОНКРЕТНО db_connection.py"""
    print("🔌 Testing db_connection.py...")

    # Создаем экземпляр класса из db_connection.py
    db = Database()

    # Проверяем подключение
    if db.connection:
        print("✅ db_connection.py: Connection successful")

        # Проверяем метод execute_query
        result = db.execute_query("SELECT version()")
        if result:
            print("✅ db_connection.py: Query execution works")

        # Проверяем метод execute_command
        success = db.execute_command("SELECT 1")
        if success:
            print("✅ db_connection.py: Command execution works")
    else:
        print("❌ db_connection.py: Connection failed")

    db.close()


if __name__ == "__main__":
    test_connection()