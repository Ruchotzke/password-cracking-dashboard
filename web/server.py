from flask import Flask, request, jsonify
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
    return """
    <html>
        <body>
            <h1>Login Server Running</h1>
            <p>POST credentials to /login</p>
        </body>
    </html>
    """


if __name__ == '__main__':
    addr = '172.16.42.192:80'
    print(f"Starting server on http://{addr}")
    print(f"Login endpoint: http://{addr}/login")
    app.run(host=addr[:addr.index(":")], port=int(addr[addr.index(":")+1:]), debug=True)