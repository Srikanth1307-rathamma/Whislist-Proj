import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allow cross-origin requests from our frontend

DB_HOST = os.environ.get('DATABASE_HOST')
DB_NAME = os.environ.get('POSTGRES_DB')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/wishlist', methods=['GET'])
def get_wishlist():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS wishlist (id SERIAL PRIMARY KEY, item_name VARCHAR(100));')
        cur.execute('SELECT item_name FROM wishlist;')
        items = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"wishlist": [item[0] for item in items]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/wishlist', methods=['POST'])
def add_item():
    data = request.get_json()
    if not data or 'item' not in data:
        return jsonify({"error": "Invalid payload"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO wishlist (item_name) VALUES (%s);', (data['item'],))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
