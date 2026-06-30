from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_organizador, require_organizador_ou_cerimonialista
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.aviso import AvisoCreate, AvisoRead, AvisoUpdate
from app.services.aviso_service import (
    atualizar_aviso,
    buscar_aviso,
    criar_aviso,
    excluir_aviso,
    listar_avisos,
)
from app.services.evento_service import buscar_evento

# Rotas autenticadas aninhadas em /eventos/{evento_id}
router = APIRouter(prefix="/eventos/{evento_id}/avisos", tags=["avisos"])


@router.post("", response_model=AvisoRead, status_code=201)
def criar(
    evento_id: int,
    body: AvisoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_aviso(db, evento, body.titulo, body.mensagem, body.destinatario_tipo)


@router.get("", response_model=list[AvisoRead])
def listar(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_avisos(db, evento_id)


@router.get("/{aviso_id}", response_model=AvisoRead)
def obter(
    evento_id: int,
    aviso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_aviso(db, aviso_id, evento_id)


@router.patch("/{aviso_id}", response_model=AvisoRead)
def atualizar(
    evento_id: int,
    aviso_id: int,
    body: AvisoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    aviso = buscar_aviso(db, aviso_id, evento_id)
    return atualizar_aviso(db, aviso, body.titulo, body.mensagem, body.destinatario_tipo)


@router.delete("/{aviso_id}", status_code=204)
def excluir(
    evento_id: int,
    aviso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    aviso = buscar_aviso(db, aviso_id, evento_id)
    excluir_aviso(db, aviso)
