import os

import psycopg2
from psycopg2 import sql

class PostgresDB:

    def __init__(self):
        """Initialize connection parameters."""
        self.dbname = 'postgres'
        self.user = 'butler_admin'
        self.password = os.environ['postgres_pw']
        self.host = 'butler-dev-database.postgres.database.azure.com'
        self.port = '5432'
        self.connection = None
        self.cursor = None


    def connect(self):
        """Create a connection to the database."""
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Connection to the database established.")
        except Exception as e:
            print(f"Error connecting to database: {e}")


    def disconnect(self):
        """Closes the connection to the PostgreSQL database."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Connection closed.")

    def execute_query(self, query, params=None):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def fetch_all(self, query, params=None):
        """Fetches all rows from a query."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def fetch_one(self, query, params=None):
        """Fetches a single row from a query."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def insert(self, table, columns, values):
        """Inserts data into a table."""
        query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})").format(
            table=sql.Identifier(table),
            columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
            values=sql.SQL(', ').join(sql.Placeholder() * len(values))
        )
        self.execute_query(query, values)
        # if self.conn:
        #     self.disconnect()

    def update(self, table, set_columns, set_values, where_clause, where_values):
        """Updates data in a table."""
        set_clause = sql.SQL(', ').join(
            sql.SQL("{} = %s").format(sql.Identifier(col)) for col in set_columns
        )
        query = sql.SQL("UPDATE {table} SET {set_clause} WHERE {where_clause}").format(
            table=sql.Identifier(table),
            set_clause=set_clause,
            where_clause=sql.SQL(where_clause)
        )
        self.execute_query(query, set_values + where_values)

    def delete(self, table, where_clause, where_values):
        """Deletes data from a table."""
        query = sql.SQL("DELETE FROM {table} WHERE {where_clause}").format(
            table=sql.Identifier(table),
            where_clause=sql.SQL(where_clause)
        )
        self.execute_query(query, where_values)

# # Example usage
# if __name__ == "__main__":
#     db = PostgresDB(user="myuser", password="mypassword", host="localhost", port="5432", dbname="mydatabase")
#     db.connect()
#
#     # Insert
#     db.insert("mytable", ["name", "age"], ["John", 30])
#
#     # Update
#     db.update("mytable", ["age"], [31], "name = %s", ["John"])
#
#     # Select
#     rows = db.fetch_all("SELECT * FROM mytable")
#     print(rows)
#
#     # Delete
#     db.delete("mytable", "name = %s", ["John"])
#
#     db.disconnect()
