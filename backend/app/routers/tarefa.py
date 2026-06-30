from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_organizador, require_organizador_ou_cerimonialista
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.tarefa import TarefaCreate, TarefaRead, TarefaUpdate
from app.services.evento_service import buscar_evento
from app.services.tarefa_service import (
    atualizar_tarefa,
    buscar_tarefa,
    criar_tarefa,
    excluir_tarefa,
    listar_tarefas,
)

# Rotas autenticadas aninhadas em /eventos/{evento_id}
router = APIRouter(prefix="/eventos/{evento_id}/tarefas", tags=["tarefas"])


@router.post("", response_model=TarefaRead, status_code=201)
def criar(
    evento_id: int,
    body: TarefaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_tarefa(
        db,
        evento,
        body.titulo,
        body.descricao,
        body.data_prazo,
        body.responsavel,
        body.status,
    )


@router.get("", response_model=list[TarefaRead])
def listar(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_tarefas(db, evento_id)


@router.get("/{tarefa_id}", response_model=TarefaRead)
def obter(
    evento_id: int,
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_tarefa(db, tarefa_id, evento_id)


@router.patch("/{tarefa_id}", response_model=TarefaRead)
def atualizar(
    evento_id: int,
    tarefa_id: int,
    body: TarefaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    tarefa = buscar_tarefa(db, tarefa_id, evento_id)
    return atualizar_tarefa(
        db,
        tarefa,
        body.titulo,
        body.descricao,
        body.data_prazo,
        body.responsavel,
        body.status,
    )


@router.delete("/{tarefa_id}", status_code=204)
def excluir(
    evento_id: int,
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    tarefa = buscar_tarefa(db, tarefa_id, evento_id)
    excluir_tarefa(db, tarefa)
