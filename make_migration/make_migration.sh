docker compose up -d --wait
cd ..
uv run alembic revision --autogenerate
cd make_migration
docker compose down
