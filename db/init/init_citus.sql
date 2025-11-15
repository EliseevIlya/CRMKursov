-- init_citus.sql
-- Выполняется на coordinator

-- Создаем extension citus
CREATE EXTENSION IF NOT EXISTS citus;

-- Регистрируем воркеры (имена контейнеров как в docker-compose)
SELECT * FROM master_add_node('worker1', 5432);
SELECT * FROM master_add_node('worker2', 5432);

-- Проверка (опционально)
-- SELECT * FROM master_get_active_worker_nodes();

-- Создаем таблицы (если не используем Alembic) — но Alembic сделает это.
-- Здесь можно оставить только extension + add_node, оставим создание таблиц в Alembic.
