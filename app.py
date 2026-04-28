from flask import Flask, request, Response
import sqlite3
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Initialize Database
# -----------------------------
def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        call_sid TEXT,
        from_number TEXT,
        to_number TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Health Check
# -----------------------------
@app.route('/', methods=['GET'])
def home():
    return "Webhook is running"

# -----------------------------
# Main Endpoint (GET + POST)
# -----------------------------
@app.route('/receive-digits', methods=['GET', 'POST'])
def receive_digits():
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.form.to_dict()
        else:
            data = request.args.to_dict()

        print("Incoming Payload:", data)

        # Extract values
        digits = data.get("Digits") or data.get("digits")
        call_sid = data.get("CallSid")
        from_number = data.get("From") or data.get("CallFrom")
        to_number = data.get("To") or data.get("CallTo")

        # Clean digits (remove quotes if any)
        if digits:
            digits = digits.replace('"', '').strip()

        print("Order ID:", digits)
        print("CallSid:", call_sid)

        # -----------------------------
        # Save to Database
        # -----------------------------
        if digits:
            conn = sqlite3.connect("orders.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO orders (order_id, call_sid, from_number, to_number, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                digits,
                call_sid,
                from_number,
                to_number,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

        # -----------------------------
        # Response to Exotel
        # -----------------------------
        if digits:
            message = f"Your order ID {digits} has been received"
        else:
            message = "No input received"

        response_xml = f"""
        <Response>
            <Say>{message}</Say>
        </Response>
        """

        return Response(response_xml, mimetype='text/xml')

    except Exception as e:
        print("Error:", str(e))

        return Response("""
        <Response>
            <Say>There was an error processing your request</Say>
        </Response>
        """, mimetype='text/xml')


# -----------------------------
# View Stored Orders (Debug API)
# -----------------------------
@app.route('/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()

    conn.close()

    return {"orders": rows}


# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
