from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db
from app.services.bank_service import deposit, withdraw, get_statement

router = APIRouter(prefix="/api", tags=["Banco"])

@router.post("/deposito/{account_id}")
async def make_deposit(account_id: int, amount: float, db: AsyncSession = Depends(get_db)):
    """
    Realiza um depósito em uma conta específica.
    
    - **account_id**: ID da conta onde o depósito será realizado.
    - **amount**: Valor do depósito (deve ser positivo).
    """
    try:
        new_balance = await deposit(db, account_id, amount)
        return {"message": "Depósito realizado com sucesso!", "new_balance": new_balance}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor.")

@router.post("/saque/{account_id}")
async def make_withdrawal(account_id: int, amount: float, db: AsyncSession = Depends(get_db)):
    """
    Realiza um saque em uma conta específica.
    
    - **account_id**: ID da conta onde o saque será realizado.
    - **amount**: Valor do saque (deve ser positivo e menor ou igual ao saldo disponível).
    """
    try:
        new_balance = await withdraw(db, account_id, amount)
        return {"message": "Saque realizado com sucesso!", "new_balance": new_balance}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor.")

@router.get("/extrato/{account_id}")
async def get_account_statement(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtém o extrato de transações de uma conta específica.
    
    - **account_id**: ID da conta cujo extrato será obtido.
    """
    try:
        transactions = await get_statement(db, account_id)
        return {"account_id": account_id, "transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor.")
