from models import History, UserHistory

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.exceptions import HTTPException


async def update_history(session: AsyncSession, data: dict):
    country = data['country_code']
    city = data['city_name']
    res = await session.execute(select(History).where(History.city == city, History.country == country))
    history = res.scalar_one_or_none()
    if not history:
        history = History(city=city, country=country, request_count=0)
    history.request_count += 1
    session.add(history)
    await session.commit()


async def update_user_history(session: AsyncSession, data: dict, uuid: str):
    country = data['country_code']
    city = data['city_name']
    res = await session.execute(select(UserHistory).where(UserHistory.uuid == uuid))
    user_history = res.scalar_one_or_none()
    if not user_history:
        user_history = UserHistory(
            uuid=uuid, requests_history={country: {city: 0}})
    if not country in user_history.requests_history:
        user_history.requests_history[country] = {city: 0}
    if not city in user_history.requests_history[country]:
        user_history.requests_history[country][city] = 0
    user_history.requests_history[country][city] += 1
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(user_history, "requests_history")
    session.add(user_history)
    await session.commit()
