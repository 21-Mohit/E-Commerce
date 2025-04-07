from fastapi import FastAPI, Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from kafka import KafkaProducer
from pydantic import BaseModel
import json
import logging
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

# Kafka Configuration
KAFKA_BROKER_URL = "localhost:9092"
ORDER_TOPIC = "order_topic"


# WebSockets for real-time updates
clients = []

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Serve static files
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

class Settings(BaseModel):
    authjwt_secret_key: str = "your_secret_key"  # Same as user_service
    authjwt_token_location: set = {"cookies"}  # ADD THIS!
    authjwt_cookie_csrf_protect: bool = False

@AuthJWT.load_config
def get_config():
    return Settings()

# JWT Exception Handler
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": exc.message})


# Order Model
class OrderRequest(BaseModel):
    order_id: str
    user_id: str
    product_id: str
    quantity: int
    
def get_current_user(request: Request, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    request.state.current_user = current_user  # Store in request state for templates
    return current_user

@app.get("/")
async def home(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("index.html",  {"request": request, "user": user})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        clients.remove(websocket)

@app.post("/place_order/")
async def place_order(order: OrderRequest):
    """API to place a new order and publish event to Kafka"""
    order_event = order.dict()
    order_event["status"] = "Payment_Pending"
    if "_id" not in order_event:
        order_event["_id"] = order_event["order_id"]
    logging.info(f'order info{order_event}')

    producer.send(ORDER_TOPIC, order_event)
    logging.info('order info sent to order_topic')
    producer.flush()
    
    #save to db
    inserted_id = db.insert_order(order_event)
    logger.info(f'order_id {inserted_id} saved to db')

    # Send real-time update via WebSockets
    for client in clients:
        await client.send_json(order_event)

    return {"message": "Order placed successfully!", "order": order_event}
