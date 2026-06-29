from datetime import date

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import StatusPagamento, TipoServicoFornecedor


class Fornecedor(Base):
    """Fornecedor contratado para o evento (buffet, decoração, fotografia etc.)."""

    __tablename__ = "fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo_servico: Mapped[TipoServicoFornecedor] = mapped_column(
        SAEnum(TipoServicoFornecedor, name="tipo_servico_fornecedor_enum"), nullable=False
    )
    contato_telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    contato_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    evento = relationship("Evento", back_populates="fornecedores")
    pagamentos = relationship("Pagamento", back_populates="fornecedor", cascade="all, delete-orphan")


class Pagamento(Base):
    """Controle simplificado de pagamento a um Fornecedor (valor total, sinal e prazos)."""

    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    fornecedor_id: Mapped[int] = mapped_column(ForeignKey("fornecedores.id"), nullable=False)
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valor_sinal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    data_sinal: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_vencimento_saldo: Mapped[date] = mapped_column(Date, nullable=False)
    status_pagamento: Mapped[StatusPagamento] = mapped_column(
        SAEnum(StatusPagamento, name="status_pagamento_enum"),
        nullable=False,
        default=StatusPagamento.PENDENTE,
    )

    fornecedor = relationship("Fornecedor", back_populates="pagamentos")
