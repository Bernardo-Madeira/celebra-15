"""
Testes do módulo de fornecedores e pagamentos (CRUD autenticado, aninhado em evento/fornecedor).
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@forn.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@forn.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@forn.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

FORNECEDOR_BASE = {
    "nome": "Buffet Sabor & Arte",
    "tipo_servico": "buffet",
    "contato_telefone": "21999990001",
    "contato_email": "contato@sabor.com",
    "observacoes": "Cardápio fechado em reunião prévia.",
}

PAGAMENTO_BASE = {
    "valor_total": 5000.0,
    "valor_sinal": 1000.0,
    "data_sinal": "2025-01-10",
    "data_vencimento_saldo": "2025-06-01",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _cadastrar_e_login(client: TestClient, usuario: dict) -> str:
    client.post("/usuarios/organizador", json=usuario)
    resp = client.post(
        "/auth/login", data={"username": usuario["email"], "password": usuario["senha"]}
    )
    return resp.json()["access_token"]


def _token_cerimonialista(client: TestClient, token_org: str) -> str:
    client.post(
        "/usuarios/cerimonialista",
        json=CERIMONIALISTA,
        headers=_auth(token_org),
    )
    resp = client.post(
        "/auth/login",
        data={"username": CERIMONIALISTA["email"], "password": CERIMONIALISTA["senha"]},
    )
    return resp.json()["access_token"]


def _criar_evento(client: TestClient, token: str, payload: dict | None = None) -> dict:
    resp = client.post("/eventos", json=payload or EVENTO_BASE, headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()


def _criar_fornecedor(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/fornecedores",
        json=payload or FORNECEDOR_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


def _criar_pagamento(
    client: TestClient,
    token: str,
    evento_id: int,
    fornecedor_id: int,
    payload: dict | None = None,
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/fornecedores/{fornecedor_id}/pagamentos",
        json=payload or PAGAMENTO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD de Fornecedores
# ---------------------------------------------------------------------------


def test_criar_fornecedor_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores", json=FORNECEDOR_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == FORNECEDOR_BASE["nome"]
    assert data["tipo_servico"] == "buffet"
    assert data["pagamentos"] == []


def test_criar_fornecedor_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/fornecedores", json=FORNECEDOR_BASE)
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_fornecedor_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores", json=FORNECEDOR_BASE, headers=_auth(token_ceri)
    )
    assert resp.status_code == 403


def test_listar_fornecedores(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_fornecedor(client, token, evento["id"])
    _criar_fornecedor(client, token, evento["id"], {**FORNECEDOR_BASE, "nome": "Decorações Top"})
    resp = client.get(f"/eventos/{evento['id']}/fornecedores", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_fornecedor_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == fornecedor["id"]


def test_obter_fornecedor_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/fornecedores/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_fornecedor(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}",
        json={"nome": "Buffet Renovado", "tipo_servico": "decoracao"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Buffet Renovado"
    assert resp.json()["tipo_servico"] == "decoracao"


def test_excluir_fornecedor(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


def test_organizador_nao_acessa_fornecedores_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/fornecedores", headers=_auth(token_a))
    assert resp.status_code == 403


def test_cerimonialista_lista_fornecedores(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_fornecedor(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/fornecedores", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ---------------------------------------------------------------------------
# CRUD de Pagamentos (aninhados em fornecedor)
# ---------------------------------------------------------------------------


def test_criar_pagamento_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        json=PAGAMENTO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["fornecedor_id"] == fornecedor["id"]
    assert data["valor_total"] == 5000.0
    assert data["status_pagamento"] == "pendente"


def test_criar_pagamento_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        json=PAGAMENTO_BASE,
    )
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_pagamento_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    fornecedor = _criar_fornecedor(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        json=PAGAMENTO_BASE,
        headers=_auth(token_ceri),
    )
    assert resp.status_code == 403


def test_criar_pagamento_valor_total_invalido_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        json={**PAGAMENTO_BASE, "valor_total": 0},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_criar_pagamento_sinal_maior_que_total_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        json={**PAGAMENTO_BASE, "valor_total": 100.0, "valor_sinal": 200.0},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_listar_pagamentos(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    _criar_pagamento(client, token, evento["id"], fornecedor["id"])
    _criar_pagamento(
        client,
        token,
        evento["id"],
        fornecedor["id"],
        {**PAGAMENTO_BASE, "data_vencimento_saldo": "2025-07-01"},
    )
    resp = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_pagamento_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    pagamento = _criar_pagamento(client, token, evento["id"], fornecedor["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos/{pagamento['id']}",
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == pagamento["id"]


def test_obter_pagamento_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos/9999",
        headers=_auth(token),
    )
    assert resp.status_code == 404


def test_atualizar_pagamento(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    pagamento = _criar_pagamento(client, token, evento["id"], fornecedor["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos/{pagamento['id']}",
        json={"status_pagamento": "pago", "valor_sinal": 5000.0},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status_pagamento"] == "pago"
    assert resp.json()["valor_sinal"] == 5000.0


def test_atualizar_pagamento_sinal_maior_que_total_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    pagamento = _criar_pagamento(client, token, evento["id"], fornecedor["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos/{pagamento['id']}",
        json={"valor_sinal": 999999.0},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_excluir_pagamento(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    pagamento = _criar_pagamento(client, token, evento["id"], fornecedor["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos/{pagamento['id']}",
        headers=_auth(token),
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos/{pagamento['id']}",
        headers=_auth(token),
    )
    assert resp_get.status_code == 404


def test_excluir_fornecedor_remove_pagamentos_em_cascata(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    fornecedor = _criar_fornecedor(client, token, evento["id"])
    _criar_pagamento(client, token, evento["id"], fornecedor["id"])

    resp = client.delete(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204

    resp_get = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        headers=_auth(token),
    )
    assert resp_get.status_code == 404


def test_cerimonialista_lista_pagamentos(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    fornecedor = _criar_fornecedor(client, token_org, evento["id"])
    _criar_pagamento(client, token_org, evento["id"], fornecedor["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(
        f"/eventos/{evento['id']}/fornecedores/{fornecedor['id']}/pagamentos",
        headers=_auth(token_ceri),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
