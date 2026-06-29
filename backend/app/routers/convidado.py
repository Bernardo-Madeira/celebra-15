from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import (
    require_organizador,
    require_organizador_ou_cerimonialista,
)
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.convidado import (
    ConfirmarPresencaBody,
    ConvidadoCreate,
    ConvidadoRead,
    ConvidadoUpdate,
    MesaCreate,
    MesaRead,
    MesaUpdate,
)
from app.services.convidado_service import (
    atualizar_convidado,
    atualizar_mesa,
    buscar_convidado,
    buscar_mesa,
    cadastrar_convidado,
    confirmar_presenca,
    criar_mesa,
    excluir_convidado,
    excluir_mesa,
    listar_convidados,
    listar_mesas,
)
from app.services.evento_service import buscar_evento

# Rotas autenticadas aninhadas em /eventos/{evento_id}
router = APIRouter(prefix="/eventos/{evento_id}", tags=["convidados"])

# Rota pública de confirmação de presença
confirmacao_router = APIRouter(prefix="/convidados", tags=["confirmação de presença"])


# ---------------------------------------------------------------------------
# Convidados
# ---------------------------------------------------------------------------

@router.post("/convidados", response_model=ConvidadoRead, status_code=201)
def criar_convidado(
    evento_id: int,
    body: ConvidadoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return cadastrar_convidado(db, evento, body.nome, body.email, body.telefone)


@router.get("/convidados", response_model=list[ConvidadoRead])
def listar_convidados_route(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_convidados(db, evento_id)


@router.get("/convidados/{convidado_id}", response_model=ConvidadoRead)
def obter_convidado(
    evento_id: int,
    convidado_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_convidado(db, convidado_id, evento_id)


@router.patch("/convidados/{convidado_id}", response_model=ConvidadoRead)
def atualizar_convidado_route(
    evento_id: int,
    convidado_id: int,
    body: ConvidadoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    convidado = buscar_convidado(db, convidado_id, evento_id)
    return atualizar_convidado(db, convidado, body.nome, body.telefone, body.mesa_id)


@router.delete("/convidados/{convidado_id}", status_code=204)
def excluir_convidado_route(
    evento_id: int,
    convidado_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    convidado = buscar_convidado(db, convidado_id, evento_id)
    excluir_convidado(db, convidado)


# ---------------------------------------------------------------------------
# Mesas
# ---------------------------------------------------------------------------

@router.post("/mesas", response_model=MesaRead, status_code=201)
def criar_mesa_route(
    evento_id: int,
    body: MesaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_mesa(db, evento, body.numero, body.capacidade)


@router.get("/mesas", response_model=list[MesaRead])
def listar_mesas_route(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_mesas(db, evento_id)


@router.get("/mesas/{mesa_id}", response_model=MesaRead)
def obter_mesa(
    evento_id: int,
    mesa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_mesa(db, mesa_id, evento_id)


@router.patch("/mesas/{mesa_id}", response_model=MesaRead)
def atualizar_mesa_route(
    evento_id: int,
    mesa_id: int,
    body: MesaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    mesa = buscar_mesa(db, mesa_id, evento_id)
    return atualizar_mesa(db, mesa, body.numero, body.capacidade)


@router.delete("/mesas/{mesa_id}", status_code=204)
def excluir_mesa_route(
    evento_id: int,
    mesa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    mesa = buscar_mesa(db, mesa_id, evento_id)
    excluir_mesa(db, mesa)


# ---------------------------------------------------------------------------
# Confirmação de presença (pública — sem autenticação)
# ---------------------------------------------------------------------------

@confirmacao_router.patch("/confirmar/{token}", response_model=ConvidadoRead)
def confirmar(
    token: str,
    body: ConfirmarPresencaBody,
    db: Session = Depends(get_db),
):
    return confirmar_presenca(db, token, body.status_confirmacao, body.acompanhantes)
