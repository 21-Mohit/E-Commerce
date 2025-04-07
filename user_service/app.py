from flask import Flask, jsonify, request, redirect, url_for,make_response
from flask_jwt_extended import JWTManager, create_access_token,jwt_required,get_jwt_identity,get_jwt,set_access_cookies
from db import save_user, get_user
from flask import render_template
from flask_cors import CORS 
import requests

app = Flask(__name__)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"

app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Change in production
jwt = JWTManager(app)

# Connect to MongoDB
CORS(app, supports_credentials=True)  # ✅ Allow cross-origin cookies
# User Registration
@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        save_user(username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            access_token = access_token.decode("utf-8") if isinstance(access_token, bytes) else access_token
            response = make_response(redirect("http://127.0.0.1:8080/"))
            set_access_cookies(response, access_token)
            return response
        #    response = redirect("http://127.0.0.1:8080/") # Redirect to orders page
        #     response.set_cookie("access_token_cookie", access_token, httponly=True, samesite=None,secure=False)  # Store JWT in a cookie
        #     return response
        else:
            message = "Failed to login"

    return render_template('login.html', message=message)

# Home Route
@app.route('/')
def home():
    return render_template("index.html")

# Orders Redirect (Frontend should call this)
@app.route('/orders')
@jwt_required()
def orders():
    current_user = get_jwt_identity()
    jwt_token = get_jwt()    #Get the current JWT payload
    access_token = request.cookies.get("access_token_cookie")  # or Generate one manually
    if isinstance(access_token, bytes):
        access_token = access_token.decode("utf-8")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
        # Call order_service
    order_service_url = "http://127.0.0.1:8080"
    payload = {
        "user_id": current_user,
    
    }
    
    response = requests.post(order_service_url, json=payload, headers=headers)
    print("🔍 Order service response status:", response.status_code)
    print("📄 Order service response text:", response.text)
    
    return ({"message": "Order service called", "order_response": response.status_code()})
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)
