"""
Pruebas del modulo de metodos de pago.

El identificador acepta cualquier valor alfanumerico con longitud razonable.
La unicidad por usuario se sigue cuidando via fingerprint HMAC.
"""

import pytest


VALID_CARD = "4111 1111 1111 1111"
ANOTHER_VALID_CARD = "5500 0000 0000 0004"
SHORT_IDENTIFIER = "12"
VALID_CLABE = "012345678901234567"


def _card_payload(**overrides):
    base = {
        "type": "card",
        "alias": "Mi Visa",
        "institution": "BBVA",
        "currency": "MXN",
        "identifier": VALID_CARD,
    }
    base.update(overrides)
    return base


def test_create_card_returns_masked(client, auth_headers):
    response = client.post("/payment-methods", json=_card_payload(), headers=auth_headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["identifier_last4"] == "1111"
    assert "1111" in body["identifier_masked"]
    # Nunca debe regresar el numero completo
    assert "4111111111111111" not in body["identifier_masked"]


def test_create_accepts_any_card_number(client, auth_headers):
    # No se aplica Luhn: cualquier secuencia con longitud razonable es valida.
    response = client.post(
        "/payment-methods",
        json=_card_payload(identifier="1234567890123456"),
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["identifier_last4"] == "3456"


def test_create_rejects_identifier_too_short(client, auth_headers):
    # Pydantic exige minimo 4 caracteres en el schema; longitudes menores
    # son rechazadas como entrada invalida.
    response = client.post(
        "/payment-methods",
        json=_card_payload(identifier=SHORT_IDENTIFIER),
        headers=auth_headers,
    )
    assert response.status_code in (400, 422)


def test_create_clabe_with_any_length(client, auth_headers):
    response = client.post(
        "/payment-methods",
        json=_card_payload(type="clabe", identifier=VALID_CLABE, alias="Nomina"),
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["identifier_last4"] == VALID_CLABE[-4:]


def test_duplicate_card_is_rejected(client, auth_headers):
    first = client.post("/payment-methods", json=_card_payload(), headers=auth_headers)
    assert first.status_code == 201
    second = client.post("/payment-methods", json=_card_payload(alias="Otra"), headers=auth_headers)
    assert second.status_code == 409


def test_list_methods_pagination(client, auth_headers):
    # Se registran dos tarjetas validas distintas
    client.post("/payment-methods", json=_card_payload(), headers=auth_headers)
    client.post(
        "/payment-methods",
        json=_card_payload(identifier=ANOTHER_VALID_CARD, alias="Mi MC"),
        headers=auth_headers,
    )
    response = client.get("/payment-methods?page=1&size=10", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_list_filter_by_status(client, auth_headers):
    create = client.post("/payment-methods", json=_card_payload(), headers=auth_headers).json()
    client.patch(f"/payment-methods/{create['id']}/deactivate", headers=auth_headers)

    active = client.get("/payment-methods?status=active", headers=auth_headers).json()
    inactive = client.get("/payment-methods?status=inactive", headers=auth_headers).json()
    assert active["total"] == 0
    assert inactive["total"] == 1


def test_get_method_detail(client, auth_headers):
    created = client.post("/payment-methods", json=_card_payload(), headers=auth_headers).json()
    response = client.get(f"/payment-methods/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_deactivate_method(client, auth_headers):
    created = client.post("/payment-methods", json=_card_payload(), headers=auth_headers).json()
    response = client.patch(
        f"/payment-methods/{created['id']}/deactivate",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


def test_soft_delete_method(client, auth_headers):
    created = client.post("/payment-methods", json=_card_payload(), headers=auth_headers).json()
    response = client.delete(f"/payment-methods/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    # Tras el soft delete ya no debe aparecer en el listado
    listed = client.get("/payment-methods", headers=auth_headers).json()
    assert listed["total"] == 0

    # Y el detalle responde 404
    detail = client.get(f"/payment-methods/{created['id']}", headers=auth_headers)
    assert detail.status_code == 404


def test_methods_isolated_by_user(client):
    # Usuario A registra un metodo
    reg_a = client.post(
        "/auth/register",
        json={"email": "a@example.com", "full_name": "Usuario A", "password": "Clave1234"},
    )
    assert reg_a.status_code == 201, reg_a.text
    token_a = client.post(
        "/auth/login",
        json={"email": "a@example.com", "password": "Clave1234"},
    ).json()["access_token"]
    client.post(
        "/payment-methods",
        json=_card_payload(),
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Usuario B no deberia ver ningun metodo
    reg_b = client.post(
        "/auth/register",
        json={"email": "b@example.com", "full_name": "Usuario B", "password": "Clave1234"},
    )
    assert reg_b.status_code == 201, reg_b.text
    token_b = client.post(
        "/auth/login",
        json={"email": "b@example.com", "password": "Clave1234"},
    ).json()["access_token"]
    listed_b = client.get(
        "/payment-methods",
        headers={"Authorization": f"Bearer {token_b}"},
    ).json()
    assert listed_b["total"] == 0
