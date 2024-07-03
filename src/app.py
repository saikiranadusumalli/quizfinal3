import os
from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
DB_SERVER = 'manub.database.windows.net'
DB_NAME = 'quiz5'
DB_USER = 'manub'
DB_PASSWORD = 'Arjunsuha1*'
DB_DRIVER = 'ODBC Driver 17 for SQL Server'
DATABASE_URI = f'mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'

engine = create_engine(DATABASE_URI)

metadata = MetaData()

# Define the food table
food_table = Table('food', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('name', String, nullable=False),
                   Column('price', Float, nullable=False),
                   Column('quantity', Integer, nullable=False))

metadata.create_all(engine)

@app.route('/')
def index():
    select = food_table.select()
    result = engine.execute(select)
    foods = [dict(row) for row in result]
    return render_template('index.html', foods=foods)

@app.route('/query')
def query():
    return render_template('query.html')

@app.route('/food', methods=['POST'])
def food():
    data = request.get_json()
    command = data.get('command')
    if command == 'add':
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')
        ins = food_table.insert().values(name=name, price=price, quantity=quantity)
        engine.execute(ins)
    elif command == 'delete':
        id = data.get('id')
        delete = food_table.delete().where(food_table.c.id == id)
        engine.execute(delete)
    elif command == 'modify':
        id = data.get('id')
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')
        update = food_table.update().where(food_table.c.id == id).values(name=name, price=price, quantity=quantity)
        engine.execute(update)

    select = food_table.select()
    result = engine.execute(select)
    foods = [dict(row) for row in result]
    return render_template('results.html', foods=foods)

@app.route('/visualize', methods=['POST'])
def visualize():
    data = request.get_json()
    viz_type = data.get('type')
    N = int(data.get('N'))

    if viz_type == 'pie':
        query = f'SELECT name, quantity FROM food ORDER BY quantity DESC LIMIT {N}'
        result = engine.execute(query)
        chart_data = [dict(row) for row in result]
        return jsonify(success=True, type='pie', chartData=chart_data)

    elif viz_type == 'bar':
        query = f'SELECT name, price FROM food ORDER BY price DESC LIMIT {N}'
        result = engine.execute(query)
        chart_data = [dict(row) for row in result]
        return jsonify(success=True, type='bar', chartData=chart_data)

    elif viz_type == 'scatter':
        query = 'SELECT id, name, price, quantity FROM food'
        result = engine.execute(query)
        chart_data = [dict(row) for row in result]
        chart_data = [{'index': i, **item} for i, item in enumerate(chart_data)]
        return jsonify(success=True, type='scatter', chartData=chart_data)

    return jsonify(success=False)

if __name__ == '__main__':
    app.run(debug=True)
