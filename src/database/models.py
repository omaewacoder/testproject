from .db_connection import db


def create_tables():
    """Create necessary tables if they don't exist"""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS time_series_data (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            value FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS forecasts (
            id SERIAL PRIMARY KEY,
            forecast_date DATE NOT NULL,
            predicted_value FLOAT NOT NULL,
            model_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    for command in commands:
        db.execute_command(command)
    print("✅ Tables created successfully")


def insert_sample_data():
    """Insert sample data for testing"""
    sample_data = [
        ('2024-01-01', 100.0),
        ('2024-01-02', 102.5),
        ('2024-01-03', 105.2),
    ]

    for date, value in sample_data:
        db.execute_command(
            "INSERT INTO time_series_data (date, value) VALUES (%s, %s)",
            (date, value)
        )
    print("✅ Sample data inserted")