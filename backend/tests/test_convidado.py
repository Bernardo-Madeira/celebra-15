"""
Testes do módulo de convidados: CRUD, mesas e confirmação de presença.
"""

import pytest
from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@conv.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@conv.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@conv.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

CONVIDADO_BASE = {
    "nome": "Pedro Convidado",
    "email": "pedro@conv.com",
    "telefone": "21999990001",
}

MESA_BASE = {"numero": 1, "capacidade": 6}


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


def _criar_convidado(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/convidados",
        json=payload or CONVIDADO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


def _criar_mesa(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/mesas",
        json=payload or MESA_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


def _criar_acompanhante(
    client: TestClient, token: str, evento_id: int, convidado_id: int, nome: str = "Maria"
):
    return client.post(
        f"/eventos/{evento_id}/convidados/{convidado_id}/acompanhantes",
        json={"nome": nome},
        headers=_auth(token),
    )


# ---------------------------------------------------------------------------
# CRUD de Convidados
# ---------------------------------------------------------------------------


def test_criar_convidado_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/convidados",
        json=CONVIDADO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == CONVIDADO_BASE["nome"]
    assert data["telefone"] == CONVIDADO_BASE["telefone"]
    assert data["status_confirmacao"] == "pendente"
    assert "token_confirmacao" in data
    assert data["acompanhantes"] == []


def test_criar_convidado_email_duplicado_retorna_409(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_convidado(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/convidados",
        json=CONVIDADO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 409


def test_criar_convidado_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/convidados", json=CONVIDADO_BASE)
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_convidado_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/convidados",
        json=CONVIDADO_BASE,
        headers=_auth(token_ceri),
    )
    assert resp.status_code == 403


def test_listar_convidados(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_convidado(client, token, evento["id"])
    _criar_convidado(client, token, evento["id"], {**CONVIDADO_BASE, "email": "outro@conv.com", "nome": "Ana"})
    resp = client.get(f"/eventos/{evento['id']}/convidados", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_convidado_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == convidado["id"]


def test_obter_convidado_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/convidados/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_convidado(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}",
        json={"nome": "Pedro Atualizado", "telefone": "21888880001"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Pedro Atualizado"
    assert resp.json()["telefone"] == "21888880001"


def test_excluir_convidado(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


# ---------------------------------------------------------------------------
# CRUD de Acompanhantes (administrativo, pelo organizador)
# ---------------------------------------------------------------------------


def test_criar_acompanhante_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    resp = _criar_acompanhante(client, token, evento["id"], convidado["id"], "Maria")
    assert resp.status_code == 201
    assert resp.json()["nome"] == "Maria"
    assert resp.json()["convidado_id"] == convidado["id"]


def test_criar_acompanhante_excede_limite_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token, {**EVENTO_BASE, "max_acompanhantes_por_convidado": 1})
    convidado = _criar_convidado(client, token, evento["id"])
    _criar_acompanhante(client, token, evento["id"], convidado["id"], "Maria")
    resp = _criar_acompanhante(client, token, evento["id"], convidado["id"], "João")
    assert resp.status_code == 422


def test_criar_acompanhante_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    resp = client.post(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes",
        json={"nome": "Maria"},
    )
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_acompanhante_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    convidado = _criar_convidado(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)
    resp = _criar_acompanhante(client, token_ceri, evento["id"], convidado["id"], "Maria")
    assert resp.status_code == 403


def test_listar_acompanhantes(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    _criar_acompanhante(client, token, evento["id"], convidado["id"], "Maria")
    _criar_acompanhante(client, token, evento["id"], convidado["id"], "João")
    resp = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes",
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_acompanhante_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    acompanhante = _criar_acompanhante(client, token, evento["id"], convidado["id"]).json()
    resp = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes/{acompanhante['id']}",
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == acompanhante["id"]


def test_obter_acompanhante_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes/9999",
        headers=_auth(token),
    )
    assert resp.status_code == 404


def test_atualizar_acompanhante(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    acompanhante = _criar_acompanhante(client, token, evento["id"], convidado["id"]).json()
    resp = client.patch(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes/{acompanhante['id']}",
        json={"nome": "Maria Atualizada"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Maria Atualizada"


def test_excluir_acompanhante(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    acompanhante = _criar_acompanhante(client, token, evento["id"], convidado["id"]).json()
    resp = client.delete(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes/{acompanhante['id']}",
        headers=_auth(token),
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes/{acompanhante['id']}",
        headers=_auth(token),
    )
    assert resp_get.status_code == 404


def test_cerimonialista_lista_acompanhantes(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    convidado = _criar_convidado(client, token_org, evento["id"])
    _criar_acompanhante(client, token_org, evento["id"], convidado["id"])
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.get(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}/acompanhantes",
        headers=_auth(token_ceri),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ---------------------------------------------------------------------------
# Confirmação de presença (pública)
# ---------------------------------------------------------------------------


def test_confirmar_presenca_confirmado(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    token_conf = convidado["token_confirmacao"]

    resp = client.patch(
        f"/convidados/confirmar/{token_conf}",
        json={"status_confirmacao": "confirmado", "acompanhantes": []},
    )
    assert resp.status_code == 200
    assert resp.json()["status_confirmacao"] == "confirmado"


def test_confirmar_presenca_recusado(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.patch(
        f"/convidados/confirmar/{convidado['token_confirmacao']}",
        json={"status_confirmacao": "recusado", "acompanhantes": []},
    )
    assert resp.status_code == 200
    assert resp.json()["status_confirmacao"] == "recusado"


def test_confirmar_presenca_com_acompanhantes(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.patch(
        f"/convidados/confirmar/{convidado['token_confirmacao']}",
        json={"status_confirmacao": "confirmado", "acompanhantes": ["Maria", "João"]},
    )
    assert resp.status_code == 200
    nomes = [ac["nome"] for ac in resp.json()["acompanhantes"]]
    assert "Maria" in nomes
    assert "João" in nomes


def test_confirmar_presenca_excede_limite_de_acompanhantes_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    # evento com máximo 1 acompanhante
    evento = _criar_evento(client, token, {**EVENTO_BASE, "max_acompanhantes_por_convidado": 1})
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.patch(
        f"/convidados/confirmar/{convidado['token_confirmacao']}",
        json={"status_confirmacao": "confirmado", "acompanhantes": ["Maria", "João"]},
    )
    assert resp.status_code == 422


def test_confirmar_presenca_token_invalido_retorna_404(client):
    resp = client.patch(
        "/convidados/confirmar/token-falso",
        json={"status_confirmacao": "confirmado", "acompanhantes": []},
    )
    assert resp.status_code == 404


def test_reconfirmar_presenca_atualiza_acompanhantes(client):
    """Segunda confirmação substitui acompanhantes anteriores."""
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])
    tok = convidado["token_confirmacao"]

    client.patch(
        f"/convidados/confirmar/{tok}",
        json={"status_confirmacao": "confirmado", "acompanhantes": ["Maria"]},
    )
    resp2 = client.patch(
        f"/convidados/confirmar/{tok}",
        json={"status_confirmacao": "confirmado", "acompanhantes": ["João"]},
    )
    assert resp2.status_code == 200
    nomes = [ac["nome"] for ac in resp2.json()["acompanhantes"]]
    assert nomes == ["João"]


# ---------------------------------------------------------------------------
# CRUD de Mesas
# ---------------------------------------------------------------------------


def test_criar_mesa_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/mesas", json=MESA_BASE, headers=_auth(token))
    assert resp.status_code == 201
    assert resp.json()["numero"] == 1
    assert resp.json()["capacidade"] == 6


def test_criar_mesa_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/mesas", json=MESA_BASE)
    assert resp.status_code == 401


def test_listar_mesas(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_mesa(client, token, evento["id"])
    _criar_mesa(client, token, evento["id"], {"numero": 2, "capacidade": 4})
    resp = client.get(f"/eventos/{evento['id']}/mesas", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_mesa_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    mesa = _criar_mesa(client, token, evento["id"])
    resp = client.get(f"/eventos/{evento['id']}/mesas/{mesa['id']}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == mesa["id"]


def test_obter_mesa_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/mesas/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_mesa(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    mesa = _criar_mesa(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/mesas/{mesa['id']}",
        json={"capacidade": 10},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["capacidade"] == 10


def test_excluir_mesa(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    mesa = _criar_mesa(client, token, evento["id"])
    resp = client.delete(f"/eventos/{evento['id']}/mesas/{mesa['id']}", headers=_auth(token))
    assert resp.status_code == 204
    resp_get = client.get(f"/eventos/{evento['id']}/mesas/{mesa['id']}", headers=_auth(token))
    assert resp_get.status_code == 404


# ---------------------------------------------------------------------------
# Alocar convidado em mesa
# ---------------------------------------------------------------------------


def test_alocar_convidado_em_mesa(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    mesa = _criar_mesa(client, token, evento["id"])
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.patch(
        f"/eventos/{evento['id']}/convidados/{convidado['id']}",
        json={"mesa_id": mesa["id"]},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["mesa_id"] == mesa["id"]


def test_alocar_convidado_mesa_lotada_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    mesa = _criar_mesa(client, token, evento["id"], {"numero": 1, "capacidade": 1})

    # Primeiro convidado ocupa a mesa
    conv1 = _criar_convidado(client, token, evento["id"])
    client.patch(
        f"/eventos/{evento['id']}/convidados/{conv1['id']}",
        json={"mesa_id": mesa["id"]},
        headers=_auth(token),
    )

    # Segundo convidado tenta entrar na mesa lotada
    conv2 = _criar_convidado(client, token, evento["id"], {**CONVIDADO_BASE, "email": "x@conv.com"})
    resp = client.patch(
        f"/eventos/{evento['id']}/convidados/{conv2['id']}",
        json={"mesa_id": mesa["id"]},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_alocar_convidado_mesa_de_outro_evento_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento1 = _criar_evento(client, token)
    evento2 = _criar_evento(client, token, {**EVENTO_BASE, "nome_debutante": "Laura"})
    mesa_ev2 = _criar_mesa(client, token, evento2["id"])
    convidado = _criar_convidado(client, token, evento1["id"])

    resp = client.patch(
        f"/eventos/{evento1['id']}/convidados/{convidado['id']}",
        json={"mesa_id": mesa_ev2["id"]},
        headers=_auth(token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Acesso de cerimonialista a convidados e mesas
# ---------------------------------------------------------------------------


def test_cerimonialista_lista_convidados(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_convidado(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/convidados", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_cerimonialista_lista_mesas(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_mesa(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/mesas", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
