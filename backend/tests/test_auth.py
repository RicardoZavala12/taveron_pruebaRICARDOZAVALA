"""
Pruebas del flujo de autenticacion.
"""


def test_register_creates_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "nuevo@example.com",
            "full_name": "Usuario Nuevo",
            "password": "Clave1234",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "nuevo@example.com"
    assert "id" in body
    # La contrasena nunca debe regresar en la respuesta.
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejects_weak_password(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "weak@example.com",
            "full_name": "Sin Numeros",
            "password": "soloLetras",
        },
    )
    assert response.status_code == 422


def test_register_rejects_duplicate_email(client, registered_user):
    response = client.post("/auth/register", json=registered_user)
    assert response.status_code == 409


def test_login_returns_token(client, registered_user):
    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == registered_user["email"]


def test_login_with_wrong_password(client, registered_user):
    response = client.post(
        "/auth/login",
        json={"email": registered_user["email"], "password": "incorrecta1"},
    )
    assert response.status_code == 401


def test_profile_requires_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_profile_returns_current_user(client, auth_headers, registered_user):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


def test_logout_succeeds(client, auth_headers):
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 204


def test_change_password_requires_auth(client):
    response = client.put(
        "/users/me/password",
        json={"current_password": "x", "new_password": "Nuev4Pass"},
    )
    assert response.status_code == 401


def test_change_password_with_correct_current(client, auth_headers, registered_user):
    response = client.put(
        "/users/me/password",
        headers=auth_headers,
        json={
            "current_password": registered_user["password"],
            "new_password": "Nuev4Clave",
        },
    )
    assert response.status_code == 204

    # La contrasena anterior ya no debe servir
    failed = client.post(
        "/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert failed.status_code == 401

    # La nueva contrasena debe permitir login
    ok = client.post(
        "/auth/login",
        json={"email": registered_user["email"], "password": "Nuev4Clave"},
    )
    assert ok.status_code == 200


def test_change_password_rejects_wrong_current(client, auth_headers):
    response = client.put(
        "/users/me/password",
        headers=auth_headers,
        json={"current_password": "incorrecta", "new_password": "Nuev4Clave"},
    )
    assert response.status_code == 400


def test_change_password_rejects_weak_new(client, auth_headers, registered_user):
    response = client.put(
        "/users/me/password",
        headers=auth_headers,
        json={
            "current_password": registered_user["password"],
            "new_password": "soloLetras",
        },
    )
    assert response.status_code == 422


def test_change_password_rejects_same_as_current(client, auth_headers, registered_user):
    response = client.put(
        "/users/me/password",
        headers=auth_headers,
        json={
            "current_password": registered_user["password"],
            "new_password": registered_user["password"],
        },
    )
    assert response.status_code == 400
