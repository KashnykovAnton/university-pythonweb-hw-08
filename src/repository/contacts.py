import logging
from typing import Sequence

from sqlalchemy import select, or_, func, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.schemas.contacts import ContactSchema, ContactUpdateSchema
from datetime import date

logger = logging.getLogger("uvicorn.error")


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, limit: int, offset: int) -> Sequence[Contact]:
        stmt = select(Contact).order_by(Contact.id).offset(offset).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactSchema) -> Contact:
        contact = Contact(**body.model_dump())
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdateSchema
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            update_data = body.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(self, query: str) -> Sequence[Contact]:
        stmt = (
            select(Contact)
            .where(
                or_(
                    Contact.first_name.ilike(f"%{query}%"),
                    Contact.last_name.ilike(f"%{query}%"),
                    Contact.email.ilike(f"%{query}%"),
                )
            )
            .order_by(Contact.id)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contacts_with_birthdays(
        self, start_date: date, end_date: date
    ) -> Sequence[Contact]:
        stmt = (
            select(Contact)
            .where(
                func.to_char(Contact.birthday, "MM-DD").between(
                    func.to_char(start_date, "MM-DD"), func.to_char(end_date, "MM-DD")
                )
            )
            .order_by(asc(func.to_char(Contact.birthday, "MM-DD")))
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
