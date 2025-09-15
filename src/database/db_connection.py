import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters from environment variables"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432),
            'database': os.getenv('DB_NAME', 'mydatabase'),
            'user': os.getenv('DB_USER', 'myuser'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    def connect(self):
        """Establish database connection"""
        try:
            params = self.get_connection_params()
            self.connection = psycopg2.connect(**params)
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connection = None

    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute SELECT query and return results"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                return None
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return None

    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute INSERT/UPDATE/DELETE command"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(command, params)
                self.connection.commit()
                return True
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            self.connection.rollback()
            return False

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")


# Singleton instance
db = Database()