# Contexto do Projeto — celebra-15 (TCC Sistema de Gestão de Eventos de Debutantes)

> Este arquivo substitui o `contexto_implementacao.md` anterior, que ficou
> desatualizado (dizia "nenhum módulo implementado ainda" — não é mais
> verdade). Use este como fonte de verdade do estado atual do código.
> Continuação feita anteriormente em chat separado (claude.ai); a partir
> de agora a implementação segue no Claude Code, direto no repositório.

## Dados do trabalho

- **Instituição:** FAETERJ — Análise e Desenvolvimento de Sistemas
- **Autor:** Bernardo Madeira Pacífico de Souza Brito
- **Orientador:** Alexandre Louzada
- **Repositório:** `celebra-15` (monorepo: `backend/` + `frontend/` + `docs/`)
- O `.docx` do TCC é tratado em outro chat (redação acadêmica) — não afeta este.

## Decisões fechadas — NÃO REABRIR

- **Monorepo** (não polyrepo) — único desenvolvedor, contrato de API muda junto com o front.
- **Backend:** FastAPI, arquitetura em camadas estrita: `routers` → `services` → `models`.
  - `services` não importa nada do FastAPI (sem `HTTPException` dentro de services) — lançam exceções de domínio (`app/core/exceptions.py`), traduzidas para HTTP por **handlers globais registrados em `app/main.py`**. Todo módulo novo reaproveita esses handlers.
- **ORM:** SQLAlchemy 2.0 (estilo `Mapped`/`mapped_column`) + Alembic.
- **Banco de dados:** **MySQL** via Docker (`docker-compose.yml` na raiz, serviço `db`), driver PyMySQL.
- **Gerenciador de dependências Python:** pip + `requirements.txt` (não Poetry/Pipenv).
- **Autenticação organizador/cerimonialista:** JWT (python-jose) + bcrypt (passlib), fluxo OAuth2PasswordBearer padrão FastAPI.
- **Acesso do convidado:** sem login — via `token_confirmacao` único (gerado em `app/core/tokens.py` com `secrets.token_urlsafe`). **Não reintroduzir login de convidado.**
- **Entidade `PaiPadrinho` foi removida** — absorvida pelo campo `nomes_envolvidos` (texto livre) em `AnotacaoCerimonial`. Não recriar essa entidade.
- **Frontend:** React + Vite (não Create React App) + React Router DOM + Axios + Tailwind CSS + React Hook Form + Zod.
- **`Usuario` e `Convidado` são entidades separadas** (não unificadas por role) — convidado tem um `Usuario` próprio (perfil `convidado`, sem senha), criado automaticamente no cadastro do convidado.

## Estrutura atual do repositório

```
celebra-15/
├── docker-compose.yml          # MySQL 8.0
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── requirements-dev.txt    # pytest, httpx
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py              # já importa app.models para autogenerate
│   │   └── versions/           # vazio — nenhuma migração gerada ainda
│   ├── app/
│   │   ├── main.py             # FastAPI app + CORS + exception handlers globais
│   │   ├── config.py           # Settings (pydantic-settings, lê .env)
│   │   ├── db/database.py      # engine, SessionLocal, Base, get_db
│   │   ├── core/
│   │   │   ├── security.py     # hash/verify senha, create/decode JWT
│   │   │   ├── tokens.py       # gerar_token_confirmacao()
│   │   │   ├── exceptions.py   # DomainError e subclasses
│   │   │   └── deps.py         # get_current_usuario, require_organizador
│   │   ├── models/             # 19 entidades — ver seção abaixo
│   │   ├── schemas/
│   │   │   └── usuario.py
│   │   ├── services/
│   │   │   └── usuario_service.py
│   │   └── routers/
│   │       ├── health.py
│   │       ├── auth.py          # POST /auth/login
│   │       └── usuario.py       # POST /usuarios/organizador, /cerimonialista, GET /usuarios/me
│   └── tests/
│       ├── conftest.py          # SQLite em memória + dependency_override de get_db
│       ├── test_health.py
│       └── test_usuario.py      # 7 casos (cadastro, e-mail duplicado, login, /me, autorização)
└── frontend/
    ├── package.json             # Vite, React, Router, Axios, Tailwind, RHF+Zod (deps declaradas, npm install ainda não rodado)
    ├── vite.config.js / tailwind.config.js / postcss.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── routes/AppRoutes.jsx   # só rota "/" placeholder
        └── services/api.js       # instância Axios com interceptor de JWT
```

## Status da implementação

### ✅ Concluído

**Scaffold do monorepo** — docker-compose (MySQL), estrutura de pastas, configs do Vite/Tailwind.

**Models SQLAlchemy — todas as 19 entidades**, em `backend/app/models/`:
- `usuario.py` → `Usuario`
- `evento.py` → `Evento`
- `convidado.py` → `Mesa`, `Convidado`, `Acompanhante`
- `presente.py` → `Presente`, `ReservaPresente` (unique presente+convidado)
- `fornecedor.py` → `Fornecedor`, `Pagamento`
- `tarefa.py` → `Tarefa`
- `cerimonial.py` → `Homenagem`, `AnotacaoCerimonial`
- `playlist.py` → `Musica`, `SugestaoMusical`, `VotoMusica` (unique sugestão+convidado)
- `aviso.py` → `Aviso`
- `mural.py` → `Album`, `Foto`, `Postagem`, `Comentario`, `Curtida` (unique postagem+usuário)
- `enums.py` → todos os enums Python usados nas colunas

