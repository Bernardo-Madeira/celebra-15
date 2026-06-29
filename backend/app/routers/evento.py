from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_usuario,
    require_organizador,
    require_organizador_ou_cerimonialista,
)
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.evento import EventoCreate, EventoRead, EventoUpdate
from app.services.evento_service import (
    atualizar_evento,
    buscar_evento,
    criar_evento,
    excluir_evento,
    listar_eventos,
)

router = APIRouter(prefix="/eventos", tags=["eventos"])


@router.post("", response_model=EventoRead, status_code=201)
def criar(
    body: EventoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    return criar_evento(
        db,
        usuario,
        body.nome_debutante,
        body.data_evento,
        body.local,
        body.max_acompanhantes_por_convidado,
    )


@router.get("", response_model=list[EventoRead])
def listar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    return listar_eventos(db, usuario)


@router.get("/{evento_id}", response_model=EventoRead)
def obter(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    return buscar_evento(db, evento_id, usuario)


@router.patch("/{evento_id}", response_model=EventoRead)
def atualizar(
    evento_id: int,
    body: EventoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return atualizar_evento(
        db,
        evento,
        body.nome_debutante,
        body.data_evento,
        body.local,
        body.max_acompanhantes_por_convidado,
    )


@router.delete("/{evento_id}", status_code=204)
def excluir(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    excluir_evento(db, evento)
