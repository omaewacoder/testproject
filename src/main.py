import os
from dotenv import load_dotenv
from src.database.db_connection import db
from src.database.models import create_tables, insert_sample_data


def main():
    """Main function"""
    load_dotenv()
    print("📊 Time Series Forecast Project")

    # Database operations
    if db.connection:
        create_tables()
        insert_sample_data()

        # Test query
        results = db.execute_query("SELECT * FROM time_series_data")
        if results:
            print("📋 Sample data from database:")
            for row in results:
                print(f"  {row[1]}: {row[2]}")

    db.close()


if __name__ == "__main__":
    main()