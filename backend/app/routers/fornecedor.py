from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_organizador, require_organizador_ou_cerimonialista
from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas.fornecedor import (
    FornecedorCreate,
    FornecedorRead,
    FornecedorUpdate,
    PagamentoCreate,
    PagamentoRead,
    PagamentoUpdate,
)
from app.services.evento_service import buscar_evento
from app.services.fornecedor_service import (
    atualizar_fornecedor,
    atualizar_pagamento,
    buscar_fornecedor,
    buscar_pagamento,
    criar_fornecedor,
    criar_pagamento,
    excluir_fornecedor,
    excluir_pagamento,
    listar_fornecedores,
    listar_pagamentos,
)

# Rotas autenticadas aninhadas em /eventos/{evento_id}
router = APIRouter(prefix="/eventos/{evento_id}/fornecedores", tags=["fornecedores"])


# ---------------------------------------------------------------------------
# Fornecedores
# ---------------------------------------------------------------------------

@router.post("", response_model=FornecedorRead, status_code=201)
def criar(
    evento_id: int,
    body: FornecedorCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    evento = buscar_evento(db, evento_id, usuario)
    return criar_fornecedor(
        db,
        evento,
        body.nome,
        body.tipo_servico,
        body.contato_telefone,
        body.contato_email,
        body.observacoes,
    )


@router.get("", response_model=list[FornecedorRead])
def listar(
    evento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return listar_fornecedores(db, evento_id)


@router.get("/{fornecedor_id}", response_model=FornecedorRead)
def obter(
    evento_id: int,
    fornecedor_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    return buscar_fornecedor(db, fornecedor_id, evento_id)


@router.patch("/{fornecedor_id}", response_model=FornecedorRead)
def atualizar(
    evento_id: int,
    fornecedor_id: int,
    body: FornecedorUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    fornecedor = buscar_fornecedor(db, fornecedor_id, evento_id)
    return atualizar_fornecedor(
        db,
        fornecedor,
        body.nome,
        body.tipo_servico,
        body.contato_telefone,
        body.contato_email,
        body.observacoes,
    )


@router.delete("/{fornecedor_id}", status_code=204)
def excluir(
    evento_id: int,
    fornecedor_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    fornecedor = buscar_fornecedor(db, fornecedor_id, evento_id)
    excluir_fornecedor(db, fornecedor)


# ---------------------------------------------------------------------------
# Pagamentos (aninhados em /eventos/{evento_id}/fornecedores/{fornecedor_id})
# ---------------------------------------------------------------------------

@router.post("/{fornecedor_id}/pagamentos", response_model=PagamentoRead, status_code=201)
def criar_pagamento_route(
    evento_id: int,
    fornecedor_id: int,
    body: PagamentoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    fornecedor = buscar_fornecedor(db, fornecedor_id, evento_id)
    return criar_pagamento(
        db,
        fornecedor,
        body.valor_total,
        body.valor_sinal,
        body.data_sinal,
        body.data_vencimento_saldo,
        body.status_pagamento,
    )


@router.get("/{fornecedor_id}/pagamentos", response_model=list[PagamentoRead])
def listar_pagamentos_route(
    evento_id: int,
    fornecedor_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    buscar_fornecedor(db, fornecedor_id, evento_id)
    return listar_pagamentos(db, fornecedor_id)


@router.get("/{fornecedor_id}/pagamentos/{pagamento_id}", response_model=PagamentoRead)
def obter_pagamento(
    evento_id: int,
    fornecedor_id: int,
    pagamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador_ou_cerimonialista),
):
    buscar_evento(db, evento_id, usuario)
    buscar_fornecedor(db, fornecedor_id, evento_id)
    return buscar_pagamento(db, pagamento_id, fornecedor_id)


@router.patch("/{fornecedor_id}/pagamentos/{pagamento_id}", response_model=PagamentoRead)
def atualizar_pagamento_route(
    evento_id: int,
    fornecedor_id: int,
    pagamento_id: int,
    body: PagamentoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    buscar_fornecedor(db, fornecedor_id, evento_id)
    pagamento = buscar_pagamento(db, pagamento_id, fornecedor_id)
    return atualizar_pagamento(
        db,
        pagamento,
        body.valor_total,
        body.valor_sinal,
        body.data_sinal,
        body.data_vencimento_saldo,
        body.status_pagamento,
    )


@router.delete("/{fornecedor_id}/pagamentos/{pagamento_id}", status_code=204)
def excluir_pagamento_route(
    evento_id: int,
    fornecedor_id: int,
    pagamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_organizador),
):
    buscar_evento(db, evento_id, usuario)
    buscar_fornecedor(db, fornecedor_id, evento_id)
    pagamento = buscar_pagamento(db, pagamento_id, fornecedor_id)
    excluir_pagamento(db, pagamento)
