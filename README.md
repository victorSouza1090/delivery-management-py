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
- **Alembic**: Ferramenta de versionamento e migração de banco de dados
- **RabbitMQ**: fila de eventos
- **Workers**: processamento assíncrono do fluxo de pedidos
- **Outbox Pattern**: garante consistência entre banco e fila
- **Logs estruturados**: rastreamento de eventos e falhas
- **Observabilidade(Prometheus+Grafana)**: exposição de metricas
- **Testes unitários e de integração**: arquitetura de testes baseada em `pytest`, com separação entre testes unitários (regras de negócio, validação) e testes de integração (API, workers, mensageria, persistência), todos orquestrados via Docker Compose para garantir isolamento e confiabilidade


## Justificativa das Tecnologias

- **FastAPI**: Escolhida pela alta performance, tipagem forte, facilidade de integração com Pydantic e excelente suporte a APIs assíncronas.
- **SQLAlchemy Async**: Permite operações assíncronas e escaláveis com PostgreSQL, garantindo maior throughput e menor latência no acesso ao banco.
- **RabbitMQ**: Utilizada como fila de eventos pela robustez, confiabilidade e suporte a padrões de mensageria, essencial para desacoplamento e escalabilidade.
- **Docker e Docker Compose**: Facilitam o isolamento dos serviços, reprodutibilidade do ambiente e automação dos testes de integração.
- **Prometheus/Grafana**: Permitem monitoramento detalhado do sistema e dos workers, facilitando observabilidade e diagnóstico.

## Estratégia de Consistência, Latência e Resiliência

- O sistema utiliza o padrão Outbox para garantir que eventos publicados na fila estejam sempre sincronizados com o estado do banco, evitando perda de dados mesmo em caso de falha.
- Confirmação de escrita e retries são aplicados tanto na persistência dos pedidos quanto na publicação dos eventos, garantindo consistência total.
- Idempotência é aplicada nos workers e publishers, evitando duplicidade de eventos e garantindo processamento confiável.
- O processamento assíncrono via workers e mensageria reduz a latência entre a criação do pedido e a atualização dos status/eventos.
- O ambiente orquestrado via Docker Compose permite recuperação rápida e isolada dos serviços, tornando o sistema resiliente a falhas e reinícios.

## Estratégia de Testes

- O projeto utiliza `pytest` para execução dos testes.
- Testes unitários cobrem regras de negócio, validação de dados e funções isoladas dos serviços e repositórios.
- Testes de integração validam o funcionamento completo da API, workers, mensageria e persistência, simulando cenários reais de criação de pedidos, processamento assíncrono e consulta de eventos.
- O ambiente de integração é orquestrado via `docker-compose-test.yml`, garantindo que banco, RabbitMQ, API e workers estejam disponíveis e isolados.
- Fixtures e factories são usadas para criar dados de teste e garantir idempotência.
- A cobertura dos testes é gerada automaticamente e pode ser consultada via artefato no CI.
- Os testes garantem que o sistema é resiliente, consistente e que nenhum evento ou estado é perdido, mesmo em caso de falha.

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
"id": "uuid",
"customer_name": "João Silva",
"address": "Rua Exemplo, 123",
"status": "RECEIVED",
"created_at": "2025-11-03T00:32:55.534780Z"
}
```
### Consultar status atual
```json
GET /orders/{order_id}
Response:
{
"id": "793491aa-5958-4c3f-b51d-d8abf83eef12",
"customer_name": "João Silva",
"address": "Rua A, 123",
"status": "DELIVERED",
"created_at": "2025-11-02T01:46:47.087816Z"
}
```
### Consultar histórico de eventos
```json
GET /orders/{order_id}/events
Response:
[
    {
        "id": "c854b8a2-fef2-4407-a7d8-3a88c71b5cc8",
        "order_id": "58a3df14-0c77-4c55-b38e-06e10b1d5373",
        "status": "RECEIVED",
        "timestamp": "2025-11-03T00:19:36.502902Z"
    },
    {
        "id": "d5daae51-fcd0-4137-90a9-8ca7881202d0",
        "order_id": "58a3df14-0c77-4c55-b38e-06e10b1d5373",
        "status": "IN_TRANSIT",
        "timestamp": "2025-11-03T00:19:37.681178Z"
    },
    {
        "id": "75a771a4-a5f3-433a-a536-6c439d79890f",
        "order_id": "58a3df14-0c77-4c55-b38e-06e10b1d5373",
        "status": "DELIVERED",
        "timestamp": "2025-11-03T00:19:39.661796Z"
    }
]
```
## Requisitos técnicos

- Python 3.11, FastAPI, Pydantic
- PostgreSQL (persistência de pedidos e eventos)
- RabbitMQ (fila de eventos)
- SQLAlchemy Async para ORM assíncrono
- Alembic para versionamento e migração do schema do banco
- Docker e Docker Compose
- Arquitetura orientada a eventos
- Event sourcing / Outbox Pattern para consistência banco ↔ fila
- Logs estruturados para rastreabilidade e monitoramento
- Exposição de metricas para monitoramento com Prometheus e Grafana

## Rodando o projeto

1. Crie o `.env` com as variáveis de ambiente 
2. Suba os containers: docker-compose up --build
3. Acesse a API: [http://localhost:8000/docs](http://localhost:8000/docs)

## Rodando migrations

1. O projeto utiliza Alembic para versionamento e migração do banco de dados. Para aplicar as migrations, execute:
```bash
alembic upgrade head
```
2. As migrations estão localizadas em /migrations/versions

## Rodando os testes
1. Para executar os testes execute o comando
```bash
docker compose -f docker-compose-test.yml up --build --exit-code-from tests tests
```
2. Será levantado uma aplicação, banco de dados, mensageria, worker, publisher. Com os container processando será executado os testes unitários, integração e cobertura.

## Monitoramento

O projeto inclui integração com Prometheus e Grafana Cloud para monitoramento das métricas da API e dos workers.

- O arquivo `prometheus.yml.template` permite gerar a configuração dinâmica do Prometheus usando variáveis do `.env`.
- O arquivo `prometheus.yml` precisa ser gerado antes de subir o container Prometheus.
- O serviço Prometheus é orquestrado pelo `docker-compose.yml` e expõe métricas em `http://localhost:9090`.
- Um exemplo de dashboard está disponivél no arquivo grafana.yaml.

