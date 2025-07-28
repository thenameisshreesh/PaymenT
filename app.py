import os
from flask import Flask, render_template, request, redirect
import requests
import uuid
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'shreeshpitambare084@gmail.com'
app.config['MAIL_PASSWORD'] = 'untk duvx aisq ssuq'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# 🔴 In-memory storage for temporary user data
order_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pay', methods=['POST'])
def pay():
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    amount = request.form['amount']

    order_id = 'Order' + str(uuid.uuid4())
    transaction_id = str(uuid.uuid4())

    headers = {
        "accept": "application/json",
        "x-api-version": "2022-09-01",
        "content-type": "application/json",
        "x-client-id": "896457b3bd65c4bc202da34a48754698",
        "x-client-secret": "cfsk_ma_prod_58a4944f0018534a39d68c2e96a5337e_ca091af8"
    }

    # Include all info in return_url as query parameters
    return_url = (
        f"https://payment-production-a756.up.railway.app/payment_status"
        f"?order_id={order_id}&name={name}&email={email}&mobile={mobile}&txnid={transaction_id}"
    )

    data = {
        "order_id": order_id,
        "order_amount": amount,
        "order_currency": "INR",
        "customer_details": {
            "customer_id": mobile,
            "customer_name": name,
            "customer_email": email,
            "customer_phone": mobile
        },
        "order_meta": {
            "return_url": return_url
        }
    }

    response = requests.post("https://sandbox.cashfree.com/pg/orders", json=data, headers=headers)

    if response.status_code == 200:
        res_data = response.json()
        return redirect(res_data['payment_link'])
    else:
        return f"Error: {response.text}"

@app.route('/payment_status')
def payment_status():
    name = request.args.get('name')
    email = request.args.get('email')
    mobile = request.args.get('mobile')
    transaction_id = request.args.get('txnid')

    if not all([name, email, mobile, transaction_id]):
        return "Missing payment details. Cannot confirm."

    try:
        msg = Message('Payment Confirmation', sender='shreeshpitambare084@gmail.com', recipients=[email])
        msg.body = f'Thank you {name} for your payment.\n\nTransaction ID: {transaction_id}\nMobile: {mobile}'
        mail.send(msg)
        return render_template('success.html', name=name)
    except Exception as e:
        return f"Error sending mail: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
