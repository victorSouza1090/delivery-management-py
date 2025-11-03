# Delivery Service API

Sistema de gerenciamento de entregas orientado a eventos, desenvolvido em FastAPI, com processamento assíncrono de pedidos e publicação de eventos via RabbitMQ.

## Funcionalidades

- Criar novos pedidos via API REST
- Processamento assíncrono do fluxo de entrega (separação, transporte, entrega)
- Emissão de eventos a cada mudança de status do pedido
- Persistência dos pedidos e histórico completo de eventos
- Consulta do status atual e histórico de eventos de um pedido

## Arquitetura

- **FastAPI**: API principal
- **SQLAlchemy Async**: ORM assíncrono para PostgreSQL
- **RabbitMQ**: fila de eventos
- **Workers**: processamento assíncrono do fluxo de pedidos
- **Outbox Pattern**: garante consistência entre banco e fila
- **Logs estruturados**: rastreamento de eventos e falhas

## Endpoints

### Criar pedido
```json
POST /orders
Body:
{
"customer_name": "João Silva",
"address": "Rua Exemplo, 123"
}
Response:
{
"order_id": "uuid",
"status": "RECEIVED"
}
```
### Consultar status atual
```json
GET /orders/{order_id}
Response:
{
"order_id": "uuid",
"status": "IN_TRANSIT"
}
```
### Consultar histórico de eventos
```json
GET /orders/{order_id}/events
Response:
[
{"status": "RECEIVED", "timestamp": "2025-11-01T20:00:00Z"},
{"status": "IN_TRANSIT", "timestamp": "2025-11-01T20:05:00Z"},
{"status": "DELIVERED", "timestamp": "2025-11-01T20:30:00Z"}
]
```
## Requisitos técnicos

- Python 3.11, FastAPI, Pydantic
- PostgreSQL (persistência de pedidos e eventos)
- RabbitMQ (fila de eventos)
- SQLAlchemy Async para ORM assíncrono
- Docker e Docker Compose
- Arquitetura orientada a eventos
- Event sourcing / Outbox Pattern para consistência banco ↔ fila
- Logs estruturados para rastreabilidade e monitoramento

## Rodando o projeto

1. Crie o `.env` com as variáveis de ambiente 
2. Suba os containers: docker-compose up --build
3. Acesse a API: [http://localhost:8000/docs](http://localhost:8000/docs)

## Arquitetura de pastas
```
delivery-management-py/
├── app/
│   ├── main.py               # Ponto de entrada da API FastAPI
│   ├── core/                 # Configurações globais do projeto (ex: config.py)
│   ├── workers/              # Workers e publishers para mensageria (RabbitMQ, etc)
│   ├── db/
│   │   ├── database.py       # Configuração do SQLAlchemy Async
│   │   └── migrations/       # Scripts de migração do banco
│   ├── models/               # Definição das entidades/tabelas ORM
│   ├── schemas/              # Schemas Pydantic para validação de dados
│   ├── repositories/         # Interfaces e implementações de acesso a dados
│   │   ├── impl/             # Implementações concretas dos repositórios
│   ├── services/             # Regras de negócio e orquestração
│   ├── api/
│   │   └── routes/           # Rotas/endpoints da API
│   └── dependencies.py       # Injeção de dependências para FastAPI/Workers
├── .env                      # Variáveis de ambiente do projeto
├── Dockerfile                # Imagem do serviço FastAPI
├── docker-compose.yml        # Orquestração dos containers (API, DB, RabbitMQ)
```