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

2. Enter app directory:

    ```cd docker_litestar_piccolo_pg/services/backend/app```

3. Create & activate virtual environment:

    ```uv venv .venv && source .venv/bin/activate```

4. Install dependencies for local development/intellisense:

    ```uv sync```

5. Add .env file and populate with your secrets:

    ```cd ../../..```

    ```cp ./.env.example ./.env```


6. Run stack (we attach only to the backend to ignore other containers' log spam):

    ```docker compose up --build --attach backend```

7. Everything's running:

    [http://127.0.0.1:8000/schema](http://127.0.0.1:8000/schema)

8. Run migrations with Piccolo migrations:

    TODO

9. Run tests:

    `docker compose exec backend pytest`
