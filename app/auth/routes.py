from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models import User
from app.schemas import UserRegister, UserLogin, Token
from app.auth.utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == user_data.username))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        name=user_data.name,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == credentials.username))
    user = result.scalar()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}
