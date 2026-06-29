from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Evento(Base):
    """Evento (festa de 15 anos). Raiz de quase todas as demais entidades do domínio."""

    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_debutante: Mapped[str] = mapped_column(String(150), nullable=False)
    data_evento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    local: Mapped[str] = mapped_column(String(255), nullable=False)
    max_acompanhantes_por_convidado: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    usuario_organizador_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    organizador = relationship("Usuario", back_populates="eventos_organizados")

    convidados = relationship("Convidado", back_populates="evento", cascade="all, delete-orphan")
    mesas = relationship("Mesa", back_populates="evento", cascade="all, delete-orphan")
    presentes = relationship("Presente", back_populates="evento", cascade="all, delete-orphan")
    fornecedores = relationship("Fornecedor", back_populates="evento", cascade="all, delete-orphan")
    tarefas = relationship("Tarefa", back_populates="evento", cascade="all, delete-orphan")
    homenagens = relationship("Homenagem", back_populates="evento", cascade="all, delete-orphan")
    anotacoes_cerimoniais = relationship(
        "AnotacaoCerimonial", back_populates="evento", cascade="all, delete-orphan"
    )
    sugestoes_musicais = relationship(
        "SugestaoMusical", back_populates="evento", cascade="all, delete-orphan"
    )
    avisos = relationship("Aviso", back_populates="evento", cascade="all, delete-orphan")
    albuns = relationship("Album", back_populates="evento", cascade="all, delete-orphan")
    postagens = relationship("Postagem", back_populates="evento", cascade="all, delete-orphan")
