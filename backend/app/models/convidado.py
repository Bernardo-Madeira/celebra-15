from sqlalchemy import ForeignKey, Integer, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import StatusConfirmacao


class Mesa(Base):
    """Mesa do salão. Capacidade validada na camada de service ao alocar convidados."""

    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False)

    evento = relationship("Evento", back_populates="mesas")
    convidados = relationship("Convidado", back_populates="mesa")


class Convidado(Base):
    """
    Convidado do evento. Possui um Usuario próprio (perfil 'convidado'),
    criado automaticamente no cadastro, sem senha. O acesso à confirmação
    de presença é feito via token_confirmacao (sem login).
    """

    __tablename__ = "convidados"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    token_confirmacao: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    status_confirmacao: Mapped[StatusConfirmacao] = mapped_column(
        SAEnum(StatusConfirmacao, name="status_confirmacao_enum"),
        nullable=False,
        default=StatusConfirmacao.PENDENTE,
    )
    mesa_id: Mapped[int | None] = mapped_column(ForeignKey("mesas.id"), nullable=True)

    evento = relationship("Evento", back_populates="convidados")
    usuario = relationship("Usuario", back_populates="convidado")
    mesa = relationship("Mesa", back_populates="convidados")

    acompanhantes = relationship(
        "Acompanhante", back_populates="convidado", cascade="all, delete-orphan"
    )
    reservas_presente = relationship(
        "ReservaPresente", back_populates="convidado", cascade="all, delete-orphan"
    )
    sugestoes_musicais = relationship(
        "SugestaoMusical", back_populates="convidado", cascade="all, delete-orphan"
    )
    votos_musica = relationship(
        "VotoMusica", back_populates="convidado", cascade="all, delete-orphan"
    )


class Acompanhante(Base):
    """
    Acompanhante de um Convidado. Regra de negócio (camada services):
    total de acompanhantes do convidado <= Evento.max_acompanhantes_por_convidado.
    """

    __tablename__ = "acompanhantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    convidado_id: Mapped[int] = mapped_column(ForeignKey("convidados.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)

    convidado = relationship("Convidado", back_populates="acompanhantes")
