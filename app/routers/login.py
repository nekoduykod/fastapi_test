from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db

from app.models.models import Users as ModelUsers

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, 
               username: str = Form(...),
               password: str = Form(...)):
    credentials = db.session.query(ModelUsers) \
                            .filter(ModelUsers.username == username) \
                            .filter(ModelUsers.password == password) \
                            .first()
    if credentials:
        role = credentials.role
        request.session["user"] = {"username": username, "id": credentials.id, "role": role}
        return RedirectResponse(url="/account", status_code=303)
    else:
        return templates.TemplateResponse("login.html",
                                          {"request": request,
                                           "error": "Invalid login or password"})
