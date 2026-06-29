from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Homenagem(Base):
    """
    Texto de homenagem do evento, com ordenação cronológica explícita
    (campo `ordem`) para evitar que homenagens sejam conduzidas fora
    da sequência planejada durante a cerimônia.
    """

    __tablename__ = "homenagens"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    homenageado: Mapped[str] = mapped_column(String(150), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    autor: Mapped[str | None] = mapped_column(String(150), nullable=True)

    evento = relationship("Evento", back_populates="homenagens")


class AnotacaoCerimonial(Base):
    """
    Anotação da cerimonialista para um momento da cerimônia.
    `nomes_envolvidos` é texto livre para registrar nomes formais de
    pais/padrinhos relevantes ao momento (substitui a entidade
    PaiPadrinho, removida do modelo).
    """

    __tablename__ = "anotacoes_cerimoniais"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    momento_cerimonia: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    nomes_envolvidos: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)

    evento = relationship("Evento", back_populates="anotacoes_cerimoniais")
