pushd ./services/backend/app
uv venv .venv
source .venv/bin/activate
uv sync
popd
cp -n ./.env.example ./.env
docker compose up --build
