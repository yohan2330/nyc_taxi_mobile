import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='nyc_taxi.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Drivers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                license_plate TEXT NOT NULL,
                rating REAL,
                total_trips INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Driver locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS driver_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                is_available BOOLEAN DEFAULT 1,
                eta_minutes INTEGER DEFAULT 5,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (driver_id) REFERENCES drivers (driver_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_locations_availability 
            ON driver_locations(is_available, last_update)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_locations_coords 
            ON driver_locations(latitude, longitude)
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=()):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def clear_data(self):
        """Clear all existing data"""
        self.execute_query("DELETE FROM drivers")
        self.execute_query("DELETE FROM driver_locations")