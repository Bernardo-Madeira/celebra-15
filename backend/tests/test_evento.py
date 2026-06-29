"""
Testes do módulo de eventos: CRUD e controle de acesso por perfil.
"""

import pytest
from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@evento.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@evento.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@evento.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cadastrar_e_login(client: TestClient, usuario: dict) -> str:
    """Cadastra organizador e retorna access_token."""
    client.post("/usuarios/organizador", json=usuario)
    resp = client.post(
        "/auth/login", data={"username": usuario["email"], "password": usuario["senha"]}
    )
    return resp.json()["access_token"]


def _token_cerimonialista(client: TestClient, token_org: str) -> str:
    client.post(
        "/usuarios/cerimonialista",
        json=CERIMONIALISTA,
        headers={"Authorization": f"Bearer {token_org}"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": CERIMONIALISTA["email"], "password": CERIMONIALISTA["senha"]},
    )
    return resp.json()["access_token"]


def _criar_evento(client: TestClient, token: str, payload: dict | None = None) -> dict:
    resp = client.post(
        "/eventos",
        json=payload or EVENTO_BASE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Criar evento
# ---------------------------------------------------------------------------


def test_criar_evento_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    resp = client.post("/eventos", json=EVENTO_BASE, headers=_auth(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome_debutante"] == EVENTO_BASE["nome_debutante"]
    assert data["local"] == EVENTO_BASE["local"]
    assert data["max_acompanhantes_por_convidado"] == 2


def test_criar_evento_sem_autenticacao_retorna_401(client):
    resp = client.post("/eventos", json=EVENTO_BASE)
    assert resp.status_code == 401


def test_criar_evento_por_cerimonialista_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post("/eventos", json=EVENTO_BASE, headers=_auth(token_ceri))
    assert resp.status_code == 403


def test_criar_evento_com_max_acompanhantes_negativo_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    payload = {**EVENTO_BASE, "max_acompanhantes_por_convidado": -1}
    resp = client.post("/eventos", json=payload, headers=_auth(token))
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Listar eventos
# ---------------------------------------------------------------------------


def test_listar_retorna_apenas_eventos_do_organizador(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    _criar_evento(client, token_a)
    _criar_evento(client, token_b, {**EVENTO_BASE, "nome_debutante": "Mariana"})

    resp = client.get("/eventos", headers=_auth(token_a))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["nome_debutante"] == "Júlia"


def test_cerimonialista_lista_todos_os_eventos(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    _criar_evento(client, token_org)
    _criar_evento(client, token_b, {**EVENTO_BASE, "nome_debutante": "Mariana"})
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get("/eventos", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_listar_sem_autenticacao_retorna_401(client):
    resp = client.get("/eventos")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Obter evento por ID
# ---------------------------------------------------------------------------


def test_obter_evento_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == evento["id"]


def test_obter_evento_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    resp = client.get("/eventos/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_organizador_nao_acessa_evento_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento['id']}", headers=_auth(token_a))
    assert resp.status_code == 403


def test_cerimonialista_acessa_qualquer_evento(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento = _criar_evento(client, token_b)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.get(f"/eventos/{evento['id']}", headers=_auth(token_ceri))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Atualizar evento
# ---------------------------------------------------------------------------


def test_atualizar_evento_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.patch(
        f"/eventos/{evento['id']}",
        json={"local": "Novo Salão", "max_acompanhantes_por_convidado": 3},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["local"] == "Novo Salão"
    assert resp.json()["max_acompanhantes_por_convidado"] == 3


def test_organizador_nao_atualiza_evento_alheio_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento = _criar_evento(client, token_b)
    resp = client.patch(
        f"/eventos/{evento['id']}", json={"local": "Invasão"}, headers=_auth(token_a)
    )
    assert resp.status_code == 403


def test_cerimonialista_nao_atualiza_evento_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.patch(
        f"/eventos/{evento['id']}", json={"local": "Invasão"}, headers=_auth(token_ceri)
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Excluir evento
# ---------------------------------------------------------------------------


def test_excluir_evento_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.delete(f"/eventos/{evento['id']}", headers=_auth(token))
    assert resp.status_code == 204
    resp_get = client.get(f"/eventos/{evento['id']}", headers=_auth(token))
    assert resp_get.status_code == 404


def test_organizador_nao_exclui_evento_alheio_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento = _criar_evento(client, token_b)
    resp = client.delete(f"/eventos/{evento['id']}", headers=_auth(token_a))
    assert resp.status_code == 403
