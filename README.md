# Sistema Bancário V1 — API Assíncrona (FastAPI)

API bancária assíncrona construída com FastAPI e SQLAlchemy 2.x (async) usando SQLite (aiosqlite) por padrão. O projeto expõe rotas para cadastro de usuários, criação de contas e operações bancárias básicas (depósito, saque e extrato), além de documentação automática via Swagger UI.

## Sumário
- Visão Geral
- Stack e Funcionalidades
- Requisitos
- Instalação
- Configuração (.env)
- Executando a API
- Documentação e Teste Rápido
- Endpoints Principais (com exemplos)
- Estrutura do Projeto
- Notas e Limitações

## Visão Geral
Este serviço oferece um backend simples de sistema bancário, com modelos para `User`, `Account` e `Transaction`, serviços de negócio e rotas organizadas por domínio.

## Stack e Funcionalidades
- FastAPI para a camada HTTP.
- SQLAlchemy (async) + aiosqlite como banco local padrão.
- Pydantic para validação.
- passlib[bcrypt] para hashing de senhas.
- jose para utilidades de JWT (sem rota de login implementada ainda).
- Criação automática das tabelas no startup da aplicação.

## Requisitos
- Python 3.10+ (recomendado 3.11)
- pip

## Instalação
1) Crie e ative um ambiente virtual:
- Windows (PowerShell):
  - `python -m venv .venv`
  - `.venv\Scripts\Activate.ps1`
- Linux/macOS:
  - `python -m venv .venv`
  - `source .venv/bin/activate`

2) Instale as dependências:
- `pip install -r requirements.txt`

## Configuração (.env)
Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo (exemplo):

```
# URL do banco (SQLite assíncrono local)
DB_URL=sqlite+aiosqlite:///./bank.db

# Configuração JWT (utilidades prontas; sem rota de login ainda)
SECRET_KEY=troque-por-uma-chave-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Observações:
- `DB_URL` pode apontar para outro banco compatível com SQLAlchemy async (ex.: Postgres + asyncpg), se preferir.
- `ACCESS_TOKEN_EXPIRE_MINUTES` deve ser um número inteiro (minutos).

## Executando a API
- Via uvicorn diretamente:
  - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Ou usando o Makefile (se disponível no seu ambiente):
  - `make run`

A aplicação cria as tabelas automaticamente ao iniciar.

## Documentação e Teste Rápido
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Principais (com exemplos)
Base URLs (locais): `http://localhost:8000`

Usuários (`app/views/user_routes.py`)
- POST `/users/register` (Form)
  - Campos: `username`, `password`
  - Exemplo (PowerShell):
    - `curl -Method POST -Uri "http://localhost:8000/users/register" -Form @{ username='alice'; password='SenhaForte123' }`
  - Exemplo (curl):
    - `curl -X POST -F "username=alice" -F "password=SenhaForte123" http://localhost:8000/users/register`
- GET `/users/buscar/{user_id}`
  - Ex.: `curl http://localhost:8000/users/buscar/1`

Contas (`app/views/account_routes.py`)
- POST `/accounts/create?user_id={id}`
  - Ex.: `curl -X POST "http://localhost:8000/accounts/create?user_id=1"`

Operações Bancárias (`app/views/routes.py` – prefixo `/api`)
- POST `/api/deposito/{account_id}?amount={valor}`
  - Ex.: `curl -X POST "http://localhost:8000/api/deposito/1?amount=150.75"`
- POST `/api/saque/{account_id}?amount={valor}`
  - Ex.: `curl -X POST "http://localhost:8000/api/saque/1?amount=50"`
- GET `/api/extrato/{account_id}`
  - Ex.: `curl "http://localhost:8000/api/extrato/1"`

Códigos de resposta comuns:
- 201 Created: criação bem-sucedida (usuário, conta).
- 200 OK: operações realizadas/consultas.
- 400/422: validações (valor inválido, usuário/conta inexistente, saldo insuficiente).
- 500: erro interno não previsto.

## Estrutura do Projeto
```
.
├─ app/
│  ├─ main.py                 # Cria app FastAPI e inclui routers
│  ├─ models/
│  │  ├─ database.py         # Engine async, sessão e Base
│  │  ├─ user.py             # Modelo User
│  │  ├─ account.py          # Modelo Account
│  │  ├─ transaction.py      # Modelo Transaction
│  │  └─ __init__.py
│  ├─ services/
│  │  ├─ auth_service.py     # Hash de senha, JWT util, criação de usuários
│  │  └─ bank_service.py     # Depósito, saque, extrato, criar conta
│  ├─ views/
│  │  ├─ user_routes.py      # Rotas de usuário
│  │  ├─ account_routes.py   # Rotas de conta
│  │  └─ routes.py           # Rotas de operações bancárias
│  ├─ controllers/
│  │  └─ auth.py             # Utilidades JWT/crypto (não expostas em rotas)
│  └─ utils/
│     └─ estrutura.py        # Script auxiliar (sem impacto na API)
├─ requirements.txt
├─ Makefile                  # Alvo: run
├─ log.txt                   # Log básico para criação de contas
├─ system.py / system_poo.py # Versões antigas/CLI (fora do fluxo da API)
└─ README.md
```

## Notas e Limitações
- As senhas são armazenadas com hash bcrypt; nunca armazene senhas em texto puro.
- Utilidades de JWT estão presentes, mas não há rotas de autenticação/login implementadas no momento.
- O valor de `amount` nas operações vem como querystring (não no corpo JSON).
- Em `account_routes.py` há logging simples para `log.txt`.
- Se usar outro banco (Postgres, etc.), ajuste `DB_URL` e as dependências necessárias.

## Próximos Passos (sugestões)
- Adicionar rota de login e proteção com JWT nas rotas.
- Mover `amount` para o corpo (Pydantic) e padronizar respostas.
- Adicionar testes automatizados e CI.
- Adicionar migrações de banco com Alembic.

---