Para gerar o arquivo de configuração do Prometheus:
```bash
export $(grep -E '^PROMETHEUS_USER=|^PROMETHEUS_PASSWORD=' .env | xargs) && envsubst < prometheus.yml.template > prometheus.yml
```

## Arquitetura de pastas
```
delivery-management-py/
├── app/
│   ├── main.py               # Ponto de entrada da API FastAPI
│   ├── core/
│   │   ├── config.py         # Configurações globais
│   │   ├── logging_config.py # Configuração de logs estruturados
│   │   └── exceptions/       # Exceções customizadas
│   ├── db/
│   │   ├── database.py       # Configuração do SQLAlchemy Async
│   │   ├── migrations/       # Scripts de migração do banco (Alembic)
│   │   └── seed/             # Scripts de seed do banco
│   ├── dto/
│   │   └── outbox_event_dto.py # DTO para eventos do outbox
│   ├── middlewares/
│   │   └── logging_middleware.py # Middleware para logs
│   ├── models/
│   │   ├── order.py          # Model de Pedido
│   │   ├── order_event.py    # Model de Evento de Pedido
│   │   └── outbox_event.py   # Model de Evento Outbox
│   ├── repositories/
│   │   ├── order_repository_interface.py # Interface do repositório de pedidos
│   │   ├── outbox_event_repository_interface.py # Interface do repositório de outbox
│   │   └── impl/
│   │       ├── order_repository.py      # Implementação do repositório de pedidos
│   │       └── outbox_event_repository.py # Implementação do repositório de outbox
│   ├── schemas/
│   │   └── order_schema.py   # Schemas Pydantic para pedidos
│   ├── services/
│   │   └── order_service.py  # Regras de negócio de pedidos
│   ├── api/
│   │   └── routes/
│   │       └── orders.py     # Rotas da API de pedidos
│   ├── workers/
│   │   ├── interfaces.py     # Interfaces de workers/publishers
│   │   ├── outbox.py         # Worker de publicação de eventos do outbox
│   │   ├── worker.py         # Worker de processamento de eventos
│   │   └── rabbitmq/
│   │       ├── rabbitmq_worker.py    # Worker RabbitMQ
│   │       └── rabbitmq_publisher.py # Publisher RabbitMQ
│   └── dependencies.py       # Injeção de dependências para FastAPI/Workers
├── tests/
│   ├── conftest.py           # Fixtures globais de teste
│   ├── integration/
│   │   ├── factories.py      # Factories para dados de teste
│   │   ├── test_create_order.py
│   │   ├── test_get_events.py
│   │   └── test_get_order.py
│   └── unit/
│       ├── test_order_repository.py
│       ├── test_order_service.py
│       ├── test_order_status_life_cycle.py
│       ├── test_outbox_event_repository.py
│       └── workers/
│           ├── test_outbox.py
│           └── test_worker.py
├── .env                      # Variáveis de ambiente do projeto
├── Dockerfile                # Imagem do serviço FastAPI
├── docker-compose.yml        # Orquestração dos containers (API, DB, RabbitMQ, Prometheus)
├── docker-compose-test.yml   # Orquestração dos containers para testes
├── prometheus.yml            # Configuração final do Prometheus (gerada via template)
├── prometheus.yml.template   # Template para configuração dinâmica do Prometheus
├── grafana.yaml              # Exemplo de dashboard Grafana
├── logging.yaml              # Configuração de logs
├── requirements.txt          # Dependências do projeto
├── setup.py                  # Setup do projeto
├── wait-for-it.sh            # Script para aguardar serviços
```
