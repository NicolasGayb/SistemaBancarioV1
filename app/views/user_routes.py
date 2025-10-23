from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.user import User
from app.services.auth_service import create_user
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["Usuários"])

@router.post("/register", summary="Registrar um novo usuário", status_code=status.HTTP_201_CREATED)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um novo usuário.
    - **username**: nome de usuário único.
    - **password**: senha em texto simples (até 72 caracteres).
    """
    if not username or not password:
        raise HTTPException(status_code=400, detail="Usuário e senha são obrigatórios.")

    try:
        user = await create_user(db, username, password)
        return {"message": "Usuário criado com sucesso!", "user_id": user.id}

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Nome de usuário já existe.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/buscar/{user_id}", summary="Obter informações do usuário pelo ID", status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Obtém informações do usuário pelo ID."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"username": user.username, "user_id": user.id, "accounts": [account.id for account in user.accounts]}
