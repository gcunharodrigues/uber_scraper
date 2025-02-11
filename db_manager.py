import sqlite3
import logging
from sqlite3 import Error


def insert_batch_data(database, data):
    """ create a database connection to a SQLite database """

    # Configure logging
    logging.basicConfig(
        filename='db_insert.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Database connection
        conn = sqlite3.connect(database)
        cur = conn.cursor()

        # Create table if it doesn't exist
        cur.execute('''CREATE TABLE IF NOT EXISTS ride_data
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    distance TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    total_earning TEXT NOT NULL,
                    base_fare TEXT NOT NULL,
                    customer_fare TEXT NOT NULL,
                    paid_to_driver TEXT NOT NULL,
                    paid_to_uber TEXT NOT NULL,
                    UNIQUE(type, date, time, duration, origin, destination))''')

        # Batch insert using parameterized query
        try:
            query = '''
                INSERT OR IGNORE INTO ride_data
                (type, date, time, duration, distance, origin, destination,
                total_earning, base_fare, customer_fare, paid_to_driver,
                paid_to_uber)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            cur.executemany(query, data)
            conn.commit()
            logging.info(
                f"Successfully inserted/updated {cur.rowcount} records")

        except Error as e:
            conn.rollback()
            logging.error(f"Insert/update failed: {str(e)}")
            raise

    finally:
        if conn:
            cur.close()
            conn.close()
            logging.info("Database connection closed")


def view_all_data(database):
    try:
        # Database connection
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("SELECT * FROM ride_data")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Error as e:
        print(e)
    finally:
        if conn:
            cur.close()
            conn.close()


def execute_query(database, query):
    try:
        # Database connection
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(e)
    finally:
        if conn:
            cur.close()
            conn.close()
