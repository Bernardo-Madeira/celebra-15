from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_usuario, require_organizador
from app.db.database import get_db
from app.models.enums import TipoPerfil
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate
from app.services.usuario_service import (
    atualizar_usuario,
    buscar_cerimonialista,
    cadastrar_usuario,
    excluir_cerimonialista,
    listar_cerimonialistas,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/organizador", response_model=UsuarioRead, status_code=201)
def criar_organizador(body: UsuarioCreate, db: Session = Depends(get_db)):
    return cadastrar_usuario(db, body.nome, body.email, body.senha, TipoPerfil.ORGANIZADOR)


@router.post("/cerimonialista", response_model=UsuarioRead, status_code=201)
def criar_cerimonialista(
    body: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_organizador),
):
    return cadastrar_usuario(db, body.nome, body.email, body.senha, TipoPerfil.CERIMONIALISTA)


@router.get("/me", response_model=UsuarioRead)
def me(usuario: Usuario = Depends(get_current_usuario)):
    return usuario


@router.patch("/me", response_model=UsuarioRead)
def atualizar_me(
    body: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    return atualizar_usuario(db, usuario, body.nome, body.senha)


@router.get("/cerimonialistas", response_model=list[UsuarioRead])
def listar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_organizador),
):
    return listar_cerimonialistas(db)


@router.get("/cerimonialistas/{usuario_id}", response_model=UsuarioRead)
def obter_cerimonialista(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_organizador),
):
    return buscar_cerimonialista(db, usuario_id)


@router.patch("/cerimonialistas/{usuario_id}", response_model=UsuarioRead)
def atualizar_cerimonialista(
    usuario_id: int,
    body: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_organizador),
):
    cerimonialista = buscar_cerimonialista(db, usuario_id)
    return atualizar_usuario(db, cerimonialista, body.nome, body.senha)


@router.delete("/cerimonialistas/{usuario_id}", status_code=204)
def remover_cerimonialista(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_organizador),
):
    excluir_cerimonialista(db, usuario_id)
