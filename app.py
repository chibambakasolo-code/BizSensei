from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

@app.route('/')
def home():
    return render_template('setup.html')  # Your HTML form lives here

@app.route('/setup', methods=['POST'])
def setup_business():
    business_name = request.form.get("business_name")
    business_type = request.form.get("business_type")

    # You can process/store the data here

    flash(f"Business '{business_name}' of type '{business_type}' was successfully set up!")
    return redirect(url_for('home'))  # Redirect back to the form page

if __name__ == '__main__':
    app.run(debug=True)
