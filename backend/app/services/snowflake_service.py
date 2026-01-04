import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database", "mock_snowflake.db")

class SnowflakeService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        """
        conn = self.get_connection()
        try:
            # For security in real app we use parameterized queries, but here we expect generated SQL
            # We should at least be careful about restricted commands (DROP, DELETE etc)
            if "DROP" in query.upper() or "DELETE" in query.upper():
                 raise ValueError("Destructive queries are not allowed.")
            
            df = pd.read_sql_query(query, conn)
            return df.to_dict(orient="records")
        except Exception as e:
            print(f"Error executing query: {e}")
            raise e
        finally:
            conn.close()

    def get_schema_info(self) -> str:
        """
        Returns schema information for the LLM to understand table structures.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_text = ""
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_strings = [f"{col[1]} ({col[2]})" for col in columns]
            schema_text += f"Table: {table_name}\nColumns: {', '.join(col_strings)}\n\n"
            
        conn.close()
        return schema_text

snowflake_service = SnowflakeService()
