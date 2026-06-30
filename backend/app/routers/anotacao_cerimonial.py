from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_organizador_ou_cerimonialista
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.anotacao_cerimonial import (
    AnotacaoCerimonialCreate,
    AnotacaoCerimonialRead,
    AnotacaoCerimonialUpdate,
)
from app.services.anotacao_cerimonial_service import (
    atualizar_anotacao_cerimonial,
    buscar_anotacao_cerimonial,
    criar_anotacao_cerimonial,
    excluir_anotacao_cerimonial,
    listar_anotacoes_cerimoniais,
)
from app.services.evento_service import buscar_evento

# Rotas autenticadas aninhadas em /eventos/{evento_id}
# Acesso liberado a organizador e cerimonialista em todas as operações,
# pois a anotação cerimonial é a ferramenta de trabalho da cerimonialista.
router = APIRouter(prefix="/eventos/{evento_id}/anotacoes-cerimoniais", tags=["anotacoes-cerimoniais"])


@router.post("", response_model=AnotacaoCerimonialRead, status_code=201)
def criar(
    evento_id: int,
    body: AnotacaoCerimonialCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_anotacao_cerimonial(
        db,
        evento,
        body.momento_cerimonia,
        body.descricao,
        body.nomes_envolvidos,
        body.ordem,
    )


@router.get("", response_model=list[AnotacaoCerimonialRead])
def listar(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_anotacoes_cerimoniais(db, evento_id)


@router.get("/{anotacao_id}", response_model=AnotacaoCerimonialRead)
def obter(
    evento_id: int,
    anotacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_anotacao_cerimonial(db, anotacao_id, evento_id)


@router.patch("/{anotacao_id}", response_model=AnotacaoCerimonialRead)
def atualizar(
    evento_id: int,
    anotacao_id: int,
    body: AnotacaoCerimonialUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    anotacao = buscar_anotacao_cerimonial(db, anotacao_id, evento_id)
    return atualizar_anotacao_cerimonial(
        db,
        anotacao,
        body.momento_cerimonia,
        body.descricao,
        body.nomes_envolvidos,
        body.ordem,
    )


@router.delete("/{anotacao_id}", status_code=204)
def excluir(
    evento_id: int,
    anotacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    anotacao = buscar_anotacao_cerimonial(db, anotacao_id, evento_id)
    excluir_anotacao_cerimonial(db, anotacao)
