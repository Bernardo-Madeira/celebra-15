# celebra-15

Sistema de Gestão de Eventos de Debutantes — plataforma web para organização de festas de 15 anos (convidados, mesas, presentes, fornecedores, cronograma, conteúdo cerimonial, playlist colaborativa, avisos e mural de fotos/postagens).

Projeto desenvolvido como Trabalho de Conclusão de Curso (TCC) — FAETERJ, Análise e Desenvolvimento de Sistemas.

**Autor:** Bernardo Madeira Pacífico de Souza Brito
**Orientador:** Prof. Alexandre Louzada

## Stack

- **Backend:** FastAPI (Python) — arquitetura em camadas: `routers` → `services` → `models` (SQLAlchemy)
- **Banco de dados:** MySQL (via Docker)
- **Migrações:** Alembic
- **Autenticação:** JWT (python-jose) + bcrypt (passlib) para organizador/cerimonialista; convidado acessa via `token_confirmacao` (sem login)
- **Frontend:** React + Vite, React Router DOM, Axios, Tailwind CSS, React Hook Form + Zod

## Estrutura do repositório

```
celebra-15/
├── backend/          # API FastAPI
├── frontend/         # SPA React (Vite)
├── docs/             # Diagramas e documentação técnica
└── docker-compose.yml
```

## Como rodar (desenvolvimento)

### 1. Subir o banco de dados (MySQL via Docker)

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # ajuste as variáveis se necessário
alembic upgrade head
uvicorn app.main:app --reload
```

API disponível em `http://localhost:8000` — documentação interativa em `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend disponível em `http://localhost:5173`.

## Status

Projeto em desenvolvimento inicial — scaffold do monorepo. Modelagem de entidades já definida (ver `docs/`); implementação de models, migrações e endpoints em andamento.
