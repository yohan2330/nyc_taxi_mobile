#!/usr/bin/env python3
"""
Database Initialization Script for NYC Taxi Driver Availability
Run this to set up a fresh database with sample data
"""

import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize a fresh database with schema and sample data"""
    
    # Remove existing database if it exists
    if os.path.exists('nyc_taxi.db'):
        os.remove('nyc_taxi.db')
        print("🗑️  Removed existing database")
    
    # Create new database
    conn = sqlite3.connect('nyc_taxi.db')
    cursor = conn.cursor()
    
    print("🚀 Creating new database...")
    
    # Create tables
    cursor.execute('''
        CREATE TABLE drivers (
            driver_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            license_plate TEXT NOT NULL,
            rating REAL,
            total_trips INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE driver_locations (
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
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_locations_availability ON driver_locations(is_available, last_update)')
    cursor.execute('CREATE INDEX idx_locations_coords ON driver_locations(latitude, longitude)')
    
    print("✅ Database schema created successfully!")
    
    # Add some sample data for testing
    sample_drivers = [
        ('DRV_TEST_001', 'Test Driver One', 'standard', 'TEST001', 4.5, 25),
        ('DRV_TEST_002', 'Test Driver Two', 'premium', 'TEST002', 4.8, 42),
        ('DRV_TEST_003', 'Test Driver Three', 'suv', 'TEST003', 4.3, 18)
    ]
    
    sample_locations = [
        ('DRV_TEST_001', 40.7128, -74.0060, 1, 5),
        ('DRV_TEST_002', 40.7589, -73.9851, 1, 3),
        ('DRV_TEST_003', 40.7282, -73.7949, 0, 10)
    ]
    
    cursor.executemany(
        'INSERT INTO drivers (driver_id, name, vehicle_type, license_plate, rating, total_trips) VALUES (?, ?, ?, ?, ?, ?)',
        sample_drivers
    )
    
    cursor.executemany(
        'INSERT INTO driver_locations (driver_id, latitude, longitude, is_available, eta_minutes) VALUES (?, ?, ?, ?, ?)',
        sample_locations
    )
    
    conn.commit()
    conn.close()
    
    print("✅ Sample test data added!")
    print("📊 Database ready for use!")
    print("💡 Now run 'python app.py' to start the server")

if __name__ == '__main__':
    init_database()