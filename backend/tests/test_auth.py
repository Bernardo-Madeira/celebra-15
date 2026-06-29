"""
Testes de autenticação: login, refresh, logout, login de convidado,
recuperação de senha e alteração de senha.
"""

import pytest
from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Organizadora", "email": "ana@auth.com", "senha": "senha123"}


def _cadastrar_e_login(client: TestClient) -> dict:
    """Cadastra organizador e faz login, retornando o payload completo do login."""
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post(
        "/auth/login",
        data={"username": ORGANIZADOR["email"], "password": ORGANIZADOR["senha"]},
    )
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def test_login_retorna_access_e_refresh_token(client):
    data = _cadastrar_e_login(client)
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciais_invalidas_retorna_401(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post(
        "/auth/login",
        data={"username": ORGANIZADOR["email"], "password": "errada"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------


def test_refresh_retorna_novo_par_de_tokens(client):
    tokens = _cadastrar_e_login(client)
    resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Novo refresh token deve ser diferente do anterior (rotação)
    assert data["refresh_token"] != tokens["refresh_token"]


def test_refresh_com_token_invalido_retorna_401(client):
    _cadastrar_e_login(client)
    resp = client.post("/auth/refresh", json={"refresh_token": "token-inexistente"})
    assert resp.status_code == 401


def test_refresh_token_pode_ser_usado_apenas_uma_vez(client):
    tokens = _cadastrar_e_login(client)
    # Primeiro refresh — deve funcionar
    resp1 = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp1.status_code == 200
    # Segundo refresh com o token original — deve falhar (token revogado)
    resp2 = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp2.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


def test_logout_revoga_refresh_token(client):
    tokens = _cadastrar_e_login(client)
    resp = client.post(
        "/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 204
    # Após logout, refresh token não deve mais funcionar
    resp2 = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp2.status_code == 401


def test_logout_sem_autenticacao_retorna_401(client):
    resp = client.post("/auth/logout", json={"refresh_token": "qualquer"})
    assert resp.status_code == 401


def test_logout_com_refresh_token_invalido_retorna_401(client):
    tokens = _cadastrar_e_login(client)
    resp = client.post(
        "/auth/logout",
        json={"refresh_token": "token-invalido"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Esqueci minha senha / Redefinir senha
# ---------------------------------------------------------------------------


def test_esqueci_senha_retorna_200_sempre(client):
    """Não revela se o e-mail existe — sempre 200."""
    resp = client.post("/auth/esqueci-senha", json={"email": "naoexiste@exemplo.com"})
    assert resp.status_code == 200


def test_esqueci_senha_gera_token_para_email_cadastrado(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp = client.post("/auth/esqueci-senha", json={"email": ORGANIZADOR["email"]})
    assert resp.status_code == 200
    assert resp.json()["token_reset"] is not None


def test_redefinir_senha_com_token_valido(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp_token = client.post("/auth/esqueci-senha", json={"email": ORGANIZADOR["email"]})
    token_reset = resp_token.json()["token_reset"]

    resp = client.post(
        "/auth/redefinir-senha",
        json={"token": token_reset, "nova_senha": "novaSenha456"},
    )
    assert resp.status_code == 204

    # Deve conseguir logar com a nova senha
    resp_login = client.post(
        "/auth/login",
        data={"username": ORGANIZADOR["email"], "password": "novaSenha456"},
    )
    assert resp_login.status_code == 200


def test_redefinir_senha_invalida_senha_antiga(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp_token = client.post("/auth/esqueci-senha", json={"email": ORGANIZADOR["email"]})
    token_reset = resp_token.json()["token_reset"]

    client.post(
        "/auth/redefinir-senha",
        json={"token": token_reset, "nova_senha": "novaSenha456"},
    )

    # Senha original não deve mais funcionar
    resp_login = client.post(
        "/auth/login",
        data={"username": ORGANIZADOR["email"], "password": ORGANIZADOR["senha"]},
    )
    assert resp_login.status_code == 401


def test_redefinir_senha_token_invalido_retorna_401(client):
    resp = client.post(
        "/auth/redefinir-senha",
        json={"token": "token-falso", "nova_senha": "qualquer"},
    )
    assert resp.status_code == 401


def test_redefinir_senha_token_de_uso_unico(client):
    client.post("/usuarios/organizador", json=ORGANIZADOR)
    resp_token = client.post("/auth/esqueci-senha", json={"email": ORGANIZADOR["email"]})
    token_reset = resp_token.json()["token_reset"]

    client.post("/auth/redefinir-senha", json={"token": token_reset, "nova_senha": "senha1"})
    # Segunda tentativa com o mesmo token deve falhar
    resp2 = client.post("/auth/redefinir-senha", json={"token": token_reset, "nova_senha": "senha2"})
    assert resp2.status_code == 401


# ---------------------------------------------------------------------------
# Alterar senha (autenticado)
# ---------------------------------------------------------------------------


def test_alterar_senha_com_sucesso(client):
    tokens = _cadastrar_e_login(client)
    resp = client.post(
        "/auth/alterar-senha",
        json={"senha_atual": ORGANIZADOR["senha"], "nova_senha": "novaSenha789"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 204

    # Nova senha deve funcionar
    resp_login = client.post(
        "/auth/login",
        data={"username": ORGANIZADOR["email"], "password": "novaSenha789"},
    )
    assert resp_login.status_code == 200


def test_alterar_senha_revoga_refresh_tokens(client):
    tokens = _cadastrar_e_login(client)
    client.post(
        "/auth/alterar-senha",
        json={"senha_atual": ORGANIZADOR["senha"], "nova_senha": "novaSenha789"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    # Refresh token anterior deve estar revogado
    resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401


def test_alterar_senha_com_senha_atual_errada_retorna_400(client):
    tokens = _cadastrar_e_login(client)
    resp = client.post(
        "/auth/alterar-senha",
        json={"senha_atual": "senhaErrada", "nova_senha": "novaSenha789"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 400


def test_alterar_senha_sem_autenticacao_retorna_401(client):
    resp = client.post(
        "/auth/alterar-senha",
        json={"senha_atual": "qualquer", "nova_senha": "qualquer"},
    )
    assert resp.status_code == 401
