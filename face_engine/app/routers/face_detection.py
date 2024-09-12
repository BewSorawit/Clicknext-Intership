from datetime import datetime
import traceback
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from requests import Session
from app.database import SessionLocal, get_db
import cv2
import numpy as np
from PIL import Image
import io
import base64
from fastapi import APIRouter, HTTPException

from app.models.face_detection import FaceDetectionResult
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix='/face', tags=["face"])


class ImageRequest(BaseModel):
    image_base64: str


def base642image(base64str: str, use_opencv: bool = False):
    image = None
    if use_opencv:
        data_bytes = np.frombuffer(base64.b64decode(base64str), np.uint8)
        image = cv2.imdecode(data_bytes, cv2.IMREAD_COLOR)
    else:
        image_bytes = base64.b64decode(base64str)
        image = Image.open(io.BytesIO(image_bytes))
    return image


def detect_faces(image: np.array):
    # Load the Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image using the Haar Cascade classifier
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5)

    # Draw bounding boxes around the detected faces
    for x, y, w, h in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return image


@router.post("/detect_faces", operation_id="detect_faces")
def detect_faces_endpoint(request: ImageRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == current_user['user_id']).first()
    if user.api_quota_limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="API quota exceeded")

    try:
        image = base642image(request.image_base64, use_opencv=True)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image data")

        image_out = detect_faces(image)
        _, buffer = cv2.imencode(".jpg", image_out)
        b64str_out = base64.b64encode(buffer).decode('utf-8')

        result = FaceDetectionResult(
            user_id=current_user['user_id'],
            detected_faces=b64str_out
        )
        db.add(result)
        db.commit()
        db.refresh(result)

        user.api_quota_limit -= 1
        db.commit()

        return {"result": b64str_out}
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {str(e)}")
    finally:
        db.close()


@router.get("/results")
def get_results(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    result_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # print(f"Current User ID: {current_user['user_id']}")
        query = db.query(FaceDetectionResult).filter(
            FaceDetectionResult.user_id == current_user['user_id'])
        # print(f"Initial Query Count: {query.count()}")
        if start_time:
            query = query.filter(FaceDetectionResult.created_at >= start_time)
        if end_time:
            query = query.filter(FaceDetectionResult.created_at <= end_time)
        if result_id:
            query = query.filter(FaceDetectionResult.id == result_id)
        # print(f"Filtered Query Count: {query.count()}")
        results = query.all()
        # print(f"Results: {results}")

        return results

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {str(e)}")
