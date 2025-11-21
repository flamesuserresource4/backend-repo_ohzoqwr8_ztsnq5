"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# WhatsApp Chatbot configuration schema
class Chatbot(BaseModel):
    """
    Chatbot configuration per user for WhatsApp automation
    Collection name: "chatbot"
    """
    user_email: str = Field(..., description="Owner email")
    is_active: bool = Field(True, description="Whether chatbot is enabled")
    webhook_url: Optional[str] = Field(None, description="Webhook endpoint to receive messages")
    greeting_message: Optional[str] = Field("Hi! I'm your WhatsApp AI assistant.", description="Default greeting")
    auto_replies: List[str] = Field(default_factory=lambda: [
        "What's your order number?",
        "We'll get back to you shortly.",
        "Thank you for contacting us!"
    ], description="Quick reply templates")
