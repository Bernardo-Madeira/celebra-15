import pytest
from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Organizadora", "email": "ana@exemplo.com", "senha": "senha123"}
CERIMONIALISTA = {"nome": "Carlos Cerimonialista", "email": "carlos@exemplo.com", "senha": "senha456"}


def _token_organizador(client: TestClient) -> str:
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post("/auth/login", data={"username": ORGANIZADOR["email"], "password": ORGANIZADOR["senha"]})
    return resp.json()["access_token"]


def _token(client: TestClient, email: str, senha: str) -> str:
    resp = client.post("/auth/login", data={"username": email, "password": senha})
    return resp.json()["access_token"]


def _criar_cerimonialista(client: TestClient, token_organizador: str) -> int:
    resp = client.post(
        "/usuarios/cerimonialista",
        json=CERIMONIALISTA,
        headers={"Authorization": f"Bearer {token_organizador}"},
    )
    return resp.json()["id"]


def test_cadastro_organizador_sucesso(client):
    resp = client.post("/usuarios/organizador", json=ORGANIZADOR)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == ORGANIZADOR["email"]
    assert data["tipo_perfil"] == "organizador"
    assert "senha" not in data
    assert "senha_hash" not in data


def test_email_duplicado_retorna_409(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post("/usuarios/organizador", json=ORGANIZADOR)
    assert resp.status_code == 409


def test_login_sucesso(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post("/auth/login", data={"username": ORGANIZADOR["email"], "password": ORGANIZADOR["senha"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_login_credenciais_invalidas(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post("/auth/login", data={"username": ORGANIZADOR["email"], "password": "senha_errada"})
    assert resp.status_code == 401


def test_me_retorna_perfil_autenticado(client):
    token = _token_organizador(client)
    resp = client.get("/usuarios/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == ORGANIZADOR["email"]
    assert resp.json()["tipo_perfil"] == "organizador"


def test_criar_cerimonialista_por_organizador(client):
    token = _token_organizador(client)
    resp = client.post(
        "/usuarios/cerimonialista",
        json=CERIMONIALISTA,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["tipo_perfil"] == "cerimonialista"


def test_criar_cerimonialista_sem_autenticacao_retorna_401(client):
    resp = client.post("/usuarios/cerimonialista", json=CERIMONIALISTA)
    assert resp.status_code == 401


def test_listar_cerimonialistas_por_organizador(client):
    token = _token_organizador(client)
    _criar_cerimonialista(client, token)
    resp = client.get("/usuarios/cerimonialistas", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["email"] == CERIMONIALISTA["email"]


def test_obter_cerimonialista_por_id(client):
    token = _token_organizador(client)
    cerimonialista_id = _criar_cerimonialista(client, token)
    resp = client.get(
        f"/usuarios/cerimonialistas/{cerimonialista_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == cerimonialista_id


def test_obter_cerimonialista_inexistente_retorna_404(client):
    token = _token_organizador(client)
    resp = client.get("/usuarios/cerimonialistas/9999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_atualizar_cerimonialista_por_organizador(client):
    token = _token_organizador(client)
    cerimonialista_id = _criar_cerimonialista(client, token)
    resp = client.patch(
        f"/usuarios/cerimonialistas/{cerimonialista_id}",
        json={"nome": "Carlos Atualizado"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Carlos Atualizado"


def test_excluir_cerimonialista_por_organizador(client):
    token = _token_organizador(client)
    cerimonialista_id = _criar_cerimonialista(client, token)
    resp = client.delete(
        f"/usuarios/cerimonialistas/{cerimonialista_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
    resp = client.get(
        f"/usuarios/cerimonialistas/{cerimonialista_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_atualizar_proprio_perfil(client):
    token = _token_organizador(client)
    resp = client.patch(
        "/usuarios/me",
        json={"nome": "Ana Atualizada"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Ana Atualizada"


def test_cerimonialista_nao_pode_gerenciar_outros_cerimonialistas(client):
    token_organizador = _token_organizador(client)
    _criar_cerimonialista(client, token_organizador)
    token_cerimonialista = _token(client, CERIMONIALISTA["email"], CERIMONIALISTA["senha"])
    resp = client.get(
        "/usuarios/cerimonialistas",
        headers={"Authorization": f"Bearer {token_cerimonialista}"},
    )
    assert resp.status_code == 403
