from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import TipoPerfil


class Usuario(Base):
    """
    Entidade central de identidade. Cobre os três perfis do sistema:
    organizador e cerimonialista (login com senha) e convidado (sem senha,
    criado automaticamente ao cadastrar um Convidado — ver app.models.convidado).
    """

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo_perfil: Mapped[TipoPerfil] = mapped_column(
        SAEnum(TipoPerfil, name="tipo_perfil_enum"), nullable=False
    )
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relacionamentos reversos (definidos via back_populates nos models filhos)
    eventos_organizados = relationship("Evento", back_populates="organizador")
    convidado = relationship("Convidado", back_populates="usuario", uselist=False)
    postagens = relationship("Postagem", back_populates="autor")
    comentarios = relationship("Comentario", back_populates="autor")
    curtidas = relationship("Curtida", back_populates="usuario")
