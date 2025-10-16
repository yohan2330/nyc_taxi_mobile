NYC Taxi Trip Data Explorer Documentation Report
1. Problem Framing and Dataset Analysis
The New York City Taxi Trip dataset contains detailed trip-level data from taxi services, including pickup and drop-off times, coordinates, trip distance, fare, and payment details. This project aimed to build a full-stack data exploration dashboard that helps visualize and analyze urban mobility patterns in New York City.
Data Challenges Identified:
Missing or zero coordinates for pickup/dropoff locations


Inconsistent timestamps and duplicate records


Extreme outliers in trip duration and fare (e.g., 0 or unrealistic values)


Incorrect passenger counts (e.g., >6 passengers)

Data Cleaning and Processing Steps:
Removed duplicates and rows with missing essential fields


Normalized timestamps to a standard ISO format


Filtered trips with unrealistic distance (>100 km) or duration (>3 hours)


Derived three new features:


Average Speed (km/h) = distance / (duration / 60)


Fare per Km = fare_amount / distance


Trip Hour = hour extracted from pickup time (for time-based trends)


Unexpected Observation:
 During exploration, we found that trips around 8 AM and 6 PM had significantly lower average speeds despite shorter distances, indicating peak-hour congestion. This observation guided our dashboard’s focus on temporal patterns.
   
2. System Architecture and Design Decisions
System Overview
The system is a three-tier architecture:
Frontend:
HTML, CSS, JavaScript (Vanilla)


Interactive dashboard with charts and filters


Fetches data dynamically from the backend API


Backend (Flask):
RESTful API exposing endpoints for trip filtering, statistics, and aggregation


Data cleaning and feature engineering scripts in Python


Database (PostgreSQL):
Normalized schema with tables for trips, passengers, and fares


Indexed on pickup/dropoff datetime and location for query efficiency


3. Architecture Diagram:


Design Justification:
Flask chosen for simplicity and Python integration with pandas for preprocessing.


PostgreSQL for strong relational support and indexing.


Vanilla JS frontend for lightweight interactivity without framework overhead.


Trade-offs:
Flask is simple but less scalable than Node.js.


PostgreSQL requires more setup than SQLite but supports better performance for larger datasets.


4. Insights and Interpretation




5. Reflection and Future Work
Challenges Faced:
Handling huge CSV files during preprocessing (memory management).


Designing an efficient schema that balances normalization and query speed.


Creating intuitive, meaningful visualizations from raw numeric data.


Future Improvements:
Integrate map-based visualization using Leaflet or Mapbox.


Deploy the application with Docker and load balancing for scalability.


Automate data ingestion for real-time updates.


Add predictive models for fare estimation or traffic congestion alerts.
