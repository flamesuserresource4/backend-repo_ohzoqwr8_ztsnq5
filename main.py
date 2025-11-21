import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from database import db
from schemas import Chatbot as ChatbotSchema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# -------------------- Chatbot Config Endpoints --------------------
class ChatbotIn(BaseModel):
    user_email: str
    is_active: Optional[bool] = True
    webhook_url: Optional[str] = None
    greeting_message: Optional[str] = "Hi! I'm your WhatsApp AI assistant."
    auto_replies: Optional[List[str]] = []

@app.get("/api/chatbot")
def get_chatbot(user_email: str = Query(..., description="Owner email")):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["chatbot"].find_one({"user_email": user_email}, sort=[("updated_at", -1)])
    if not doc:
        # Return default schema if none exists yet
        default = ChatbotSchema(user_email=user_email)
        return default.model_dump()
    # Convert ObjectId and datetime
    doc["_id"] = str(doc.get("_id"))
    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()
    if "updated_at" in doc:
        doc["updated_at"] = doc["updated_at"].isoformat()
    return doc

@app.post("/api/chatbot")
def upsert_chatbot(payload: ChatbotIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    from datetime import datetime, timezone
    data = payload.model_dump()
    now = datetime.now(timezone.utc)
    existing = db["chatbot"].find_one({"user_email": payload.user_email})
    if existing:
        db["chatbot"].update_one(
            {"_id": existing["_id"]},
            {"$set": {**data, "updated_at": now}}
        )
        updated = db["chatbot"].find_one({"_id": existing["_id"]})
    else:
        data["created_at"] = now
        data["updated_at"] = now
        inserted = db["chatbot"].insert_one(data)
        updated = db["chatbot"].find_one({"_id": inserted.inserted_id})
    updated["_id"] = str(updated.get("_id"))
    if "created_at" in updated:
        updated["created_at"] = updated["created_at"].isoformat()
    if "updated_at" in updated:
        updated["updated_at"] = updated["updated_at"].isoformat()
    return updated

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
