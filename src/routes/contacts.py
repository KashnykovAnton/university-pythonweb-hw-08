import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.database.db import get_db
from src.services.contacts import ContactService

# from src.models import Contact
from src.schemas.contact import ContactSchema, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
       contact_service = ContactService(db)
    return await contact_service.get_contacts(limit, offset)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    contact = Contact(**body.dict())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, body: ContactSchema, db: AsyncSession = Depends(get_db)
):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    for key, value in body.dict().items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    await db.delete(contact)
    await db.commit()
    return None


@router.get("/search", response_model=list[ContactResponse])
async def search_contacts(
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Contact)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/upcoming_birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)

    query = select(Contact).where(
        (Contact.birthday >= today) & (Contact.birthday <= next_week)
    )
    result = await db.execute(query)
    return result.scalars().all()
