from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from ..utils.security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Пользователь с таким username уже существует")
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")
    if user_data.role == UserRole.PARENT.value and not user_data.linked_student_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Для роли 'родитель' необходимо указать linked_student_id")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        linked_student_id=user_data.linked_student_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})

    from ..services.audit_service import log_action
    log_action(db, new_user.id, new_user.full_name, "Зарегистрировался", f"Роль: {new_user.role}")

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=new_user.id, username=new_user.username, email=new_user.email,
                          full_name=new_user.full_name, role=new_user.role)
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный username или пароль",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    from ..services.audit_service import log_action
    log_action(db, user.id, user.full_name, "Вошёл в систему", f"Роль: {user.role}")

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(id=user.id, username=user.username, email=user.email, full_name=user.full_name,
                          role=user.role)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(token: str, db: Session = Depends(get_db)):
    from ..utils.security import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return UserResponse(id=user.id, username=user.username, email=user.email, full_name=user.full_name, role=user.role)


@router.put("/change-password")
def change_password(
        old_password: str,
        new_password: str,
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    from ..utils.security import verify_token

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный старый пароль")

    user.hashed_password = hash_password(new_password)
    db.commit()

    from ..services.audit_service import log_action
    log_action(db, user_id, user.full_name, "Сменил пароль", "")

    return {"message": "Пароль изменён"}