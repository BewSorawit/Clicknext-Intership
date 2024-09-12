from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class FaceDetectionResult(Base):
    __tablename__ = 'face_detection_results'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    detected_faces = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="face_detection_results")

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "detected_faces": self.detected_faces,
            "created_at": self.created_at.isoformat()
        }
