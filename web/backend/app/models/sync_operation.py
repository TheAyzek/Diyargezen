from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from app.core.database import Base


class SyncOperation(Base):
    """Durable per-account receipts, committed with the character mutation."""
    __tablename__ = "sync_operations"
    __table_args__ = (UniqueConstraint("user_id", "operation_id"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    operation_id = Column(String, nullable=False)
    payload_hash = Column(String, nullable=False)
    response_json = Column(Text, nullable=False)
