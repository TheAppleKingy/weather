from fastapi import FastAPI, Request, Form, Cookie, Depends, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from service.weather_api import get_forecast, extract_data

from typing import Optional

from service.user import identify, check_uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session

from models import History, UserHistory

from schemas import UserHistorySchema, HistorySchema

from service.history import update_history, update_user_history


app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/show_forecast', response_class=HTMLResponse)
def show_forecast_form(request: Request, uuid: Optional[str] = Cookie(default=None)):
    resp = identify(templates.TemplateResponse(
        'forecast_form.html', {'request': request}), uuid)
    return resp


@app.post('/show_forecast', response_class=HTMLResponse)
async def show_forecast(request: Request, city: str = Form(), uuid: str = Cookie(default=None), session: AsyncSession = Depends(get_db_session)):
    check_uuid(uuid)
    forecast, geopolitically_data = await get_forecast(city)
    prepaired_data = extract_data(forecast)
    await update_history(session, geopolitically_data)
    await update_user_history(session, geopolitically_data, uuid)
    return templates.TemplateResponse(
        "forecast.html",
        {
            "request": request,
            "city": city.capitalize(),
            "forecast": prepaired_data
        }
    )


@app.get('/api/users_history', response_model=list[UserHistorySchema])
async def users_histories(session: AsyncSession = Depends(get_db_session)):
    res = await session.execute(select(UserHistory))
    users_histories = res.scalars().all()
    return users_histories


@app.get('/api/user_history/{uuid}', response_model=UserHistorySchema)
async def user_history(uuid: str, session: AsyncSession = Depends(get_db_session)):
    res = await session.execute(select(UserHistory).where(UserHistory.uuid == uuid))
    user_history = res.scalar_one()
    return user_history


@app.get('/api/history', response_model=list[HistorySchema])
async def history(country: str = Query(default=None), city: str = Query(default=None), session: AsyncSession = Depends(get_db_session)):
    query = select(History)
    if country:
        query = query.where(History.country == country.upper())
    if city:
        query = query.where(History.city == city)
    res = await session.execute(query)
    history = res.scalars().all()
    return history
