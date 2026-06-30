from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_organizador, require_organizador_ou_cerimonialista
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.presente import PresenteCreate, PresenteRead, PresenteUpdate, ReservaPresenteRead
from app.services.evento_service import buscar_evento
from app.services.presente_service import (
    atualizar_presente,
    buscar_presente,
    cancelar_reserva,
    criar_presente,
    excluir_presente,
    listar_presentes,
    listar_presentes_do_convidado,
    reservar_presente,
)

# Rotas autenticadas aninhadas em /eventos/{evento_id}
router = APIRouter(prefix="/eventos/{evento_id}/presentes", tags=["presentes"])

# Rotas públicas de reserva (acesso via token_confirmacao do convidado)
reserva_router = APIRouter(prefix="/presentes", tags=["presentes - reserva pública"])


# ---------------------------------------------------------------------------
# Presentes (CRUD autenticado)
# ---------------------------------------------------------------------------

@router.post("", response_model=PresenteRead, status_code=201)
def criar(
    evento_id: int,
    body: PresenteCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_presente(
        db,
        evento,
        body.nome,
        body.descricao,
        body.link_loja,
        body.quantidade_maxima_contribuintes,
    )


@router.get("", response_model=list[PresenteRead])
def listar(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_presentes(db, evento_id)


@router.get("/{presente_id}", response_model=PresenteRead)
def obter(
    evento_id: int,
    presente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_presente(db, presente_id, evento_id)


@router.patch("/{presente_id}", response_model=PresenteRead)
def atualizar(
    evento_id: int,
    presente_id: int,
    body: PresenteUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    presente = buscar_presente(db, presente_id, evento_id)
    return atualizar_presente(
        db,
        presente,
        body.nome,
        body.descricao,
        body.link_loja,
        body.quantidade_maxima_contribuintes,
    )


@router.delete("/{presente_id}", status_code=204)
def excluir(
    evento_id: int,
    presente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    presente = buscar_presente(db, presente_id, evento_id)
    excluir_presente(db, presente)


# ---------------------------------------------------------------------------
# Reserva de presentes (pública — sem autenticação, via token_confirmacao)
# ---------------------------------------------------------------------------

@reserva_router.get("/lista/{token}", response_model=list[PresenteRead])
def listar_publico(
    token: str,
    db: Session = Depends(get_db),
):
    return listar_presentes_do_convidado(db, token)


@reserva_router.post("/reservar/{token}/{presente_id}", response_model=ReservaPresenteRead, status_code=201)
def reservar(
    token: str,
    presente_id: int,
    db: Session = Depends(get_db),
):
    return reservar_presente(db, token, presente_id)


@reserva_router.delete("/reservar/{token}/{presente_id}", status_code=204)
def cancelar(
    token: str,
    presente_id: int,
    db: Session = Depends(get_db),
):
    cancelar_reserva(db, token, presente_id)
