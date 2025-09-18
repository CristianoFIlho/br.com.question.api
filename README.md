# api.question.com.br

# Salesforce Quiz API

FastAPI backend para o sistema de simulados Salesforce.

## 🚀 Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## 🗄️ Configuração do Banco de Dados

```bash
# Configurar variáveis de ambiente (copiar env.example para .env)
cp env.example .env

# Executar migrações
python migrate.py
```

## 🏃‍♂️ Executar

```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Para usar endpoints protegidos:

1. **Registrar usuário:**
   ```bash
   POST /api/v1/auth/register
   {
     "name": "João Silva",
     "email": "joao@example.com",
     "password": "senha123",
     "role": "user"
   }
   ```

2. **Fazer login:**
   ```bash
   POST /api/v1/auth/login
   {
     "username": "joao@example.com",
     "password": "senha123"
   }
   ```

3. **Usar token nos headers:**
   ```
   Authorization: Bearer <seu-token-jwt>
   ```

## 📚 Documentação da API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com verbose
pytest -v

# Executar apenas testes unitários
pytest -m unit

# Executar apenas testes de integração
pytest -m integration

# Executar testes com coverage
pytest --cov=app

# Executar testes específicos
pytest tests/test_auth.py
```

## 📁 Estrutura do Projeto

```
salesforce-api/
├── app/
│   ├── core/           # Configurações e segurança
│   ├── database/       # Conexão e configuração do banco
│   ├── models/         # Modelos SQLAlchemy
│   ├── routers/        # Endpoints da API
│   ├── services/       # Lógica de negócio
│   └── main.py         # Aplicação principal
├── alembic/           # Migrações do banco
├── tests/             # Testes
└── requirements.txt   # Dependências
```
