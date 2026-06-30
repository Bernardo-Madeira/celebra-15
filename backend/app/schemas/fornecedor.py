from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import StatusPagamento, TipoServicoFornecedor


class FornecedorCreate(BaseModel):
    nome: str
    tipo_servico: TipoServicoFornecedor
    contato_telefone: str
    contato_email: str | None = None
    observacoes: str | None = None


class FornecedorUpdate(BaseModel):
    nome: str | None = None
    tipo_servico: TipoServicoFornecedor | None = None
    contato_telefone: str | None = None
    contato_email: str | None = None
    observacoes: str | None = None


class PagamentoCreate(BaseModel):
    valor_total: float
    valor_sinal: float = 0
    data_sinal: date | None = None
    data_vencimento_saldo: date
    status_pagamento: StatusPagamento = StatusPagamento.PENDENTE

    @field_validator("valor_total")
    @classmethod
    def valor_total_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Deve ser > 0")
        return v

    @field_validator("valor_sinal")
    @classmethod
    def valor_sinal_nao_negativo(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Deve ser >= 0")
        return v


class PagamentoUpdate(BaseModel):
    valor_total: float | None = None
    valor_sinal: float | None = None
    data_sinal: date | None = None
    data_vencimento_saldo: date | None = None
    status_pagamento: StatusPagamento | None = None

    @field_validator("valor_total")
    @classmethod
    def valor_total_positivo(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Deve ser > 0")
        return v

    @field_validator("valor_sinal")
    @classmethod
    def valor_sinal_nao_negativo(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Deve ser >= 0")
        return v


class PagamentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fornecedor_id: int
    valor_total: float
    valor_sinal: float
    data_sinal: date | None
    data_vencimento_saldo: date
    status_pagamento: StatusPagamento


class FornecedorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evento_id: int
    nome: str
    tipo_servico: TipoServicoFornecedor
    contato_telefone: str
    contato_email: str | None
    observacoes: str | None
    pagamentos: list[PagamentoRead] = []
