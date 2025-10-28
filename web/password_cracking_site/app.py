from datetime import datetime

from flask import Flask, render_template, request

app = Flask(__name__)
passwords = set()

@app.route('/')
def home():
    return render_template('home.html', curr_time=datetime.now())

@app.route('/submit')
def submit_passwords():
    return render_template('submit.html')

@app.route('/post_passwords', methods=['POST'])
def post_passwords():
    # Grab the items from the form
    for key, val in request.form.items():
        passwords.add(val)
    print(f"Passwords updated. Current set has {len(passwords)} passwords.")
    return render_template("success.html")

@app.route('/curr_count', methods=['GET'])
def curr_count():
    # Return the current number of passwords to the requester
    return {
        "curr_count": len(passwords)
    }

@app.route('/gather', methods=['GET'])
def gather():
    # Gather up all passwords, clear queue, and return them
    data = {"passwords": list(passwords)}
    passwords.clear()
    return data

if __name__ == '__main__':
    app.run()
