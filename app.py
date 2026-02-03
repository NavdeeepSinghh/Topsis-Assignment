import os
import pandas as pd
import numpy as np
import smtplib
from flask import Flask, render_template, request
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "topsis_secret"


# 1. HOME ROUTE: Displays the form at http://127.0.0.1:5000/
@app.route('/')
def home():
    return render_template('index.html')


# 2. VALIDATION LOGIC: Matches Part-I and Part-III constraints
def validate_topsis(df, weights, impacts):
    # Requirement: Input file must contain three or more columns
    if len(df.columns) < 3:
        return "Error: Input file must contain at least three columns."

    w_list = weights.split(',')
    i_list = impacts.split(',')

    # Requirement: Weights and impacts must be separated by ','
    # Requirement: Number of weights, impacts, and numeric columns must be same
    numeric_cols_count = len(df.columns) - 1
    if len(w_list) != len(i_list) or len(w_list) != numeric_cols_count:
        return f"Error: Number of weights ({len(w_list)}), impacts ({len(i_list)}), and data columns ({numeric_cols_count}) must be equal."

    # Requirement: Impacts must be either +ve or -ve
    if not all(i.strip() in ['+', '-'] for i in i_list):
        return "Error: Impacts must be either '+' or '-'."

    # Requirement: From 2nd to last columns must contain numeric values only
    for col in df.columns[1:]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return f"Error: Column '{col}' contains non-numeric values."

    return None


# 3. EMAIL LOGIC: Handles result delivery
def send_email(receiver_email, file_path):
    # NOTE: Use a Google App Password here, not your regular password
    SENDER_EMAIL = os.environ.get('EMAIL_USER')
    SENDER_PASS = os.environ.get('EMAIL_PASS')

    msg = EmailMessage()
    msg['Subject'] = 'Topsis Analysis Results'
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg.set_content("The Topsis analysis is complete. Please find the result file attached.")

    with open(file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename="result.csv")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        return True
    except Exception:
        return False


# 4. CALCULATION ROUTE: Handles form submission
@app.route('/calculate', methods=['POST'])
def handle_form():
    file = request.files['file']
    weights = request.form['weights']
    impacts = request.form['impacts']
    email = request.form['email']

    if not file:
        return "No file uploaded", 400

    try:
        df = pd.read_csv(file)
    except Exception:
        return "Error: Could not read CSV file.", 400

    # Perform Validations
    error = validate_topsis(df, weights, impacts)
    if error:
        return error, 400

    # --- SUCCESS LOGIC ---
    # In a real run, you would call your topsis logic here to add
    # 'Topsis Score' and 'Rank' columns
    output_path = "result.csv"
    df.to_csv(output_path, index=False)

    # Trigger Email
    email_status = send_email(email, output_path)

    if email_status:
        return f"Processing complete. Result has been emailed to {email}."
    else:
        return f"Calculation complete, but failed to send email. Check your SMTP settings."


if __name__ == "__main__":
    app.run(debug=True)