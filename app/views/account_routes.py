from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.bank_service import create_account
import logging

# Configura o log básico (opcional, mas útil para depuração)
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

router = APIRouter(prefix="/accounts", tags=["Contas"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_new_account(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Cria uma nova conta bancária vinculada a um usuário existente.
    
    - **user_id**: ID do usuário que será dono da conta.
    """
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O ID do usuário deve ser um número positivo."
        )

    try:
        account = await create_account(db, user_id)
        logging.info(f"Conta criada com sucesso: user_id={user_id}, account_id={account.id}")

        return {
            "message": "Conta criada com sucesso!",
            "data": {
                "account_id": account.id,
                "user_id": account.user_id,
                "saldo_inicial": account.balance
            }
        }

    except ValueError as e:
        logging.warning(f"Erro de validação ao criar conta (user_id={user_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except HTTPException:
        raise  # Re-levanta exceções HTTP já tratadas

    except Exception as e:
        logging.error(f"Erro inesperado ao criar conta (user_id={user_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno ao criar a conta. Tente novamente mais tarde."
        )
