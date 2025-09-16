import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Загружаем переменные окружения
load_dotenv()


def debug_database():
    print("=== ОТЛАДКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ ===")

    # 1. Проверяем переменные окружения
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

    print("Переменные окружения:")
    print(f"  DB_HOST: {DB_HOST}")
    print(f"  DB_PORT: {DB_PORT}")
    print(f"  DB_NAME: {DB_NAME}")
    print(f"  DB_USER: {DB_USER}")
    print(f"  DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}")

    # 2. Пробуем подключиться
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✓ Подключение к БД успешно")

        cursor = conn.cursor()

        # 3. Проверяем существование таблицы
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'forecasts'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"✓ Таблица forecasts существует: {table_exists}")

        # 4. Проверяем структуру таблицы
        if table_exists:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'forecasts'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("Структура таблицы forecasts:")
            for col in columns:
                print(f"  {col[0]} ({col[1]})")

        # 5. Проверяем текущие данные
        cursor.execute("SELECT COUNT(*) FROM forecasts;")
        count = cursor.fetchone()[0]
        print(f"✓ Записей в таблице: {count}")

        cursor.close()
        conn.close()
        print("✓ Соединение закрыто")

    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return False

    return True


def test_insert():
    print("\n=== ТЕСТ ЗАПИСИ ДАННЫХ ===")

    try:
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'postgres')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Тестовая запись
        test_data = [('2025-01-01', 100.5, 90.0, 110.0, 'test_model')]

        insert_query = """
        INSERT INTO forecasts 
            (forecast_date, predicted_value, confidence_lower, confidence_upper, model_name)
        VALUES %s
        ON CONFLICT (forecast_date) 
        DO UPDATE SET
            predicted_value = EXCLUDED.predicted_value,
            confidence_lower = EXCLUDED.confidence_lower,
            confidence_upper = EXCLUDED.confidence_upper,
            model_name = EXCLUDED.model_name,
            created_at = CURRENT_TIMESTAMP;
        """

        execute_values(cursor, insert_query, test_data)
        conn.commit()

        print("✓ Тестовая запись добавлена успешно")

        # Проверяем что записалось
        cursor.execute("SELECT * FROM forecasts WHERE model_name = 'test_model';")
        result = cursor.fetchone()
        print(f"✓ Тестовая запись: {result}")

        # Удаляем тестовую запись
        cursor.execute("DELETE FROM forecasts WHERE model_name = 'test_model';")
        conn.commit()
        print("✓ Тестовая запись удалена")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"✗ Ошибка при тестовой записи: {e}")
        return False

    return True


if __name__ == "__main__":
    debug_database()
    test_insert()