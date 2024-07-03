import os
from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
DB_SERVER = 'manub.database.windows.net'
DB_NAME = 'quiz5'
DB_USER = 'manub'
DB_PASSWORD = 'your_password'
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
    return render_template('index.html')

@app.route('/food', methods=['GET', 'POST'])
def food():
    if request.method == 'POST':
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
        return jsonify(success=True)
    else:
        select = food_table.select()
        result = engine.execute(select)
        foods = [dict(row) for row in result]
        return jsonify(foods)

@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    if request.method == 'POST':
        data = request.get_json()
        viz_type = data.get('type')
        N = data.get('N')
        if viz_type == 'pie':
            query = f'SELECT name, quantity FROM food ORDER BY quantity DESC LIMIT {N}'
            result = engine.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=['name', 'quantity'])
            plt.figure(figsize=(10, 6))
            plt.pie(df['quantity'], labels=df['name'], autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.savefig('static/pie_chart.png')
            plt.close()
        elif viz_type == 'bar':
            query = f'SELECT name, price FROM food ORDER BY price DESC LIMIT {N}'
            result = engine.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=['name', 'price'])
            plt.figure(figsize=(10, 6))
            plt.barh(df['name'], df['price'], color='blue')
            plt.xlabel('Price')
            plt.ylabel('Food')
            plt.savefig('static/bar_chart.png')
            plt.close()
        elif viz_type == 'scatter':
            query = 'SELECT * FROM food'
            result = engine.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=['id', 'name', 'price', 'quantity'])
            plt.figure(figsize=(10, 6))
            colors = df['quantity'].apply(lambda x: 'red' if x < 100 else 'blue' if x <= 1000 else 'green')
            plt.scatter(df.index, df['price'], c=colors)
            plt.xlabel('Index')
            plt.ylabel('Price')
            plt.savefig('static/scatter_plot.png')
            plt.close()
        return jsonify(success=True)
    return render_template('visualize.html')

if __name__ == '__main__':
    app.run(debug=True)
