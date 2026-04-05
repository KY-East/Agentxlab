from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.models.base import Base


class PointLog(Base):
    __tablename__ = "point_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    reference_type = Column(String(30), nullable=True)
    reference_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
