from flask import Flask, jsonify, request
from flask_cors import CORS
from Backend.database import Database
from Backend.data_processor import DataProcessor
import math
import os

app = Flask(__name__)
CORS(app)

# Initialize database and data processor
db = Database()
data_processor = DataProcessor(db)

@app.route('/')
def hello():
    return jsonify({
        'message': 'NYC Taxi Driver Availability API - Real Data',
        'status': 'running',
        'endpoints': {
            '/api/drivers/availability': 'GET - Get available drivers with real NYC data',
            '/api/stats/summary': 'GET - Get dashboard statistics',
            '/api/data/process': 'POST - Process real NYC taxi data',
            '/api/data/status': 'GET - Get data processing status'
        }
    })

@app.route('/api/drivers/availability', methods=['GET'])
def get_driver_availability():
    try:
        # Get query parameters
        date = request.args.get('date', '')
        time_range = request.args.get('time_range', 'all')
        location_lat = float(request.args.get('lat', '40.7128'))
        location_lng = float(request.args.get('lng', '-74.0060'))
        radius_km = float(request.args.get('radius', 5))
        vehicle_type = request.args.get('vehicle_type', 'all')
        
        # Build base query
        query = """
        SELECT d.driver_id, d.name, d.vehicle_type, d.license_plate, d.rating, d.total_trips,
               dl.latitude, dl.longitude, dl.last_update,
               CASE 
                   WHEN dl.is_available = 1 THEN 'available'
                   ELSE 'unavailable'
               END as status,
               dl.eta_minutes
        FROM drivers d
        JOIN driver_locations dl ON d.driver_id = dl.driver_id
        WHERE dl.last_update >= datetime('now', '-30 minutes')
        """
        
        params = []
        
        # Add vehicle type filter
        if vehicle_type != 'all':
            query += " AND d.vehicle_type = ?"
            params.append(vehicle_type)
        
        query += " ORDER BY dl.last_update DESC"
        
        # Execute query
        drivers_data = db.execute_query(query, params)
        
        # Process results and calculate distances
        drivers = []
        for driver in drivers_data:
            distance = data_processor.calculate_distance(
                location_lat, location_lng,
                driver['latitude'], driver['longitude']
            )
            
            # Only include drivers within the search radius
            if distance <= radius_km:
                drivers.append({
                    'id': driver['driver_id'],
                    'name': driver['name'],
                    'vehicle_type': driver['vehicle_type'],
                    'vehicle_name': get_vehicle_name(driver['vehicle_type']),
                    'license_plate': driver['license_plate'],
                    'rating': driver['rating'],
                    'total_trips': driver['total_trips'],
                    'latitude': driver['latitude'],
                    'longitude': driver['longitude'],
                    'last_update': driver['last_update'],
                    'status': driver['status'],
                    'eta_minutes': driver['eta_minutes'],
                    'distance_km': round(distance, 2)
                })
        
        return jsonify({
            'success': True,
            'drivers': drivers,
            'count': len(drivers),
            'search_location': {
                'lat': location_lat,
                'lng': location_lng,
                'radius_km': radius_km
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    try:
        # Get total drivers
        total_result = db.execute_query("SELECT COUNT(*) as count FROM drivers")
        total_drivers = total_result[0][0] if total_result else 0
        
        # Get available drivers
        available_result = db.execute_query("""
            SELECT COUNT(DISTINCT driver_id) as count 
            FROM driver_locations 
            WHERE is_available = 1 AND last_update >= datetime('now', '-30 minutes')
        """)
        available_drivers = available_result[0][0] if available_result else 0
        
        # Get average ETA
        avg_eta_result = db.execute_query("""
            SELECT AVG(eta_minutes) as avg_eta 
            FROM driver_locations 
            WHERE last_update >= datetime('now', '-30 minutes')
        """)
        avg_eta = round(avg_eta_result[0][0] or 6.5, 1) if avg_eta_result else 6.5
        
        # Calculate coverage percentage
        coverage = round((available_drivers / total_drivers * 100) if total_drivers > 0 else 0, 1)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_drivers': total_drivers,
                'available_drivers': available_drivers,
                'avg_eta_minutes': avg_eta,
                'coverage_percentage': coverage
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/process', methods=['POST'])
def process_data():
    try:
        csv_path = 'train.csv'
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': f'NYC taxi dataset not found: {csv_path}. Please ensure train.csv is in the backend directory.'
            }), 400
        
        print("Starting NYC taxi data processing...")
        result = data_processor.process_nyc_data(csv_path)
        
        if result['success']:
            print(f"Successfully processed {result['processed_records']} records into {result['drivers_created']} drivers")
        else:
            print(f"Data processing failed: {result['error']}")
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/status', methods=['GET'])
def get_data_status():
    try:
        # Check if we have any data
        driver_count = db.execute_query("SELECT COUNT(*) as count FROM drivers")[0][0]
        location_count = db.execute_query("SELECT COUNT(*) as count FROM driver_locations")[0][0]
        
        return jsonify({
            'success': True,
            'data_status': {
                'drivers_in_database': driver_count,
                'locations_in_database': location_count,
                'has_data': driver_count > 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_vehicle_name(vehicle_type):
    names = {
        'standard': 'Standard Taxi',
        'premium': 'Premium Sedan',
        'suv': 'SUV',
        'accessible': 'Accessible Vehicle'
    }
    return names.get(vehicle_type, vehicle_type)

if __name__ == '__main__':
    print("🚕 NYC Taxi Driver Availability API Starting...")
    print("📍 Endpoints:")
    print("   GET  /api/drivers/availability - Find available drivers")
    print("   GET  /api/stats/summary - Get dashboard statistics") 
    print("   POST /api/data/process - Process real NYC taxi data")
    print("   GET  /api/data/status - Check data status")
    print("\n💡 First, run: POST /api/data/process to load your NYC taxi data")
    app.run(debug=True, host='0.0.0.0', port=5000)