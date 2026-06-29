from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import (
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    UsuarioNaoEncontradoError,
)
from app.routers import auth, health, usuario

app = FastAPI(
    title="celebra-15 API",
    description="API do Sistema de Gestão de Eventos de Debutantes (TCC FAETERJ).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(EmailJaCadastradoError)
async def email_ja_cadastrado_handler(request: Request, exc: EmailJaCadastradoError):
    return JSONResponse(status_code=409, content={"detail": "E-mail já cadastrado."})


@app.exception_handler(CredenciaisInvalidasError)
async def credenciais_invalidas_handler(request: Request, exc: CredenciaisInvalidasError):
    return JSONResponse(status_code=401, content={"detail": "Credenciais inválidas."})


@app.exception_handler(UsuarioNaoEncontradoError)
async def usuario_nao_encontrado_handler(request: Request, exc: UsuarioNaoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": "Usuário não encontrado."})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(usuario.router)

# Próximos routers a registrar aqui conforme implementados:
# eventos, convidados, mesas, presentes, fornecedores, pagamentos,
# tarefas, homenagens, anotacoes_cerimoniais, musicas, avisos,
# albuns, fotos, postagens, comentarios, curtidas


@app.get("/")
def root():
    return {"message": "celebra-15 API — ver /docs para a documentação interativa."}
