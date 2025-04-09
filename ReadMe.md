# 🛍️ E-Commerce Microservices Project

A scalable, modular, and event-driven backend system for an e-commerce platform, built using Python microservices, JWT-based authentication, Kafka for messaging, and WebSockets for real-time updates.

---

## 🧱 Architecture

```plaintext
   +-------------+     +--------------+
   |  Frontend   |<--->|  User Service|<-- JWT Token
   +-------------+     +--------------+
                             |
                             v
                      +--------------+
                      | Order Service|<---> Kafka (order_topic)
                      +--------------+
                             |
         +-------------------+-------------------+
         |                                       |
         v                                       v
+------------------+                  +----------------------+
| Payment Service  | (payment_topic)         | Notification Service |
+------------------+                  +----------------------+
                                               |
                                               v
                                           (Future)

---

## 🚀 Microservices Overview

### 👤 User Service (Flask)
- Handles user registration and login
- Issues JWT tokens
- 

### 📦 Order Service (FastAPI)
- Authenticates users via JWT
- Places new orders
- Publishes order events to order_topic(Kafka)
- Sends real-time updates to frontend via WebSocket

### 🔔 Payment Service (Python)
- Subscribes to `order_topic` from Kafka
- When user pay the amount, publish payment_status to payment_topic(kafka)


### 🔔 Notification Service (Python)
- Subscribes to `payment_topic` from Kafka
- Sends payment status notifications to user.


---

## 🧰 Tech Stack

- **Flask** for user service
- **FastAPI** for order service
- **MongoDB** for order data
- **Kafka** for event streaming
- **WebSockets** for real-time UI
- **JWT** for authentication
- **Jinja2** for server-side templating

---

## 🔐 Authentication Flow

1. User logs in via `/login` endpoint.
2. JWT token is issued and stored in browser (cookie or header).
3. Token is used to access protected routes (like `/orders`) in order service.

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/21-Mohit/ecommerce-microservices.git
cd ecommerce-microservices
