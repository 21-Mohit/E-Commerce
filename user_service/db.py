from pymongo import MongoClient
import datetime
from user import User


# Connect to MongoDB
client = MongoClient("mongodb+srv://palmohit897:1234567890@cluster0.tbarxzw.mongodb.net/")
db = client["ecommerce"]
users_collection = db["users"]

def save_user(username, password):
    #password_hash = bcrypt.hashpw(password, bcrypt.gensalt()) 
    #password_hash = generate_password_hash(password)
    if users_collection.find_one({'_id': username}):  
        print("User already exists. You might want to update instead.")  
    else:  
        users_collection.insert_one({'_id': username,'password': password})
        
        
def get_user(username):
    user_data = users_collection.find_one({'_id':username})
    return User(user_data['_id'],user_data['password']) if user_data else None