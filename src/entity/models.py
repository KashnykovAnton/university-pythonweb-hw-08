from datetime import datetime

from sqlalchemy import String, DateTime, Date, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.conf import constants


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(
        String(constants.NAME_MAX_LENGTH), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(constants.NAME_MAX_LENGTH), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(constants.EMAIL_MAX_LENGTH), unique=True, nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(constants.PHONE_MAX_LENGTH), nullable=False
    )
    birthday: Mapped[datetime] = mapped_column(Date, nullable=False)
    additional_info: Mapped[str] = mapped_column(
        String(constants.ADDITIONAL_INFO_MAX_LENGTH), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
