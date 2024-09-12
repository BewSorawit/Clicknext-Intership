from datetime import timedelta
from fastapi import FastAPI
import uvicorn
from app.routers import face_detection, auth
from app.database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(face_detection.router)
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                log_level="info", reload=True)
