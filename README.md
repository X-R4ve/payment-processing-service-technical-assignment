## Обзор

Решение тестового задания. Представляет собой асинхронный сервис процессинга 
платежей. Сервис принимает запросы на оплату, обрабатывает их через внешний 
платёжный шлюз и уведомляет клиента о результате через webhook.

## Архитектура

Сервис (FastAPI) принимает запрос на оплату. Обработка платежей осуществляется 
асинхронно: событие публикуется в outbox, после чего вычитывается worker-ом 
(FastStream) из БД и отправляется в очередь (RabbitMQ). Далее consumer 
(FastStream) читает сообщения из очереди, обрабатывает платёж и обновляет статус 
платежа в БД. В случае трёх неудачных попыток обработки платёж получает статус 
'failed', событие отправляется в Dead Letter Queue.

## Эндпоинты

**1.** `POST /api/v1/payments` - создание платежа

Обязательные заголовки:
- X-API-Key - ключ аутентификации (строка, default="testapikey")
- Idempotency-Key - произвольная строка для гарантии идемпотентности запроса

Тело запроса:
```json
{
  "amount": 9.99,
  "currency": "USD",
  "description": "some description",
  "metadata": {
    "some_metadata_field": "some string"
  },
  "webhook_url": "https://example.com/webhook-endpoint"
}
```
Обязательные поля: amount, currency, webhook_url.

Тело ответа:
```json
{
  "payment_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending",
  "created_at": "2026-10-07T08:36:08.960Z"
}
```
Пример запроса:
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: testapikey" \
  -H "Idempotency-Key: 7f3b7c2e-6f5e-4e7a-9e6e-123456789abc" \
  -d '{
    "amount": 9.99,
    "currency": "USD",
    "description": "some description",
    "metadata": {
      "some_metadata_field": "some string"
      },
    "webhook_url": "https://example.com/webhook-endpoint" 
  }'
```

**2.** `GET /api/v1/payments/{payment_id}` - запрос информации о платеже

Обязательные заголовки:
- X-API-Key - ключ аутентификации (строка, default="testapikey")

Тело ответа:
```json
{
  "payment_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "amount": "549.99",
  "currency": "RUB",
  "description": "some description",
  "metadata": {
    "some_metadata_field": "some string"
  },
  "webhook_url": "https://example.com/webhook-endpoint",
  "status": "succeeded",
  "created_at": "2026-10-07T08:36:08.960Z",
  "processed_at": "2026-10-07T08:36:08.960Z"
}
```
Пример запроса:
```bash
curl -X GET "http://localhost:8000/api/v1/payments/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "X-API-Key: testapikey"
```

## Технологии

- **Язык:** python (версия 3.14)
- **API-фреймворк:** FastAPI
- **База данных:** PostgreSQL
- **Миграции:** Alembic
- **Контейнеризация:** Docker (+ Compose)
- **Брокер сообщений:** RabbitMQ
- **Фоновые задачи:** FastStream

## Основные паттерны

- Clean architecture
- Repository
- Transactional outbox
- Idempotency key
- Use case
- Dependency injection

## Запуск

Для запуска в системе должен быть установлен docker (+ compose). Запуск начнётся 
со сборки docker-образа, если он не был собран ранее. Запуск:
```bash
./run.sh
```
Миграции при старте применяются автоматически через одноразовый сервис migration.

Swagger-документация: `http://localhost:8000/api/v1/docs`.

Остановка:
```bash
./stop.sh
./remove_image.sh # Удалить docker-образ
```
