-- Useful Database Queries for NYC Taxi Driver Availability System

-- 1. Get all available drivers
SELECT d.driver_id, d.name, d.vehicle_type, d.rating,
       dl.latitude, dl.longitude, dl.eta_minutes
FROM drivers d
JOIN driver_locations dl ON d.driver_id = dl.driver_id
WHERE dl.is_available = 1
AND dl.last_update >= DATEADD(MINUTE, -30, GETDATE())
ORDER BY dl.last_update DESC;

-- 2. Get drivers within 5km of a location (example: Times Square)
SELECT d.driver_id, d.name, d.vehicle_type, d.rating,
       dl.latitude, dl.longitude, dl.eta_minutes,
       -- Distance calculation would go here in the application
       'distance_km' as distance
FROM drivers d
JOIN driver_locations dl ON d.driver_id = dl.driver_id
WHERE dl.is_available = 1
AND dl.latitude BETWEEN 40.70 AND 40.80  -- Approximate bounds
AND dl.longitude BETWEEN -74.02 AND -73.95
ORDER BY dl.last_update DESC;

-- 3. Get statistics for dashboard
SELECT 
    COUNT(DISTINCT d.driver_id) as total_drivers,
    COUNT(DISTINCT CASE WHEN dl.is_available = 1 THEN d.driver_id END) as available_drivers,
    AVG(dl.eta_minutes) as avg_eta,
    ROUND((COUNT(DISTINCT CASE WHEN dl.is_available = 1 THEN d.driver_id END) * 100.0 / COUNT(DISTINCT d.driver_id)), 1) as coverage_percentage
FROM drivers d
JOIN driver_locations dl ON d.driver_id = dl.driver_id
WHERE dl.last_update >= DATEADD(MINUTE, -30, GETDATE());

-- 4. Get driver distribution by vehicle type
SELECT 
    vehicle_type,
    COUNT(*) as driver_count,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM drivers)), 1) as percentage
FROM drivers
GROUP BY vehicle_type
ORDER BY driver_count DESC;

-- 5. Find drivers by specific vehicle type
SELECT d.driver_id, d.name, d.license_plate, d.rating,
       dl.latitude, dl.longitude, dl.eta_minutes
FROM drivers d
JOIN driver_locations dl ON d.driver_id = dl.driver_id
WHERE d.vehicle_type = 'premium'  -- Change to 'standard', 'suv', or 'accessible'
AND dl.is_available = 1
ORDER BY dl.last_update DESC;

-- 6. Get driver with most trips (most experienced)
SELECT driver_id, name, total_trips, rating
FROM drivers
ORDER BY total_trips DESC
OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY;

-- 7. Check data freshness
SELECT 
    COUNT(*) as total_locations,
    SUM(CASE WHEN dl.last_update >= DATEADD(MINUTE, -15, GETDATE()) THEN 1 ELSE 0 END) as recent_locations,
    MIN(dl.last_update) as oldest_update,
    MAX(dl.last_update) as latest_update
FROM driver_locations dl;
