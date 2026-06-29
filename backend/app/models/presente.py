from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Presente(Base):
    """Item da lista de presentes, com cota máxima de contribuintes."""

    __tablename__ = "presentes"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    link_loja: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quantidade_maxima_contribuintes: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    evento = relationship("Evento", back_populates="presentes")
    reservas = relationship("ReservaPresente", back_populates="presente", cascade="all, delete-orphan")


class ReservaPresente(Base):
    """
    Contribuição de um Convidado para um Presente.
    Regras de negócio (camada services):
      - total de reservas do presente <= Presente.quantidade_maxima_contribuintes
      - 1 contribuição por convidado por presente (UniqueConstraint abaixo)
    """

    __tablename__ = "reservas_presente"
    __table_args__ = (
        UniqueConstraint("presente_id", "convidado_id", name="uq_reserva_presente_convidado"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    presente_id: Mapped[int] = mapped_column(ForeignKey("presentes.id"), nullable=False)
    convidado_id: Mapped[int] = mapped_column(ForeignKey("convidados.id"), nullable=False)
    data_reserva: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    presente = relationship("Presente", back_populates="reservas")
    convidado = relationship("Convidado", back_populates="reservas_presente")
