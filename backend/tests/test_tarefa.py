"""
Testes do módulo de tarefas (CRUD autenticado, aninhado em evento).
"""

from fastapi.testclient import TestClient

ORGANIZADOR = {"nome": "Ana Org", "email": "ana@tarefa.com", "senha": "senha123"}
ORGANIZADOR_B = {"nome": "Bruno Org", "email": "bruno@tarefa.com", "senha": "senha456"}
CERIMONIALISTA = {"nome": "Carlos Ceri", "email": "carlos@tarefa.com", "senha": "senha789"}

EVENTO_BASE = {
    "nome_debutante": "Júlia",
    "data_evento": "2025-06-15T20:00:00",
    "local": "Salão Estrelas",
    "max_acompanhantes_por_convidado": 2,
}

TAREFA_BASE = {
    "titulo": "Fechar contrato do buffet",
    "descricao": "Confirmar cardápio final e forma de pagamento.",
    "data_prazo": "2025-03-01",
    "responsavel": "Ana Org",
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


def _criar_tarefa(
    client: TestClient, token: str, evento_id: int, payload: dict | None = None
) -> dict:
    resp = client.post(
        f"/eventos/{evento_id}/tarefas",
        json=payload or TAREFA_BASE,
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD de Tarefas
# ---------------------------------------------------------------------------


def test_criar_tarefa_por_organizador(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(
        f"/eventos/{evento['id']}/tarefas", json=TAREFA_BASE, headers=_auth(token)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["titulo"] == TAREFA_BASE["titulo"]
    assert data["status"] == "pendente"


def test_criar_tarefa_sem_autenticacao_retorna_401(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.post(f"/eventos/{evento['id']}/tarefas", json=TAREFA_BASE)
    assert resp.status_code == 401


def test_cerimonialista_nao_cria_tarefa_retorna_403(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    token_ceri = _token_cerimonialista(client, token_org)
    resp = client.post(
        f"/eventos/{evento['id']}/tarefas", json=TAREFA_BASE, headers=_auth(token_ceri)
    )
    assert resp.status_code == 403


def test_listar_tarefas(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    _criar_tarefa(client, token, evento["id"])
    _criar_tarefa(
        client,
        token,
        evento["id"],
        {**TAREFA_BASE, "titulo": "Confirmar fotógrafo", "data_prazo": "2025-04-01"},
    )
    resp = client.get(f"/eventos/{evento['id']}/tarefas", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_obter_tarefa_por_id(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    tarefa = _criar_tarefa(client, token, evento["id"])
    resp = client.get(
        f"/eventos/{evento['id']}/tarefas/{tarefa['id']}", headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == tarefa["id"]


def test_obter_tarefa_inexistente_retorna_404(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    resp = client.get(f"/eventos/{evento['id']}/tarefas/9999", headers=_auth(token))
    assert resp.status_code == 404


def test_atualizar_tarefa(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    tarefa = _criar_tarefa(client, token, evento["id"])
    resp = client.patch(
        f"/eventos/{evento['id']}/tarefas/{tarefa['id']}",
        json={"status": "concluida", "titulo": "Contrato do buffet fechado"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "concluida"
    assert resp.json()["titulo"] == "Contrato do buffet fechado"


def test_excluir_tarefa(client):
    token = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token)
    tarefa = _criar_tarefa(client, token, evento["id"])
    resp = client.delete(
        f"/eventos/{evento['id']}/tarefas/{tarefa['id']}", headers=_auth(token)
    )
    assert resp.status_code == 204
    resp_get = client.get(
        f"/eventos/{evento['id']}/tarefas/{tarefa['id']}", headers=_auth(token)
    )
    assert resp_get.status_code == 404


def test_organizador_nao_acessa_tarefas_de_outro_retorna_403(client):
    token_a = _cadastrar_e_login(client, ORGANIZADOR)
    token_b = _cadastrar_e_login(client, ORGANIZADOR_B)
    evento_b = _criar_evento(client, token_b)
    resp = client.get(f"/eventos/{evento_b['id']}/tarefas", headers=_auth(token_a))
    assert resp.status_code == 403


def test_cerimonialista_lista_tarefas(client):
    token_org = _cadastrar_e_login(client, ORGANIZADOR)
    evento = _criar_evento(client, token_org)
    _criar_tarefa(client, token_org, evento["id"])
    token_ceri = _token_cerimonialista(client, token_org)

    resp = client.get(f"/eventos/{evento['id']}/tarefas", headers=_auth(token_ceri))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
