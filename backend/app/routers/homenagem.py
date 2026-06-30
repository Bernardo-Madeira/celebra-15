from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_organizador, require_organizador_ou_cerimonialista
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.homenagem import HomenagemCreate, HomenagemRead, HomenagemUpdate
from app.services.evento_service import buscar_evento
from app.services.homenagem_service import (
    atualizar_homenagem,
    buscar_homenagem,
    criar_homenagem,
    excluir_homenagem,
    listar_homenagens,
)

# Rotas autenticadas aninhadas em /eventos/{evento_id}
router = APIRouter(prefix="/eventos/{evento_id}/homenagens", tags=["homenagens"])


@router.post("", response_model=HomenagemRead, status_code=201)
def criar(
    evento_id: int,
    body: HomenagemCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_homenagem(
        db,
        evento,
        body.homenageado,
        body.texto,
        body.ordem,
        body.autor,
    )


@router.get("", response_model=list[HomenagemRead])
def listar(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_homenagens(db, evento_id)


@router.get("/{homenagem_id}", response_model=HomenagemRead)
def obter(
    evento_id: int,
    homenagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_homenagem(db, homenagem_id, evento_id)


@router.patch("/{homenagem_id}", response_model=HomenagemRead)
def atualizar(
    evento_id: int,
    homenagem_id: int,
    body: HomenagemUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    homenagem = buscar_homenagem(db, homenagem_id, evento_id)
    return atualizar_homenagem(
        db,
        homenagem,
        body.homenageado,
        body.texto,
        body.ordem,
        body.autor,
    )


@router.delete("/{homenagem_id}", status_code=204)
def excluir(
    evento_id: int,
    homenagem_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    homenagem = buscar_homenagem(db, homenagem_id, evento_id)
    excluir_homenagem(db, homenagem)
