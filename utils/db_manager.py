"""
Database manager for Hospital Management System.
Handles SQLite connection, initialization, and core CRUD operations.
"""

import os
import sqlite3


class HospitalDB:
    """
    Central database class for HMS.
    Manages all table creation and provides connection handling.
    """

    def __init__(self, db='hospital.db'):
        """
        Initialize database connection and create tables.

        Args:
            db (str): Path to SQLite database file.
        """
        # Get the folder where THIS file (db_manager.py) lives
        # db_manager.py is in utils/, so go up one level to project root
        utils_folder = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(utils_folder)
        # Force hospital.db to be in project root, always
        self.db = os.path.join(project_root, db)
        self._init_db()

    def _conn(self):
        """
        Create and return a database connection with Row factory.

        Returns:
            sqlite3.Connection: Configured database connection.
        """
        connection = sqlite3.connect(self.db)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self):
        """
        Initialize all required tables if they don't exist.
        Creates: patients, doctors, appointments, bills, wards.
        """
        schema = """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT,
                phone TEXT,
                blood_type TEXT,
                ward TEXT
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialisation TEXT,
                department TEXT
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER REFERENCES patients(id),
                doctor_id INTEGER REFERENCES doctors(id),
                date TEXT,
                time TEXT,
                reason TEXT,
                status TEXT DEFAULT 'Scheduled'
            );

            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER REFERENCES patients(id),
                amount REAL,
                description TEXT,
                status TEXT DEFAULT 'Unpaid',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS wards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                capacity INTEGER,
                occupied INTEGER DEFAULT 0
            );
        """
        try:
            with self._conn() as conn:
                conn.executescript(schema)
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise

    def execute_query(self, query, parameters=()):
        """
        Execute a parameterized query safely.

        Args:
            query (str): SQL query with ? placeholders.
            parameters (tuple): Values to substitute.

        Returns:
            sqlite3.Cursor: Result cursor.
        """
        try:
            with self._conn() as conn:
                return conn.execute(query, parameters)
        except sqlite3.Error as e:
            print(f"Query error: {e}")
            raise

    def fetch_all(self, query, parameters=()):
        """
        Fetch all rows from a query.

        Args:
            query (str): SQL SELECT statement.
            parameters (tuple): Query parameters.

        Returns:
            list: List of sqlite3.Row objects.
        """
        try:
            with self._conn() as conn:
                return conn.execute(query, parameters).fetchall()
        except sqlite3.Error as e:
            print(f"Fetch error: {e}")
            raise

    def fetch_one(self, query, parameters=()):
        """
        Fetch a single row from a query.

        Args:
            query (str): SQL SELECT statement.
            parameters (tuple): Query parameters.

        Returns:
            sqlite3.Row or None: Single result row.
        """
        try:
            with self._conn() as conn:
                return conn.execute(query, parameters).fetchone()
        except sqlite3.Error as e:
            print(f"Fetch error: {e}")
            raise