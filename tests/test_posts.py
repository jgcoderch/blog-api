from tests.conftest import promote_to_admin


def register_and_login(client, email="user@teste.com", password="senha123"):
    client.post("/register", json={"email": email, "password": password})
    response = client.post("/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_read_post(client):
    headers = register_and_login(client)

    response = client.post("/posts", json={"title": "Meu post", "content": "Conteudo"}, headers=headers)
    assert response.status_code == 201
    assert response.json()["owner"]["email"] == "user@teste.com"

    response = client.get("/posts")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_post_does_not_require_auth(client):
    headers = register_and_login(client)
    client.post("/posts", json={"title": "Publico", "content": "..."}, headers=headers)

    response = client.get("/posts")
    assert response.status_code == 200


def test_other_user_cannot_edit_post(client):
    headers_a = register_and_login(client, "dono@teste.com", "senha123")
    headers_b = register_and_login(client, "outro@teste.com", "senha123")

    created = client.post("/posts", json={"title": "Original", "content": "..."}, headers=headers_a)
    post_id = created.json()["id"]

    response = client.put(f"/posts/{post_id}", json={"title": "Hackeado", "content": "..."}, headers=headers_b)
    assert response.status_code == 403


def test_admin_can_edit_any_post(client):
    headers_a = register_and_login(client, "dono2@teste.com", "senha123")
    headers_admin = register_and_login(client, "admin@teste.com", "senha123")
    promote_to_admin("admin@teste.com")

    created = client.post("/posts", json={"title": "Original", "content": "..."}, headers=headers_a)
    post_id = created.json()["id"]

    response = client.put(f"/posts/{post_id}", json={"title": "Editado pelo admin", "content": "..."}, headers=headers_admin)
    assert response.status_code == 200

def test_register_rejects_invalid_email(client):
    response = client.post("/register", json={"email": "nao-e-email", "password": "senha123"})
    assert response.status_code == 422


def test_register_rejects_short_password(client):
    response = client.post("/register", json={"email": "curta@teste.com", "password": "abc123"})
    assert response.status_code == 422

 
def test_register_rejects_password_without_digit(client):
    response = client.post("/register", json={"email": "semnumero@teste.com", "password": "senhasenha"})
    assert response.status_code == 422

def test_other_user_cannot_delete_comment(client):
    headers_a = register_and_login(client, "autor@teste.com", "senha123")
    headers_b = register_and_login(client, "estranho@teste.com", "senha123")

    post = client.post("/posts", json={"title": "Post", "content": "..."}, headers=headers_a).json()
    comment = client.post(f"/posts/{post['id']}/comments", json={"content": "Comentario"}, headers=headers_a).json()

    response = client.delete(f"/comments/{comment['id']}", headers=headers_b)
    assert response.status_code == 403