from flask import Flask, request, Response
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


@app.route('/', methods=['GET'])
def home():
    return "Webhook is running"


@app.route('/receive-digits', methods=['POST'])
def receive_digits():
    try:
        data = request.form.to_dict()
        print("Payload:", data)

        # Capture full digits (Order ID)
        order_id = data.get("Digits") or data.get("digits")

        print("Order ID:", order_id)

        # Save to DB
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO orders (order_id, timestamp) VALUES (?, ?)",
            (order_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        # Response
        response_xml = f"""
        <Response>
            <Say>Your order ID {order_id} has been received</Say>
        </Response>
        """

        return Response(response_xml, mimetype='text/xml')

    except Exception as e:
        print("Error:", str(e))

        return Response("""
        <Response>
            <Say>Error processing your request</Say>
        </Response>
        """, mimetype='text/xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
