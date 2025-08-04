import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/')
def index():
    return render_template('setup.html')  # Ensure this file exists in /templates

@app.route('/setup', methods=['POST'])
def setup():
    business_name = request.form.get("business_name")
    business_type = request.form.get("business_type")

    print(f"Received {business_name} - {business_type}")  # Debug log

    flash(f"Business '{business_name}' of type '{business_type}' added!", "success")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
