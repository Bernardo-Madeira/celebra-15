from sqlalchemy.orm import Session

from app.core.exceptions import (
    AcompanhanteNaoEncontradoError,
    ConvidadoNaoEncontradoError,
    EmailJaCadastradoError,
    LimiteAcompanhantesExcedidoError,
    MesaLotadaError,
    MesaNaoEncontradaError,
)
from app.core.tokens import gerar_token_confirmacao
from app.models.convidado import Acompanhante, Convidado, Mesa
from app.models.enums import StatusConfirmacao, TipoPerfil
from app.models.evento import Evento
from app.models.usuario import Usuario


# ---------------------------------------------------------------------------
# Convidados
# ---------------------------------------------------------------------------

def cadastrar_convidado(
    db: Session, evento: Evento, nome: str, email: str, telefone: str
) -> Convidado:
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise EmailJaCadastradoError()

    usuario = Usuario(nome=nome, email=email, senha_hash=None, tipo_perfil=TipoPerfil.CONVIDADO)
    db.add(usuario)
    db.flush()

    convidado = Convidado(
        evento_id=evento.id,
        usuario_id=usuario.id,
        nome=nome,
        telefone=telefone,
        token_confirmacao=gerar_token_confirmacao(),
        status_confirmacao=StatusConfirmacao.PENDENTE,
    )
    db.add(convidado)
    db.commit()
    db.refresh(convidado)
    return convidado


def listar_convidados(db: Session, evento_id: int) -> list[Convidado]:
    return (
        db.query(Convidado)
        .filter(Convidado.evento_id == evento_id)
        .order_by(Convidado.nome)
        .all()
    )


def buscar_convidado(db: Session, convidado_id: int, evento_id: int) -> Convidado:
    convidado = (
        db.query(Convidado)
        .filter(Convidado.id == convidado_id, Convidado.evento_id == evento_id)
        .first()
    )
    if convidado is None:
        raise ConvidadoNaoEncontradoError()
    return convidado


def atualizar_convidado(
    db: Session,
    convidado: Convidado,
    nome: str | None = None,
    telefone: str | None = None,
    mesa_id: int | None = None,
) -> Convidado:
    if nome is not None:
        convidado.nome = nome
        convidado.usuario.nome = nome

    if telefone is not None:
        convidado.telefone = telefone

    if mesa_id is not None:
        mesa = db.get(Mesa, mesa_id)
        if mesa is None or mesa.evento_id != convidado.evento_id:
            raise MesaNaoEncontradaError()
        ocupados = (
            db.query(Convidado).filter(Convidado.mesa_id == mesa_id).count()
        )
        if ocupados >= mesa.capacidade:
            raise MesaLotadaError()
        convidado.mesa_id = mesa_id

    db.commit()
    db.refresh(convidado)
    return convidado


def excluir_convidado(db: Session, convidado: Convidado) -> None:
    usuario = convidado.usuario
    db.delete(convidado)
    db.flush()
    db.delete(usuario)
    db.commit()


def confirmar_presenca(
    db: Session,
    token: str,
    status: StatusConfirmacao,
    nomes_acompanhantes: list[str],
) -> Convidado:
    convidado = (
        db.query(Convidado).filter(Convidado.token_confirmacao == token).first()
    )
    if convidado is None:
        raise ConvidadoNaoEncontradoError()

    max_ac = convidado.evento.max_acompanhantes_por_convidado
    if len(nomes_acompanhantes) > max_ac:
        raise LimiteAcompanhantesExcedidoError()

    convidado.status_confirmacao = status

    for ac in list(convidado.acompanhantes):
        db.delete(ac)
    db.flush()

    for nome in nomes_acompanhantes:
        db.add(Acompanhante(convidado_id=convidado.id, nome=nome))

    db.commit()
    db.refresh(convidado)
    return convidado


# ---------------------------------------------------------------------------
# Acompanhantes (gestão administrativa, pelo organizador)
# ---------------------------------------------------------------------------

def adicionar_acompanhante(db: Session, convidado: Convidado, nome: str) -> Acompanhante:
    max_ac = convidado.evento.max_acompanhantes_por_convidado
    total_atual = (
        db.query(Acompanhante).filter(Acompanhante.convidado_id == convidado.id).count()
    )
    if total_atual >= max_ac:
        raise LimiteAcompanhantesExcedidoError()

    acompanhante = Acompanhante(convidado_id=convidado.id, nome=nome)
    db.add(acompanhante)
    db.commit()
    db.refresh(acompanhante)
    return acompanhante


def listar_acompanhantes(db: Session, convidado_id: int) -> list[Acompanhante]:
    return (
        db.query(Acompanhante)
        .filter(Acompanhante.convidado_id == convidado_id)
        .order_by(Acompanhante.nome)
        .all()
    )


def buscar_acompanhante(db: Session, acompanhante_id: int, convidado_id: int) -> Acompanhante:
    acompanhante = (
        db.query(Acompanhante)
        .filter(Acompanhante.id == acompanhante_id, Acompanhante.convidado_id == convidado_id)
        .first()
    )
    if acompanhante is None:
        raise AcompanhanteNaoEncontradoError()
    return acompanhante


def atualizar_acompanhante(db: Session, acompanhante: Acompanhante, nome: str | None = None) -> Acompanhante:
    if nome is not None:
        acompanhante.nome = nome
    db.commit()
    db.refresh(acompanhante)
    return acompanhante


def excluir_acompanhante(db: Session, acompanhante: Acompanhante) -> None:
    db.delete(acompanhante)
    db.commit()


# ---------------------------------------------------------------------------
# Mesas
# ---------------------------------------------------------------------------

def criar_mesa(db: Session, evento: Evento, numero: int, capacidade: int) -> Mesa:
    mesa = Mesa(evento_id=evento.id, numero=numero, capacidade=capacidade)
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return mesa


def listar_mesas(db: Session, evento_id: int) -> list[Mesa]:
    return (
        db.query(Mesa)
        .filter(Mesa.evento_id == evento_id)
        .order_by(Mesa.numero)
        .all()
    )


def buscar_mesa(db: Session, mesa_id: int, evento_id: int) -> Mesa:
    mesa = (
        db.query(Mesa)
        .filter(Mesa.id == mesa_id, Mesa.evento_id == evento_id)
        .first()
    )
    if mesa is None:
        raise MesaNaoEncontradaError()
    return mesa


def atualizar_mesa(
    db: Session, mesa: Mesa, numero: int | None = None, capacidade: int | None = None
) -> Mesa:
    if numero is not None:
        mesa.numero = numero
    if capacidade is not None:
        mesa.capacidade = capacidade
    db.commit()
    db.refresh(mesa)
    return mesa


def excluir_mesa(db: Session, mesa: Mesa) -> None:
    db.delete(mesa)
    db.commit()
