from typing import List, Optional
from fastapi import Request, Form, APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.models import Users as ModelUsers, Tickets as ModelTickets, Groups as ModelGroups


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_tickets(db: Session) -> List[ModelTickets]:
    return db.query(ModelTickets).all()

def get_user_tickets(db: Session, user_id: int) -> List[ModelTickets]:
    return db.query(ModelTickets).filter(ModelTickets.user_id == user_id).all()

def get_all_users(db: Session) -> List[ModelUsers]:
    return db.query(ModelUsers).all()

def get_all_groups(db: Session) -> List[ModelGroups]:
    return db.query(ModelGroups).all()


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get('/account', response_class=HTMLResponse)
async def account_page(request: Request, page: int = 1, db: Session = Depends(get_db)):
    user = request.session.get("user")

    if user:
        db_user = db.query(ModelUsers).filter(ModelUsers.id == user["id"]).first()
        role = db_user.role if db_user else None

        tickets_query = db.query(ModelTickets)
        total_tickets = tickets_query.count()
        total_pages = (total_tickets + 4) // 5

        if role == "Admin":
            tickets = tickets_query.order_by(ModelTickets.id.desc()).offset((page - 1) * 5).limit(5).all()
            group_id = None
        elif role in ["Manager", "Analyst"]:
            group_id = db_user.group_id
            tickets = tickets_query.filter(
                (ModelTickets.group_id == group_id) | (ModelTickets.group_id == None)
            ).order_by(ModelTickets.id.desc()).offset((page - 1) * 5).limit(5).all()
            
        prev_page = page - 1 if page > 1 else None
        next_page = page + 1 if (page < total_pages) and (total_tickets > (page * 5)) else None

        users = get_all_users(db)
        groups = get_all_groups(db)
        return templates.TemplateResponse("account.html", 
                                          {"request": request,
                                           "user": user, 
                                           "role": role,
                                           "error": None,
                                           "tickets": tickets,
                                           "users": users,
                                           "groups": groups,
                                           "group_id": group_id,
                                           "current_page": page,
                                           "total_pages": total_pages,
                                           "prev_page": prev_page,
                                           "next_page": next_page})
    else:
        return templates.TemplateResponse("account.html",
                                          {"request": request,
                                           "user": None, 
                                           "role": None,
                                           "error": "You are not logged in"})


@router.post('/create-ticket', response_class=HTMLResponse)
async def create_ticket(request: Request,
                        note: str = Form(...),
                        group_id: Optional[int] = Form(None),
                        db: Session = Depends(get_db)):
    user_id = request.session.get("user")["id"]
    
    if group_id == '': group_id = None
    
    new_ticket = ModelTickets(note=note, user_id=None, group_id=group_id)
    db.add(new_ticket)
    db.commit()
    return RedirectResponse(url='/account', status_code=303)


@router.post('/update-ticket-status', response_class=HTMLResponse)
async def update_ticket_status(request: Request,
                               ticket_id: int = Form(...),
                               status: str = Form(...),
                               db: Session = Depends(get_db)):
    ticket = db.query(ModelTickets).filter(ModelTickets.id == ticket_id).first()
    if ticket:
        ticket.status = status
        db.commit()
    return RedirectResponse(url='/account', status_code=303)


@router.post('/assign-ticket-user', response_class=HTMLResponse)
async def assign_ticket_user(request: Request,
                             ticket_id: int = Form(...),
                             user_id: int = Form(None),
                             db: Session = Depends(get_db)):
    ticket = db.query(ModelTickets).filter(ModelTickets.id == ticket_id).first()
    user = request.session.get("user")

    if ticket and user and user.get("role") in ["Admin", "Manager"]:
        if user_id == '' or user_id is None:
            ticket.user_id = None
        else:
            ticket.user_id = user_id
        db.commit()
    return RedirectResponse(url='/account', status_code=303)


@router.post('/assign-ticket-group', response_class=HTMLResponse)
async def assign_ticket_group(request: Request,
                              ticket_id: int = Form(...),
                              group_id: int = Form(None),
                              db: Session = Depends(get_db)):
    ticket = db.query(ModelTickets).filter(ModelTickets.id == ticket_id).first()

    user = request.session.get("user")
    if ticket and user and user.get("role") in ["Admin", "Manager"]:
        if group_id == '' or group_id is None:
            ticket.group_id = None
        else:
            ticket.group_id = group_id
            db.commit()
    return RedirectResponse(url='/account', status_code=303)


@router.post('/create-group', response_class=HTMLResponse)
async def create_group(request: Request,
                       title: str = Form(...),
                       db: Session = Depends(get_db)):
    user = request.session.get("user")
    db_user = db.query(ModelUsers).filter(ModelUsers.id == user["id"]).first()
    role = db_user.role if db_user else None
    if user and user.get("role") == "Admin":
        new_group = ModelGroups(title=title)
        db.add(new_group)
        db.commit()
        return templates.TemplateResponse("account.html", 
                                          {"request": request,
                                           "user": user,
                                           "role": role, 
                                           "error": None,})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )


@router.post('/assign-role', response_class=HTMLResponse)
async def assign_role(request: Request,
                      user_id: int = Form(...),
                      role: str = Form(...),
                      db: Session = Depends(get_db)):
    current_user = request.session.get("user")
    if current_user and current_user.get("role") == "Admin":
        user = db.query(ModelUsers).filter(ModelUsers.id == user_id).first()
        if user:
            user.role = role
            db.commit()
    return RedirectResponse(url='/account', status_code=303)


@router.post('/assign-user-group', response_class=HTMLResponse)
async def assign_user_group(request: Request,
                            user_id: int = Form(...),
                            group_id: int = Form(None),
                            db: Session = Depends(get_db)):
    current_user = request.session.get("user")
    if current_user and current_user.get("role") == "Admin":
        user = db.query(ModelUsers).filter(ModelUsers.id == user_id).first()
        if user:
            if group_id == '' or group_id is None:
                user.group_id = None
            else:
                user.group_id = group_id
            db.commit()
    return RedirectResponse(url='/account', status_code=303)


@router.post('/account', response_class=HTMLResponse)
async def change_pass(request: Request,
                      current_password: str = Form(...),
                      new_password: str = Form(...),
                      confirm_password: str = Form(...),
                      db: Session = Depends(get_db)):
    user = request.session.get("user")
    
    if not user:
        return templates.TemplateResponse("account.html", 
                                          {"request": request,
                                           "error": "You are not logged in"})
    
    db_user = db.query(ModelUsers).filter(ModelUsers.id == user["id"]).first()
    role = db_user.role if db_user else None
    
    username = user["username"]
    existing_user = db.query(ModelUsers).filter(ModelUsers.username == username).first()

    if not existing_user:
        return templates.TemplateResponse("account.html",
                                          {"request": request,
                                           "user": {"username": username},
                                           "role": role,
                                           "error": "User not found"})
    
    if not current_password:
        return templates.TemplateResponse("account.html",
                                          {"request": request,
                                           "user": {"username": username},
                                           "role": role,
                                           "error": "Current password is required"})
    
    if new_password != confirm_password:
        return templates.TemplateResponse("account.html",
                                          {"request": request,
                                           "user": {"username": username},
                                           "role": role,
                                           "error": "New and confirm password do not match"})
    
    existing_user.password = new_password
    db.commit()

    request.session["user"] = {"username": username, "id": existing_user.id}

    return templates.TemplateResponse("account.html",
                                      {"request": request,
                                       "role": role,
                                       "user": {"username": username},
                                       "success": "Password changed successfully"})
