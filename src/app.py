import os
from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float, text
from geopy.distance import geodesic
from datetime import datetime, timedelta
from statistics import mean
import pymssql
import random
import string

# Set up Matplotlib
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQLAlchemy connection string
connection_string = (
    "mssql+pymssql://manub:your_password@manub.database.windows.net:1433/quiz5"
)

# Create SQLAlchemy engine
engine = create_engine(connection_string)

def setup_matplotlib():
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

setup_matplotlib()

def execute_query(query, params=None):
    connection = pymssql.connect(
        server='manub.database.windows.net',
        user='manub',
        password='your_password',
        database='quiz5'
    )
    cursor = connection.cursor(as_dict=True)
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query_data():
    if request.method == 'POST':
        try:
            start_time = datetime.now()
            
            min_mag = request.form.get('min_mag')
            max_mag = request.form.get('max_mag')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            lat = request.form.get('latitude')
            lon = request.form.get('longitude')
            place = request.form.get('place')
            distance = request.form.get('distance')
            night_time = request.form.get('night_time')

            query = '''
                SELECT [time] AS Datetime, [latitude] AS Latitude, [longitude] AS Longitude, [mag] AS Magnitude, [place] AS Place, [distance] AS Distance, [place_name] AS Place_Name
                FROM [dbo].[earthquakes]
                WHERE 1=1
            '''
            params = []

            if min_mag and max_mag:
                query += ' AND [mag] BETWEEN %s AND %s'
                params.extend([float(min_mag), float(max_mag)])

            if start_date and end_date:
                if start_date <= end_date:
                    query += ' AND [time] BETWEEN %s AND %s'
                    params.extend([start_date, end_date])
                else:
                    return 'Error: Start date must be before end date.', 400

            if lat and lon and distance:
                try:
                    distance = float(distance)
                except ValueError:
                    return 'Error: Distance must be a number.', 400

                earthquakes = execute_query(query, params)
                nearby_earthquakes = [
                    {
                        'Datetime': quake['Datetime'],
                        'Latitude': float(quake['Latitude']),
                        'Longitude': float(quake['Longitude']),
                        'Magnitude': float(quake['Magnitude']),
                        'Place': quake['Place'],
                        'Distance': float(quake['Distance']),
                        'Place_Name': quake['Place_Name']
                    }
                    for quake in earthquakes
                    if geodesic((float(lat), float(lon)), (float(quake['Latitude']), float(quake['Longitude']))).km <= distance
                ]
                end_time = datetime.now()
                elapsed_time = (end_time - start_time).total_seconds()
                return render_template('results.html', earthquakes=nearby_earthquakes, map_path=None, query_time=elapsed_time)

            if place:
                query += ' AND [place_name] LIKE %s'
                params.append(f'%{place}%')

            if distance:
                query += ' AND [distance] <= %s'
                params.append(float(distance))

            if night_time:
                query += " AND [mag] > 4.0 AND (DATEPART(HOUR, [time]) >= 18 OR DATEPART(HOUR, [time]) <= 6)"

            query_key = f"{min_mag}_{max_mag}_{start_date}_{end_date}_{lat}_{lon}_{place}_{distance}_{night_time}"
            try:
                earthquakes = execute_query(query, params)
                end_time = datetime.now()
                elapsed_time = (end_time - start_time).total_seconds()
                return render_template('results.html', earthquakes=earthquakes, map_path=None, cached=False, query_time=elapsed_time)
            except Exception as e:
                return str(e), 400

        except Exception as e:
            return str(e), 400

    return render_template('query.html')

@app.route('/visualize', methods=['GET', 'POST'])
def visualize_data():
    if request.method == 'POST':
        data = request.json
        chart_type = data.get('type')
        N = int(data.get('N', 10))

        # Query to get top N food items
        query = f"SELECT TOP {N} * FROM food ORDER BY price DESC"
        food_items = execute_query(query)

        if chart_type == 'pie':
            create_pie_chart(food_items)
        elif chart_type == 'bar':
            create_bar_chart(food_items)
        elif chart_type == 'scatter':
            create_scatter_plot(food_items)
        
        return jsonify({"status": "success"})
    
    return render_template('visualize.html')

def create_pie_chart(data):
    import matplotlib.pyplot as plt
    labels = [item['name'] for item in data]
    sizes = [item['price'] for item in data]
    
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    plt.savefig('static/pie_chart.png')

def create_bar_chart(data):
    import matplotlib.pyplot as plt
    labels = [item['name'] for item in data]
    sizes = [item['price'] for item in data]
    
    plt.figure(figsize=(10, 5))
    plt.bar(labels, sizes)
    plt.xlabel('Food Items')
    plt.ylabel('Price')
    plt.title('Top Food Items by Price')
    plt.xticks(rotation=45)
    plt.savefig('static/bar_chart.png')

def create_scatter_plot(data):
    import matplotlib.pyplot as plt
    prices = [item['price'] for item in data]
    quantities = [item['quantity'] for item in data]
    
    plt.figure(figsize=(10, 5))
    plt.scatter(prices, quantities)
    plt.xlabel('Price')
    plt.ylabel('Quantity')
    plt.title('Price vs Quantity of Food Items')
    plt.savefig('static/scatter_plot.png')

if __name__ == '__main__':
    app.run(debug=True)
