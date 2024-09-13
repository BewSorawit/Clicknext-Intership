from fastapi import FastAPI
import uvicorn
from app.routers import face_detection, auth
from app.database import engine, Base
from middleware.middleware import AdvancedMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.add_middleware(AdvancedMiddleware)

app.include_router(face_detection.router)
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                reload=True,
                log_level="info",
                ssl_certfile="../ssl/cert.pem",
                ssl_keyfile="../ssl/key.pem")
