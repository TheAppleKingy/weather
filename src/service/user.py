import uuid

from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException

from typing import Optional


def identify(response: HTMLResponse, identificator: Optional[str]):
    if not identificator:
        identificator = str(uuid.uuid4())
        response.set_cookie(key='uuid', value=identificator,
                            max_age=60*60*24*365*2)
    return response


def check_uuid(uuid: Optional[str]):
    if not uuid:
        raise HTTPException(status_code=401)
