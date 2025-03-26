from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Store the latest received data
sensor_data_store = {}

# Endpoint to get the latest received data
@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(sensor_data_store)

# Endpoint to receive data from Raspberry Pi 2 (Arduino data)
@app.route('/data', methods=['POST'])
def receive_data():
    global sensor_data_store
    sensor_data_store = request.json  # Update with the latest received data
    print(f"Received Data: {sensor_data_store}")
    return jsonify({"status": "success"}), 200

# Main UI route
@app.route('/')
def index():
    return render_template('index.html', data=sensor_data_store)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
