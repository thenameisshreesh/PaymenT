from flask import Flask, render_template, request, redirect, session
from flask_session import Session  # add this
import os
import requests
import uuid
import qrcode
from io import BytesIO
import base64
from flask_mail import Mail, Message


name=""
email=""
mobile=""
profession=""
gender=""
address=""
transaction_id=""

order_id=""
headers = {}

app = Flask(__name__)



# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'shreeshpitambare084@gmail.com'
app.config['MAIL_PASSWORD'] = 'untk duvx aisq ssuq'
app.config['MAIL_DEFAULT_SENDER'] = 'shreeshpitambare084@gmail.com'
mail = Mail(app)







# Home Page (Payment Form)
@app.route('/')
def index():
    return render_template('index.html')

# Pay Route (Handles Form Submission)
@app.route('/pay', methods=['POST'])
def pay():
    
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    transaction_id = str(uuid.uuid4())
    amount=1

    
    # Unique Order ID
    order_id = "Order" + str(uuid.uuid4())

    

    headers = {
    "x-client-id": "896457b3bd65c4bc202da34a48754698",
    "x-client-secret": "cfsk_ma_prod_58a4944f0018534a39d68c2e96a5337e_ca091af8",
    "x-api-version": "2022-01-01",  # or latest version per Cashfree docs
    "Content-Type": "application/json"
    }


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
            "return_url": f"https://payment-production-a756.up.railway.app/payment_status?order_id={order_id}"

        }
    }

    res = requests.post("https://api.cashfree.com/pg/orders", json=data, headers=headers)
    res_data = res.json()

    if 'payment_link' in res_data:
        return redirect(res_data['payment_link'])
    else:
        return f"Error: {res_data}"
    
    



# Dummy Payment Status Route
@app.route('/payment_status')
def payment_status():
   

    ois = request.args.get('order_id')

    hs = {
        "x-client-id": "896457b3bd65c4bc202da34a48754698",
        "x-client-secret": "cfsk_ma_prod_58a4944f0018534a39d68c2e96a5337e_ca091af8",
        "x-api-version": "2022-01-01",
    }


    resf = requests.get(f"https://api.cashfree.com/pg/orders/{ois}", headers=hs)
    order_info = resf.json()

    if order_info['order_status'] == 'PAID':
        qr_data = f"{name}|{email}|{mobile}"
        qr_img = qrcode.make(qr_data)
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_code_b64 = base64.b64encode(buffered.getvalue()).decode()

                # Send Email to Customer
        msg = Message('Payment Confirmation - Your QR Code', recipients=[email])
            
        msg.body = f"""Dear {name},
            Thank you for registering for our event.
            Transaction ID: {transaction_id}
            Please find your unique QR code below. Show this at the entry gate.
            Regards,
            Event Team VEERA's NAIIL 💅
            """
        msg.attach("qr.png", "image/png", buffered.getvalue())
        try:
           mail.send(msg)
        except Exception as e:
            return f"Error sending mail: {e}", 500

            # Send Email to Admin
        admin_msg = Message('New Customer Registered', recipients=['shreeshpitambare777@gmail.com'])
        admin_msg.body = f"""New Customer Registered....!!!!

            Name: {name}
            Email: {email}
            Transaction ID: {transaction_id}
            """
        try:
            mail.send(admin_msg)
        except Exception as e:
            return f"Error sending admin mail: {e}", 500


        
        return render_template("success.html")
    else:
        return "Payment failed or not completed. Please try again.",400



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # fallback to 5000 for local
    app.run(host="0.0.0.0", port=port)

