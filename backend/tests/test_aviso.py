"""
Testes do módulo de avisos (CRUD autenticado, aninhado em evento).
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@aviso.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@aviso.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@aviso.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

AVISO_BASE = {
    "titulo": "Horário de chegada da equipe",
    "mensagem": "Equipe deve chegar às 14h para montagem.",
    "destinatario_tipo": "equipe_interna",
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


def _criar_aviso(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/avisos",
        json=payload or AVISO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD de Avisos
# ---------------------------------------------------------------------------


def test_criar_aviso_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/avisos", json=AVISO_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["titulo"] == AVISO_BASE["titulo"]
    assert data["destinatario_tipo"] == "equipe_interna"
    assert data["data_publicacao"] is not None


def test_criar_aviso_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/avisos", json=AVISO_BASE)
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_aviso_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/avisos", json=AVISO_BASE, headers=_auth(token_ceri)
    )
    assert resp.status_code == 403


def test_listar_avisos(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_aviso(client, token, evento["id"])
    _criar_aviso(
        client,
        token,
        evento["id"],
        {**AVISO_BASE, "titulo": "Alteração no cardápio", "destinatario_tipo": "todos"},
    )
    resp = client.get(f"/eventos/{evento['id']}/avisos", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_aviso_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    aviso = _criar_aviso(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/avisos/{aviso['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == aviso["id"]


def test_obter_aviso_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/avisos/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_aviso(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    aviso = _criar_aviso(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/avisos/{aviso['id']}",
        json={"titulo": "Horário atualizado", "destinatario_tipo": "cerimonialista"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["titulo"] == "Horário atualizado"
    assert resp.json()["destinatario_tipo"] == "cerimonialista"


def test_excluir_aviso(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    aviso = _criar_aviso(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/avisos/{aviso['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/avisos/{aviso['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


def test_organizador_nao_acessa_avisos_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/avisos", headers=_auth(token_a))
    assert resp.status_code == 403


def test_cerimonialista_lista_avisos(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_aviso(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/avisos", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