Todos registrados em `app/models/__init__.py`, importado por `alembic/env.py`. Todos os `back_populates` cruzados foram revisados manualmente (sem inconsistências). **Nenhuma migração Alembic foi gerada ainda** — `alembic/versions/` está vazio.

**Módulo de Usuário (organizador + cerimonialista) — completo:**
- `POST /usuarios/organizador` — cadastro público (cria conta organizador)
- `POST /usuarios/cerimonialista` — só organizador autenticado pode criar
- `POST /auth/login` — OAuth2PasswordRequestForm (username=e-mail), retorna JWT
- `GET /usuarios/me` — perfil do usuário autenticado
- `tipo_perfil` nunca vem do body da requisição — é fixado pela rota chamada (evita escalonamento de privilégio via payload)
- Login não distingue "e-mail não existe" de "senha errada" (evita enumeração de e-mail)
- Testes cobrindo os 7 cenários principais, rodando contra SQLite em memória (não precisa MySQL local para os testes)

### ⏳ Pendente (ordem sugerida)

1. **Módulo Evento + Convidado** (próximo passo natural):
   - `EventoCreate`/`EventoRead`, criação de evento vinculado ao organizador autenticado
   - Cadastro de `Convidado`: ao criar, gerar automaticamente um `Usuario` (perfil `convidado`, `senha_hash=None`) **e** um `token_confirmacao` único
   - Rota pública `GET/POST /convidados/{token}/confirmar` (sem autenticação) para o convidado confirmar/recusar presença
   - Cadastro de `Acompanhante` vinculado ao convidado, **validando** `total acompanhantes ≤ Evento.max_acompanhantes_por_convidado`
   - Contagem de confirmados
2. **Mesas** — CRUD + alocação de convidado validando `capacidade`
3. **Presentes** — CRUD + `ReservaPresente` com bloqueio de cota e de contribuição duplicada
4. **Fornecedores + Pagamentos**
5. **Tarefas (cronograma)**
6. **Homenagens + AnotacaoCerimonial**
7. **Playlist (Musica, SugestaoMusical, VotoMusica)** — bloqueio de voto duplicado
8. **Avisos** — restrito a `cerimonialista`/`equipe_interna`/`todos` (sem opção "fornecedores")
9. **Mural (Album, Foto, Postagem, Comentario, Curtida)** — bloqueio de curtida duplicada
10. Gerar a **migração Alembic inicial** (`alembic revision --autogenerate -m "modelo inicial"`) — pode ser feito já agora, ou ao final de cada módulo/lote de módulos
11. Frontend: ainda não há nenhuma tela além do placeholder — todo o front está pendente

## Regras de negócio centrais (lembrete para a camada `services`)

- Acompanhante: bloquear cadastro acima de `Evento.max_acompanhantes_por_convidado`
- Mesa: bloquear alocação que exceda `Mesa.capacidade`
- Presente: bloquear contribuição além de `quantidade_maxima_contribuintes`; bloquear segunda contribuição do mesmo convidado no mesmo presente
- Playlist: bloquear segundo voto do mesmo convidado na mesma sugestão
- Curtida: bloquear segunda curtida do mesmo usuário na mesma postagem
- Ao cadastrar um `Convidado`: criar `Usuario` (perfil `convidado`, sem senha) + `token_confirmacao` único e não previsível, automaticamente

## Fora de escopo (não implementar)

Gateway de pagamento real; envio automatizado de convites físicos; app mobile nativo; gestão financeira/orçamentária completa; integração automática com redes sociais externas; integração com serviços de streaming de música (Spotify); avisos por canais externos (WhatsApp/SMS); chat/mensagens em tempo real entre usuários.

## Como rodar

```bash
# Banco
docker compose up -d db

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
pytest -v                      # roda os testes (SQLite em memória, não precisa do MySQL)
alembic revision --autogenerate -m "modelo inicial"   # ainda não foi gerado
alembic upgrade head
uvicorn app.main:app --reload  # API em http://localhost:8000/docs

# Frontend
cd frontend
npm install                    # ainda não foi rodado
npm run dev                    # http://localhost:5173
```

## O que peço ao continuar no Claude Code

Seguir a implementação a partir do módulo **Evento + Convidado**, respeitando exatamente a arquitetura em camadas, o modelo de dados e as decisões fechadas listadas acima. Reaproveitar `app/core/exceptions.py` e os handlers de `app/main.py` para os novos erros de domínio (ex.: `LimiteAcompanhantesExcedidoError`, `CapacidadeMesaExcedidaError` etc., a criar conforme necessário). Seguir o mesmo padrão de testes com SQLite em memória usado em `tests/test_usuario.py`.
