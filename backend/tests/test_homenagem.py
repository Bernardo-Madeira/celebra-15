"""
Testes do módulo de homenagens (CRUD autenticado, aninhado em evento).
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@homenagem.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@homenagem.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@homenagem.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

HOMENAGEM_BASE = {
    "homenageado": "Júlia",
    "texto": "Que esse novo ciclo seja repleto de alegria.",
    "ordem": 1,
    "autor": "Família",
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


def _criar_homenagem(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/homenagens",
        json=payload or HOMENAGEM_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD de Homenagens
# ---------------------------------------------------------------------------


def test_criar_homenagem_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/homenagens", json=HOMENAGEM_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["homenageado"] == HOMENAGEM_BASE["homenageado"]
    assert data["ordem"] == 1


def test_criar_homenagem_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/homenagens", json=HOMENAGEM_BASE)
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_homenagem_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/homenagens", json=HOMENAGEM_BASE, headers=_auth(token_ceri)
    )
    assert resp.status_code == 403


def test_criar_homenagem_com_ordem_invalida_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/homenagens",
        json={**HOMENAGEM_BASE, "ordem": 0},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_listar_homenagens_ordenadas(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_homenagem(client, token, evento["id"], {**HOMENAGEM_BASE, "ordem": 2})
    _criar_homenagem(
        client,
        token,
        evento["id"],
        {**HOMENAGEM_BASE, "homenageado": "Madrinha", "ordem": 1},
    )
    resp = client.get(f"/eventos/{evento['id']}/homenagens", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["ordem"] == 1
    assert data[1]["ordem"] == 2


def test_obter_homenagem_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    homenagem = _criar_homenagem(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/homenagens/{homenagem['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == homenagem["id"]


def test_obter_homenagem_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/homenagens/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_homenagem(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    homenagem = _criar_homenagem(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/homenagens/{homenagem['id']}",
        json={"texto": "Texto revisado", "ordem": 2},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["texto"] == "Texto revisado"
    assert resp.json()["ordem"] == 2


def test_excluir_homenagem(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    homenagem = _criar_homenagem(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/homenagens/{homenagem['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/homenagens/{homenagem['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


def test_organizador_nao_acessa_homenagens_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/homenagens", headers=_auth(token_a))
    assert resp.status_code == 403


def test_cerimonialista_lista_homenagens(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_homenagem(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/homenagens", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
