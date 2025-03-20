import uuid
from sqlalchemy import (
    Column,
    String,
    func,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from app.database.database import Base


class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID, default=uuid.uuid4, index=True, primary_key=True)
    created_at = Column(DateTime, default=func.now())


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    nox_id = Column(String, nullable=False, unique=True)
    avatar = Column(String)


class Friends(BaseModel):
    __tablename__ = "friends"

    user_id = Column(
        String(15), ForeignKey("users.nox_id", ondelete="CASCADE"), nullable=False
    )
    friend_id = Column(
        String(15), ForeignKey("users.nox_id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String, nullable=False)
    action_by = Column(String(15), ForeignKey("users.nox_id", ondelete="CASCADE"))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', 'blocked')",
            name="check_status",
        ),
        UniqueConstraint("user_id", "friend_id", name="unique_user_friend"),
    )
