import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Subscription
from app.schemas.subscription import SubscribeRequest, SubscribeResponse

router = APIRouter()

@router.post("", response_model=SubscribeResponse)
async def subscribe_email(req: SubscribeRequest, db: AsyncSession = Depends(get_db)):
    if req.cohort not in ["2026", "2027", "2028", "all"]:
        raise HTTPException(status_code=400, detail="Invalid cohort. Must be 2026, 2027, 2028, or all.")

    existing_query = select(Subscription).where(
        Subscription.email == req.email.lower(),
        Subscription.cohort == req.cohort
    )
    res = await db.execute(existing_query)
    sub = res.scalar_one_or_none()

    if sub:
        if not sub.is_active:
            sub.is_active = True
            await db.commit()
        return SubscribeResponse(
            success=True,
            message="Your subscription has been renewed!",
            email=sub.email,
            cohort=sub.cohort
        )

    token = secrets.token_urlsafe(32)
    new_sub = Subscription(
        email=req.email.lower(),
        cohort=req.cohort,
        is_active=True,
        token=token
    )
    db.add(new_sub)
    await db.commit()

    return SubscribeResponse(
        success=True,
        message="Subscribed successfully! You will receive daily 06:00 IST verified digests.",
        email=new_sub.email,
        cohort=new_sub.cohort
    )

@router.get("/unsubscribe")
async def unsubscribe(token: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Subscription).where(Subscription.token == token))
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Invalid unsubscribe token")

    sub.is_active = False
    await db.commit()
    return {"message": "You have been successfully unsubscribed from FreshersDaily digests."}
