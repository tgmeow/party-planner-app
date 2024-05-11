from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import traceback

app = Flask(__name__)
CORS(app)

# Function to create SQLite connection
def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to fetch all events
@app.route('/events', methods=['GET'])
def get_events():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM events')
        rows = cur.fetchall()
        events = [{'id': row['id'], 'eventName': row['name'], 'eventDate': row['date'], 'eventTime': row['time'], 'eventLocation': row['location'], 'eventDescription': row['description']} for row in rows]
        return jsonify(events)
    except Exception as e:
        app.logger.error("Error fetching events: %s", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        conn.close()
# Route to create a new event
@app.route('/events', methods=['POST'])
def create_event():
    conn = None
    try:
        data = request.json
        name = data.get('eventName')
        date = data.get('eventDate')
        time = data.get('eventTime')
        location = data.get('eventLocation')
        description = data.get('eventDescription')

        if not all([name, date, time, location, description]):
            return jsonify({'error': 'Please provide all event details'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO events (name, date, time, location, description) 
                       VALUES (?, ?, ?, ?, ?)''', (name, date, time, location, description))
        conn.commit()

        return jsonify({'id': cur.lastrowid}), 201
    except Exception as e:
        app.logger.error("Error creating event: %s", str(e))
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
