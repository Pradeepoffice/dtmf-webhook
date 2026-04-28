from flask import Flask, request, Response

app = Flask(__name__)

# Health check
@app.route('/', methods=['GET'])
def home():
    return "Webhook is running"

# DTMF receiver endpoint
@app.route('/receive-digits', methods=['POST'])
def receive_digits():
    try:
        # Get incoming data from Exotel
        data = request.form.to_dict()
        print("Incoming Payload:", data)

        # Extract digits
        digits = data.get("Digits") or data.get("digits") or "No input"

        print("Digits Received:", digits)

        # Simple IVR logic
        if digits == "1":
            message = "You selected Sales"
        elif digits == "2":
            message = "You selected Support"
        elif digits == "3":
            message = "You selected Billing"
        else:
            message = f"You pressed {digits}"

        # XML response (important for Exotel)
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
            <Say>Something went wrong</Say>
        </Response>
        """, mimetype='text/xml')


# Run locally (Render will ignore this and use gunicorn)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
