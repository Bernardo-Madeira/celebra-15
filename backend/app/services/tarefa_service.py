from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import TarefaNaoEncontradoError
from app.models.enums import StatusTarefa
from app.models.evento import Evento
from app.models.tarefa import Tarefa


def criar_tarefa(
    db: Session,
    evento: Evento,
    titulo: str,
    descricao: str | None,
    data_prazo: date,
    responsavel: str,
    status: StatusTarefa,
) -> Tarefa:
    tarefa = Tarefa(
        evento_id=evento.id,
        titulo=titulo,
        descricao=descricao,
        data_prazo=data_prazo,
        responsavel=responsavel,
        status=status,
    )
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


def listar_tarefas(db: Session, evento_id: int) -> list[Tarefa]:
    return (
        db.query(Tarefa)
        .filter(Tarefa.evento_id == evento_id)
        .order_by(Tarefa.data_prazo)
        .all()
    )


def buscar_tarefa(db: Session, tarefa_id: int, evento_id: int) -> Tarefa:
    tarefa = (
        db.query(Tarefa)
        .filter(Tarefa.id == tarefa_id, Tarefa.evento_id == evento_id)
        .first()
    )
    if tarefa is None:
        raise TarefaNaoEncontradoError()
    return tarefa


def atualizar_tarefa(
    db: Session,
    tarefa: Tarefa,
    titulo: str | None = None,
    descricao: str | None = None,
    data_prazo: date | None = None,
    responsavel: str | None = None,
    status: StatusTarefa | None = None,
) -> Tarefa:
    if titulo is not None:
        tarefa.titulo = titulo
    if descricao is not None:
        tarefa.descricao = descricao
    if data_prazo is not None:
        tarefa.data_prazo = data_prazo
    if responsavel is not None:
        tarefa.responsavel = responsavel
    if status is not None:
        tarefa.status = status
    db.commit()
    db.refresh(tarefa)
    return tarefa


def excluir_tarefa(db: Session, tarefa: Tarefa) -> None:
    db.delete(tarefa)
    db.commit()
