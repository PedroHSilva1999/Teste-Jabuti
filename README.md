# usuarios-api

API de CRUD de usuários com **FastAPI**, **PostgreSQL** e **Redis**.

## Visão geral

A aplicação disponibiliza endpoints REST para:

- listar usuários (com paginação)
- buscar usuário por `user_id` (UUID)
- criar usuário
- atualizar usuário
- excluir usuário

Os dados são persistidos em PostgreSQL e as respostas de listagem e detalhes são cacheadas em Redis para melhorar o desempenho.

## Tecnologias

- FastAPI (Swagger/OpenAPI)
- Uvicorn
- PostgreSQL 16 (via Docker)
- Redis 7 (via Docker)
- SQLAlchemy (ORM)
- psycopg (driver PostgreSQL)
- Redis (cliente)

## Swagger (documentação)

A documentação interativa dos endpoints está em:

- `http://localhost:8000/docs`

## Por que inclui `pgadmin4` e `redisinsight`?

Embora o teste técnico não mencionasse explicitamente as ferramentas de visualização, incluí **pgadmin4** e **redisinsight** no `docker-compose.yml` para facilitar:

- inspeção manual dos dados do PostgreSQL
- visualização e conferência do que está sendo cacheado no Redis

Isso tende a acelerar debugging e validação durante o desenvolvimento.

## Acessar pgAdmin4

- URL: `http://localhost:5050`
- Credenciais (defaults no `docker-compose.yml`):
  - Email: `admin@admin.com` (ou `PGADMIN_DEFAULT_EMAIL` no seu `.env`)
  - Password: `admin` (ou `PGADMIN_DEFAULT_PASSWORD` no seu `.env`)

Para registrar a base de dados:

1. No pgAdmin, vá em `Servers`.
2. Clique com o botão direito em `Servers` e selecione `Register`.
3. Em `General`, defina um `Name` (ex.: `users-db`).
4. Na aba `Connection`, preencha:
   - `Host name/address`: `users-db` (valor do `container_name` do `db` no `docker-compose.yml`)
   - `Port`: `5432`
   - `Maintenance database`: `${POSTGRES_DB}` (no `db` do compose: default `users_db`)
   - `Username`: `${POSTGRES_USER}` (no `db` do compose: default `postgres`)
   - `Password`: `${POSTGRES_PASSWORD}` (no `db` do compose: default `postgres`)
5. Salve para concluir o registro.

## Acessar RedisInsight

- URL: `http://localhost:5540`
- Na interface do RedisInsight, clique em `Connect existing database`.
- Use a string de conexão: `redis://cache:6379`
- Em seguida, clique em `Add database` (adicionar base de dados).


## Requisitos

- Docker
- Docker Compose

## Como executar (Docker Compose)

1. (Opcional) ajuste o arquivo `.env`.
2. Suba a stack:

```bash
docker compose up --build
```

A API sobe na porta **8000**.

### Parar a stack

```bash
docker compose down
```

## Variáveis de ambiente

O serviço da aplicação usa `env_file: .env`.

Se o `.env` estiver vazio, a aplicação usa defaults internos compatíveis com os nomes dos containers no `docker-compose.yml`:

- `DATABASE_URL` (por padrão aponta para `users-db`)
- `REDIS_URL` (por padrão aponta para `users-cache`)
- `REDIS_CACHE_TTL` (por padrão 300 segundos)

Exemplo de `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@users-db:5432/users_db
REDIS_URL=redis://users-cache:6379/0
REDIS_CACHE_TTL=300
```

> Observação: `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` são configurados no próprio `docker-compose.yml` com defaults caso não existam no `.env`.

## Endpoints (API)

Prefixo base: `/usuarios`

### Listar usuários

- `GET /usuarios`
- Parâmetros de query:
  - `limit` (inteiro, padrão `10`, mínimo `1`, máximo `100`)
  - `offset` (inteiro, padrão `0`, mínimo `0`)

Resposta (200):

```json
{
  "items": [
    {
      "id": "c4b3c2f8-6e61-4b4a-9e5c-8c1b8b6f6c44",
      "name": "Ana",
      "email": "ana@example.com",
      "age": 30
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

Cache: a listagem é cacheada por `(limit, offset)`.

### Obter usuário por ID

- `GET /usuarios/{user_id}`
- `user_id`: UUID

Resposta (200):

```json
{
  "id": "c4b3c2f8-6e61-4b4a-9e5c-8c1b8b6f6c44",
  "name": "Ana",
  "email": "ana@example.com",
  "age": 30
}
```

Cache: o detalhe é cacheado por `user_id`.

### Criar usuário

- `POST /usuarios`

Corpo (201):

```json
{
  "name": "Ana",
  "email": "ana@example.com",
  "age": 30
}
```

Resposta (201):

```json
{
  "id": "c4b3c2f8-6e61-4b4a-9e5c-8c1b8b6f6c44",
  "name": "Ana",
  "email": "ana@example.com",
  "age": 30
}
```

Erros:

- (409) `Email ja cadastrado`

### Atualizar usuário

- `PUT /usuarios/{user_id}`
- `user_id`: UUID

Corpo:

```json
{
  "name": "Ana Maria",
  "email": "ana.maria@example.com",
  "age": 31
}
```

Resposta (200):

```json
{
  "id": "c4b3c2f8-6e61-4b4a-9e5c-8c1b8b6f6c44",
  "name": "Ana Maria",
  "email": "ana.maria@example.com",
  "age": 31
}
```

Erros:

- (404) `Usuario nao encontrado`
- (409) `Email ja cadastrado`

### Excluir usuário

- `DELETE /usuarios/{user_id}`
- `user_id`: UUID

Resposta (204):

- corpo vazio (sem `content`)

Erros:

- (404) `Usuario nao encontrado`

## Observações de comportamento (cache)

- `GET /usuarios` é cacheado por `(limit, offset)`.
- `GET /usuarios/{user_id}` é cacheado por `user_id`.
- Após `POST`, `PUT` e `DELETE`, os caches relacionados são invalidados para manter consistência.

