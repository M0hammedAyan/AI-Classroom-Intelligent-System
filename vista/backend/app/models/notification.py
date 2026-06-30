"""In-app notification model."""
from sqlalchemy import Boolean, Column, ForeignKey, Text
from ..db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Text, nullable=False)       # risk_alert | attendance | system | intervention
    is_read = Column(Boolean, default=False)
    link = Column(Text, nullable=True)        # e.g. /student/1DA23AI050
    created_at = Column(Text, nullable=False)
