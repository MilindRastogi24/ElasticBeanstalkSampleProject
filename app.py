from flask import Flask, jsonify, render_template
import psycopg2

import boto3
from botocore.exceptions import ClientError

def get_secret():

    secret_name = "rds_secret"
    region_name = "ap-south-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    print(secret)

    # Your code goes here.
get_secret()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host="database-1.crau20ig249e.ap-south-1.rds.amazonaws.com",
        database="postgres",
        user="postgres",
        password="password",
        port='5432'
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_table')
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_table (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) ,
            email VARCHAR(120) 
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    return 'Table created successfully.'

@app.route('/insert_user')
def insert_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users_table (username, email)
        VALUES (%s, %s);
    ''', ('testuser', 'testuser@example.com'))
    conn.commit()
    cursor.close()
    conn.close()
    return 'User inserted successfully.'

@app.route('/fetch_users')
def fetch_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email FROM users_table;')
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'username': user[1],
            'email': user[2]
        })

    return jsonify(users_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0')