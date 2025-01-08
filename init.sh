cd docker_litestar_piccolo_pg/services/backend/app
uv venv .venv
source .venv/bin/activate
uv sync
cd ../../..
cp -n ./.env.example ./.env
docker compose up --build
