from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/login', methods=['POST'])
def login():
    # Get username and password from form data
    username = request.form.get('username')
    password = request.form.get('password')

    # Print credentials to console
    print("=" * 50)
    print("Login attempt received:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("=" * 50)

    # Return a response
    return jsonify({
        'status': 'success',
        'message': 'Credentials received and printed to console'
    }), 200


@app.route('/')
def home():
    return render_template('submit.html')


if __name__ == '__main__':
    addr = '192.168.0.195:5000'
    print(f"Starting server on http://{addr}")
    print(f"Login endpoint: http://{addr}/login")
    app.run(host=addr[:addr.index(":")], port=int(addr[addr.index(":")+1:]), debug=True)