from fastapi import FastAPI
from pydantic import BaseModel
from firebase_service import db
import uuid
import uvicorn
app = FastAPI()

class Complaint(BaseModel):
    name: str
    mobile: str
    complaint: str

class Status(BaseModel):
    complaint_id:str

@app.post("/register")
def register_complaint(data: Complaint):
    complaint_id = str(uuid.uuid4())
    db.collection("complaints").document(complaint_id).set({
        "name": data.name,
        "mobile": data.mobile,
        "complaint": data.complaint,
        "status": "In Progress",
        "complaint_id": complaint_id
    })
    return {"message": "Complaint registered", "complaint_id": complaint_id}

@app.post("/status")
def get_status(status: Status):
    doc = db.collection("complaints").document(status.complaint_id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {"error": "Complaint not found"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)