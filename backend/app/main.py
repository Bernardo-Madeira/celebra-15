from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health

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

app.include_router(health.router)

# Próximos routers a registrar aqui conforme implementados:
# eventos, convidados, mesas, presentes, fornecedores, pagamentos,
# tarefas, homenagens, anotacoes_cerimoniais, musicas, avisos,
# albuns, fotos, postagens, comentarios, curtidas, auth


@app.get("/")
def root():
    return {"message": "celebra-15 API — ver /docs para a documentação interativa."}
