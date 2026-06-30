from sqlalchemy.orm import Session

from app.core.exceptions import AnotacaoCerimonialNaoEncontradaError
from app.models.cerimonial import AnotacaoCerimonial
from app.models.evento import Evento


def criar_anotacao_cerimonial(
    db: Session,
    evento: Evento,
    momento_cerimonia: str,
    descricao: str,
    nomes_envolvidos: str | None,
    ordem: int,
) -> AnotacaoCerimonial:
    anotacao = AnotacaoCerimonial(
        evento_id=evento.id,
        momento_cerimonia=momento_cerimonia,
        descricao=descricao,
        nomes_envolvidos=nomes_envolvidos,
        ordem=ordem,
    )
    db.add(anotacao)
    db.commit()
    db.refresh(anotacao)
    return anotacao


def listar_anotacoes_cerimoniais(db: Session, evento_id: int) -> list[AnotacaoCerimonial]:
    return (
        db.query(AnotacaoCerimonial)
        .filter(AnotacaoCerimonial.evento_id == evento_id)
        .order_by(AnotacaoCerimonial.ordem)
        .all()
    )


def buscar_anotacao_cerimonial(
    db: Session, anotacao_id: int, evento_id: int
) -> AnotacaoCerimonial:
    anotacao = (
        db.query(AnotacaoCerimonial)
        .filter(AnotacaoCerimonial.id == anotacao_id, AnotacaoCerimonial.evento_id == evento_id)
        .first()
    )
    if anotacao is None:
        raise AnotacaoCerimonialNaoEncontradaError()
    return anotacao


def atualizar_anotacao_cerimonial(
    db: Session,
    anotacao: AnotacaoCerimonial,
    momento_cerimonia: str | None = None,
    descricao: str | None = None,
    nomes_envolvidos: str | None = None,
    ordem: int | None = None,
) -> AnotacaoCerimonial:
    if momento_cerimonia is not None:
        anotacao.momento_cerimonia = momento_cerimonia
    if descricao is not None:
        anotacao.descricao = descricao
    if nomes_envolvidos is not None:
        anotacao.nomes_envolvidos = nomes_envolvidos
    if ordem is not None:
        anotacao.ordem = ordem
    db.commit()
    db.refresh(anotacao)
    return anotacao


def excluir_anotacao_cerimonial(db: Session, anotacao: AnotacaoCerimonial) -> None:
    db.delete(anotacao)
    db.commit()
