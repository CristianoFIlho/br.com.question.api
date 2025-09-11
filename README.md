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
# Configurar variáveis de ambiente (copiar .env.example para .env)
cp .env.example .env

# Executar migrações
alembic upgrade head
```

## 🏃‍♂️ Executar

```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentação da API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testes

```bash
pytest
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
