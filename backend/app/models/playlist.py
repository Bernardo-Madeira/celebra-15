from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Musica(Base):
    """Catálogo de músicas. Reutilizável entre sugestões de diferentes eventos."""

    __tablename__ = "musicas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    artista: Mapped[str] = mapped_column(String(150), nullable=False)

    sugestoes = relationship("SugestaoMusical", back_populates="musica")


class SugestaoMusical(Base):
    """Sugestão de uma Musica por um Convidado para a playlist colaborativa de um Evento."""

    __tablename__ = "sugestoes_musicais"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    musica_id: Mapped[int] = mapped_column(ForeignKey("musicas.id"), nullable=False)
    convidado_id: Mapped[int] = mapped_column(ForeignKey("convidados.id"), nullable=False)
    data_sugestao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    evento = relationship("Evento", back_populates="sugestoes_musicais")
    musica = relationship("Musica", back_populates="sugestoes")
    convidado = relationship("Convidado", back_populates="sugestoes_musicais")
    votos = relationship("VotoMusica", back_populates="sugestao", cascade="all, delete-orphan")


class VotoMusica(Base):
    """
    Voto de um Convidado em uma SugestaoMusical.
    Regra de negócio (camada services): 1 voto por convidado por sugestão
    (garantido também pela UniqueConstraint abaixo).
    """

    __tablename__ = "votos_musica"
    __table_args__ = (
        UniqueConstraint("sugestao_id", "convidado_id", name="uq_voto_musica_convidado"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sugestao_id: Mapped[int] = mapped_column(ForeignKey("sugestoes_musicais.id"), nullable=False)
    convidado_id: Mapped[int] = mapped_column(ForeignKey("convidados.id"), nullable=False)
    data_voto: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    sugestao = relationship("SugestaoMusical", back_populates="votos")
    convidado = relationship("Convidado", back_populates="votos_musica")
