import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/dashboard')
def dashboard():
    business_name = session.get('business_name', 'Unknown')
    business_type = session.get('business_type', 'Unknown')
    return render_template('dashboard.html', business_name=business_name, business_type=business_type
    
@app.route('/')
def index():
    return render_template('setup.html')  # Main form page

@app.route('/setup', methods=['POST'])
def setup():
    business_name = request.form.get("business_name")
    business_type = request.form.get("business_type")

    session['business_name'] = business_name
    session['business_type'] = business_type

    flash(f"Business '{business_name}' of type '{business_type}' added!", "success")
    return redirect(url_for("dashboard")
    

    if not business_name or not business_type:
        flash("Please fill in all fields.", "danger")
        return redirect(url_for("index"))

    # You can save this data here (e.g., to database)
    flash(f"Business '{business_name}' of type '{business_type}' added!", "success")
    return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
