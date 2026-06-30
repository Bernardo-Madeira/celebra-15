"""
Testes do módulo de anotações cerimoniais (CRUD autenticado, aninhado em
evento). Diferente de outros módulos, organizador e cerimonialista têm
acesso de escrita, pois a anotação é a ferramenta de trabalho da
cerimonialista durante o planejamento da cerimônia.
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@cerimonial.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@cerimonial.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@cerimonial.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

ANOTACAO_BASE = {
    "momento_cerimonia": "Entrada da debutante",
    "descricao": "Entrada acompanhada pelo pai, valsa de fundo.",
    "nomes_envolvidos": "Pai: Roberto Silva",
    "ordem": 1,
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


def _criar_anotacao(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/anotacoes-cerimoniais",
        json=payload or ANOTACAO_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD de Anotações Cerimoniais
# ---------------------------------------------------------------------------


def test_criar_anotacao_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais", json=ANOTACAO_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["momento_cerimonia"] == ANOTACAO_BASE["momento_cerimonia"]
    assert data["ordem"] == 1


def test_criar_anotacao_por_cerimonialista(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais",
        json=ANOTACAO_BASE,
        headers=_auth(token_ceri),
    )
    assert resp.status_code == 201


def test_criar_anotacao_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/anotacoes-cerimoniais", json=ANOTACAO_BASE)
    assert resp.status_code == 401


def test_criar_anotacao_com_ordem_invalida_retorna_422(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais",
        json={**ANOTACAO_BASE, "ordem": 0},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_listar_anotacoes_ordenadas(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_anotacao(client, token, evento["id"], {**ANOTACAO_BASE, "ordem": 2})
    _criar_anotacao(
        client,
        token,
        evento["id"],
        {**ANOTACAO_BASE, "momento_cerimonia": "Valsa", "ordem": 1},
    )
    resp = client.get(f"/eventos/{evento['id']}/anotacoes-cerimoniais", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["ordem"] == 1
    assert data[1]["ordem"] == 2


def test_obter_anotacao_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    anotacao = _criar_anotacao(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais/{anotacao['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == anotacao["id"]


def test_obter_anotacao_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/anotacoes-cerimoniais/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_anotacao_por_cerimonialista(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    anotacao = _criar_anotacao(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.patch(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais/{anotacao['id']}",
        json={"descricao": "Descrição revisada"},
        headers=_auth(token_ceri),
    )
    assert resp.status_code == 200
    assert resp.json()["descricao"] == "Descrição revisada"


def test_excluir_anotacao(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    anotacao = _criar_anotacao(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais/{anotacao['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/anotacoes-cerimoniais/{anotacao['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


def test_organizador_nao_acessa_anotacoes_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/anotacoes-cerimoniais", headers=_auth(token_a))
    assert resp.status_code == 403
