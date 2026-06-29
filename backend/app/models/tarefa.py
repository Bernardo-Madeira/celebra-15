from datetime import date

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import StatusTarefa


class Tarefa(Base):
    """Item do cronograma/planejamento do evento."""

    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_prazo: Mapped[date] = mapped_column(Date, nullable=False)
    responsavel: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[StatusTarefa] = mapped_column(
        SAEnum(StatusTarefa, name="status_tarefa_enum"),
        nullable=False,
        default=StatusTarefa.PENDENTE,
    )

    evento = relationship("Evento", back_populates="tarefas")
