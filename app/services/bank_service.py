from app.models import Account, Transaction
from sqlalchemy.future import select

async def create_account(db, user_id: int):
    """Cria uma nova conta bancária para o usuário especificado.
    
    Args:
        db: Sessão do banco de dados.
        user_id (int): ID do usuário para o qual a conta será criada.
        
    Returns:
        Account: A conta bancária criada.
    Raises:
        ValueError: Se o usuário já possuir uma conta.
    """
    result = await db.execute(select(Account).filter(Account.user_id == user_id))
    existing_account = result.scalars().first()
    if existing_account:
        raise ValueError("Usuário já possui uma conta cadastrada.")
    
    account = Account(user_id=user_id, balance=0.0)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def deposit(db, account_id: int, amount: float):
    """Realiza um depósito na conta especificada.
    
    Args:
        db: Sessão do banco de dados.
        account_id (int): ID da conta onde o depósito será realizado.
        amount (float): Valor do depósito.

    Returns:
        float: Novo saldo da conta após o depósito.
    Raises:
        ValueError: Se o valor do depósito for inválido ou a conta não for encontrada.
    """
    if amount <= 0:
        raise ValueError("Valor de depósito inválido.")
    result = await db.execute(select(Account).filter(Account.id == account_id))
    account = result.scalars().first()
    if not account:
        raise ValueError("Conta não encontrada.")
    account.balance += amount
    transaction = Transaction(account_id=account_id, type="deposit", amount=amount)
    db.add(transaction)
    await db.commit()
    await db.refresh(account)
    return account.balance


async def withdraw(db, account_id: int, amount: float):
    """Realiza um saque na conta especificada.
    
    Args:
        db: Sessão do banco de dados.
        account_id (int): ID da conta onde o saque será realizado.
        amount (float): Valor do saque.
        
    Returns:
        float: Novo saldo da conta após o saque.
    Raises:
        ValueError: Se o valor do saque for inválido, a conta não for encontrada ou saldo insuficiente.
    """
    if amount <= 0:
        raise ValueError("Valor de saque inválido.")
    result = await db.execute(select(Account).filter(Account.id == account_id))
    account = result.scalars().first()
    if not account:
        raise ValueError("Conta não encontrada.")
    if account.balance < amount:
        raise ValueError("Saldo insuficiente.")
    account.balance -= amount
    transaction = Transaction(account_id=account_id, type="withdraw", amount=amount)
    db.add(transaction)
    await db.commit()
    await db.refresh(account)
    return account.balance


async def get_statement(db, account_id: int):
    """Obtém o extrato de transações da conta especificada.

    Args:
        db: Sessão do banco de dados.
        account_id (int): ID da conta para a qual o extrato será obtido.
    Returns:
        List[Transaction]: Lista de transações da conta.
    """
    result = await db.execute(select(Transaction).filter(Transaction.account_id == account_id))
    return result.scalars().all()
