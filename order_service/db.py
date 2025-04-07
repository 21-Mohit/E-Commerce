from pymongo import MongoClient

client = MongoClient("mongodb+srv://palmohit897:1234567890@cluster0.tbarxzw.mongodb.net/")
db = client['ecommerce']
orders_collection = db['orders']

def insert_order(order_data):
    """Insert an order into MongoDB"""
    order_data["_id"] = order_data["order_id"]
    result = orders_collection.insert_one(order_data)
    return result.inserted_id

def get_order(order_id):
    """Retrieve an order by ID"""
    return orders_collection.find_one({"_id": order_id})

def update_order_status(order_id, status):
    """Update the status of an order"""
    orders_collection.update_one({"_id": order_id}, {"$set": {"status": status}})

def get_all_orders():
    """Retrieve all orders"""
    cursor = orders_collection.find({})
    return cursor.to_list(length=100)