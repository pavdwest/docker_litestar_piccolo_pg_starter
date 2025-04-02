# Dockerised Litestar Piccolo PostGres Stack

A dockerised starter stack containing the following components:

* [LiteStar](https://litestar.dev/) backend
* [Granian Server](https://github.com/emmett-framework/granian) via [https://github.com/cofin/litestar-granian](https://github.com/cofin/litestar-granian)
* [Postgres](https://www.postgresql.org/) database
* [Piccolo ORM](https://piccolo-orm.readthedocs.io/en/latest/#) (Async)
* [Msgspec](https://jcristharif.com/msgspec/) Validations
* Generic Model Base Class
* Generic Crud Controller generator


## Pre-Requisites

1. [UV Package Manager](https://github.com/astral-sh/uv)
2. [Docker](https://docs.docker.com/get-started/get-docker/)


## Getting Started

TODO

1. Clone repo:

    ```git clone git@github.com:pavdwest/docker_litestar_piccolo_pg.git```

2. Create .env file and populate with your own secrets:

    ```cp docker_litestar_piccolo_pg/.env.example docker_litestar_piccolo_pg/.env```

3. Enter app directory:

    ```cd docker_litestar_piccolo_pg/services/backend/app```

4. Create & activate virtual environment (only required for local development):

    ```uv venv .venv && source .venv/bin/activate && uv sync```

5. Run stack (we attach only to the backend to ignore other containers' log spam):

    ```docker compose up --build --attach backend```

6. Everything's running:

    [http://127.0.0.1:8000/schema](http://127.0.0.1:8000/schema)

7. Run migrations with Piccolo migrations:

    TODO

8. Run tests:

    `docker compose exec backend pytest`
