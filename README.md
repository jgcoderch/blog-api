# Blog API

![Tests](https://github.com/jgcoderch/blog-api/actions/workflows/tests.yml/badge.svg)

API REST de um blog simples, com posts, comentários e controle de acesso por papel de usuário (RBAC). Desenvolvida como projeto de estudo.

## Tecnologias

- **Python 3.13**
- **FastAPI** — framework web
- **SQLAlchemy** — ORM, com relacionamentos entre tabelas (`relationship`, `back_populates`, cascade)
- **Alembic** — migrações do banco de dados
- **Pydantic** — validação de dados, incluindo schemas aninhados
- **JWT (python-jose) + Passlib/bcrypt** — autenticação e hash de senha
- **Pytest** — testes automatizados

## Funcionalidades

- Cadastro e login de usuário (papéis: `user` ou `admin`)
- CRUD de posts — leitura pública, escrita restrita ao autor ou a administradores
- Comentários vinculados a posts — mesma regra de permissão
- Exclusão em cascata: apagar um post remove seus comentários automaticamente

## Como rodar o projeto

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

A documentação interativa fica em `http://localhost:8000/docs`.

## Rodando os testes

```bash
pytest
```

## Endpoints

| Método | Rota                         | Descrição                       | Permissão            |
|--------|------------------------------|-----------------------------------|------------------------|
| POST   | /register                     | Cadastra um novo usuário          | Pública                |
| POST   | /login                        | Autentica e retorna um token JWT  | Pública                |
| POST   | /posts                        | Cria um post                      | Usuário autenticado    |
| GET    | /posts                        | Lista todos os posts              | Pública                |
| GET    | /posts/{post_id}              | Busca um post por ID              | Pública                |
| PUT    | /posts/{post_id}              | Atualiza um post                  | Dono ou admin          |
| DELETE | /posts/{post_id}              | Remove um post                    | Dono ou admin          |
| POST   | /posts/{post_id}/comments     | Comenta em um post                | Usuário autenticado    |
| GET    | /posts/{post_id}/comments     | Lista comentários de um post      | Pública                |
| DELETE | /comments/{comment_id}        | Remove um comentário              | Dono ou admin          |

## Estrutura do projeto

```
blog-api/
├── app/
│   ├── main.py          # Rotas, autenticação e controle de permissão
│   ├── models.py         # User, Post, Comment com relacionamentos e enum de papel
│   ├── schemas.py         # Schemas Pydantic (com aninhamento de owner)
│   ├── database.py        # Configuração da conexão com o banco
│   └── security.py        # Hash de senha e geração/validação de JWT
├── alembic/                # Migrações do banco de dados
├── tests/                  # Testes automatizados (pytest)
├── requirements.txt
└── README.md
```