from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Album(Base):
    """Álbum de fotos do evento (agrupador de Foto)."""

    __tablename__ = "albuns"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)

    evento = relationship("Evento", back_populates="albuns")
    fotos = relationship("Foto", back_populates="album", cascade="all, delete-orphan")


class Foto(Base):
    """Foto pertencente a um Album."""

    __tablename__ = "fotos"

    id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albuns.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    legenda: Mapped[str | None] = mapped_column(String(255), nullable=True)

    album = relationship("Album", back_populates="fotos")


class Postagem(Base):
    """Postagem no mural do evento, feita por qualquer Usuario (organizador, convidado etc.)."""

    __tablename__ = "postagens"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    autor_usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    data_publicacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    evento = relationship("Evento", back_populates="postagens")
    autor = relationship("Usuario", back_populates="postagens")
    comentarios = relationship("Comentario", back_populates="postagem", cascade="all, delete-orphan")
    curtidas = relationship("Curtida", back_populates="postagem", cascade="all, delete-orphan")


class Comentario(Base):
    """Comentário assíncrono vinculado a uma Postagem."""

    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    postagem_id: Mapped[int] = mapped_column(ForeignKey("postagens.id"), nullable=False)
    autor_usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    postagem = relationship("Postagem", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")


class Curtida(Base):
    """
    Curtida de um Usuario em uma Postagem.
    Regra de negócio (camada services): 1 curtida por usuário por postagem
    (garantido também pela UniqueConstraint abaixo).
    """

    __tablename__ = "curtidas"
    __table_args__ = (
        UniqueConstraint("postagem_id", "usuario_id", name="uq_curtida_usuario_postagem"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    postagem_id: Mapped[int] = mapped_column(ForeignKey("postagens.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    postagem = relationship("Postagem", back_populates="curtidas")
    usuario = relationship("Usuario", back_populates="curtidas")
