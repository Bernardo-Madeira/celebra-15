from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import DestinatarioAviso


class Aviso(Base):
    """
    Aviso unidirecional do organizador para a equipe envolvida na organização.
    Sem opção de destinatário "fornecedores" — apenas cerimonialista, equipe
    interna ou todos (conforme delimitação de escopo do Cap. 1 do TCC).
    """

    __tablename__ = "avisos"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    data_publicacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    destinatario_tipo: Mapped[DestinatarioAviso] = mapped_column(
        SAEnum(DestinatarioAviso, name="destinatario_aviso_enum"), nullable=False
    )

    evento = relationship("Evento", back_populates="avisos")
