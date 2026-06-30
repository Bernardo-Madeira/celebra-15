"""
Testes do módulo de presentes: CRUD autenticado e reserva pública via token.
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@pres.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@pres.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@pres.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

CONVIDADO_BASE = {
    "nome": "Pedro Convidado",
    "email": "pedro@pres.com",
    "telefone": "21999990001",
}

PRESENTE_BASE = {
    "nome": "Jogo de panelas",
    "descricao": "Conjunto com 5 peças",
    "link_loja": "https://loja.exemplo.com/panelas",
    "quantidade_maxima_contribuintes": 1,
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


def _criar_presente(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/presentes",
        json=payload or PRESENTE_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD de Presentes
# ---------------------------------------------------------------------------


def test_criar_presente_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/presentes", json=PRESENTE_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == PRESENTE_BASE["nome"]
    assert data["quantidade_maxima_contribuintes"] == 1
    assert data["reservas"] == []


def test_criar_presente_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/presentes", json=PRESENTE_BASE)
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_presente_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/presentes", json=PRESENTE_BASE, headers=_auth(token_ceri)
    )
    assert resp.status_code == 403


def test_criar_presente_quantidade_invalida_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/presentes",
        json={**PRESENTE_BASE, "quantidade_maxima_contribuintes": 0},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_listar_presentes(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_presente(client, token, evento["id"])
    _criar_presente(client, token, evento["id"], {**PRESENTE_BASE, "nome": "Liquidificador"})
    resp = client.get(f"/eventos/{evento['id']}/presentes", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_presente_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/presentes/{presente['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == presente["id"]


def test_obter_presente_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/presentes/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_presente(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/presentes/{presente['id']}",
        json={"nome": "Panela de pressão", "quantidade_maxima_contribuintes": 3},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Panela de pressão"
    assert resp.json()["quantidade_maxima_contribuintes"] == 3


def test_excluir_presente(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/presentes/{presente['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/presentes/{presente['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


def test_organizador_nao_acessa_presentes_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/presentes", headers=_auth(token_a))
    assert resp.status_code == 403


def test_cerimonialista_lista_presentes(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_presente(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/presentes", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ---------------------------------------------------------------------------
# Reserva de presentes (pública, via token_confirmacao do convidado)
# ---------------------------------------------------------------------------


def test_listar_presentes_publico_via_token(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_presente(client, token, evento["id"])
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.get(f"/presentes/lista/{convidado['token_confirmacao']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_listar_presentes_publico_token_invalido_retorna_404(client):
    resp = client.get("/presentes/lista/token-falso")
    assert resp.status_code == 404


def test_reservar_presente_publico(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(
        client, token, evento["id"], {**PRESENTE_BASE, "quantidade_maxima_contribuintes": 2}
    )
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.post(
        f"/presentes/reservar/{convidado['token_confirmacao']}/{presente['id']}"
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["presente_id"] == presente["id"]
    assert data["convidado_id"] == convidado["id"]


def test_reservar_presente_token_invalido_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(client, token, evento["id"])

    resp = client.post(f"/presentes/reservar/token-falso/{presente['id']}")
    assert resp.status_code == 404


def test_reservar_presente_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.post(f"/presentes/reservar/{convidado['token_confirmacao']}/9999")
    assert resp.status_code == 404


def test_reservar_presente_duas_vezes_mesmo_convidado_retorna_409(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(
        client, token, evento["id"], {**PRESENTE_BASE, "quantidade_maxima_contribuintes": 2}
    )
    convidado = _criar_convidado(client, token, evento["id"])
    tok = convidado["token_confirmacao"]

    client.post(f"/presentes/reservar/{tok}/{presente['id']}")
    resp = client.post(f"/presentes/reservar/{tok}/{presente['id']}")
    assert resp.status_code == 409


def test_reservar_presente_cota_esgotada_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(
        client, token, evento["id"], {**PRESENTE_BASE, "quantidade_maxima_contribuintes": 1}
    )
    convidado1 = _criar_convidado(client, token, evento["id"])
    convidado2 = _criar_convidado(
        client, token, evento["id"], {**CONVIDADO_BASE, "email": "outro@pres.com"}
    )

    resp1 = client.post(
        f"/presentes/reservar/{convidado1['token_confirmacao']}/{presente['id']}"
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        f"/presentes/reservar/{convidado2['token_confirmacao']}/{presente['id']}"
    )
    assert resp2.status_code == 422


def test_cancelar_reserva(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(client, token, evento["id"])
    convidado = _criar_convidado(client, token, evento["id"])
    tok = convidado["token_confirmacao"]

    client.post(f"/presentes/reservar/{tok}/{presente['id']}")
    resp = client.delete(f"/presentes/reservar/{tok}/{presente['id']}")
    assert resp.status_code == 204

    # após cancelar, outro convidado pode reservar o mesmo presente
    convidado2 = _criar_convidado(
        client, token, evento["id"], {**CONVIDADO_BASE, "email": "outro2@pres.com"}
    )
    resp2 = client.post(
        f"/presentes/reservar/{convidado2['token_confirmacao']}/{presente['id']}"
    )
    assert resp2.status_code == 201


def test_cancelar_reserva_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    presente = _criar_presente(client, token, evento["id"])
    convidado = _criar_convidado(client, token, evento["id"])

    resp = client.delete(
        f"/presentes/reservar/{convidado['token_confirmacao']}/{presente['id']}"
    )
    assert resp.status_code == 404
