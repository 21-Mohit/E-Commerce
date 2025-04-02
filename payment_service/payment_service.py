from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pymongo import MongoClient

app = FastAPI()

# Kafka Configuration
KAFKA_BROKER_URL = "localhost:9092"
ORDER_TOPIC = "order_topic"
PAYMENT_TOPIC = "payment_topic"

client = MongoClient("mongodb+srv://palmohit897:1234567890@cluster0.tbarxzw.mongodb.net/")
db = client['ecommerce']
payments = db['payments']


from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_id: str
    status:str

# Setup Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Serve static files (optional)
#app.mount("/static", StaticFiles(directory="static"), name="static")

producer = None
orders = {}  # Store orders temporarily for user interaction

@app.on_event("startup")
async def start_kafka():
    """Start Kafka Producer and Consumer"""
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()

    # Start the consumer as a background task
    asyncio.create_task(consume_orders())

@app.on_event("shutdown")
async def stop_kafka():
    """Stop Kafka Producer"""
    await producer.stop()

async def consume_orders():
    """Kafka Consumer: Listen for new orders"""
    consumer = AIOKafkaConsumer(
        ORDER_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    await consumer.start()

    try:
        async for message in consumer:
            order = message.value
            orders[order["order_id"]] = order  # Store order for later processing
            print(f"Received order: {order}")
    finally:
        await consumer.stop()

@app.get("/payment_page")
@app.get("/payment_page/")
async def payment_page(request: Request, order_id: str):
    """Serve the payment page for a specific order"""
    order = orders.get(order_id, None)
    if not order:
        return {"error": "Order not found"}
    
    return templates.TemplateResponse("payment_page.html", {"request": request, "order": order})

@app.post("/process_payment/")
async def process_payment(payment: PaymentRequest):
    """Process the payment and publish event to Kafka"""
    order_id = payment.order_id
    status = payment.status
   
    if not order_id:
        return {"error": "Order not found"}

    # Simulate payment processing
  
    await producer.send(PAYMENT_TOPIC, order_id)
    print(f"Payment processed for order {order_id}")

    return {"message": "Payment processed successfully!", "order": order_id,"status":status}
