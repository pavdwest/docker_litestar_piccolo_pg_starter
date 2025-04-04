import random
import json
from pathlib import Path


script_folder = Path(__file__).parent
print(script_folder)


def generate_create(
    start_id: int = 1,
    n: int = 1000,
):
    items = []
    for i in range(start_id, n+start_id):
        items.append(
            {
                "title": f"Product Title {i}",
                "description": f"Product Description {i}",
                "active": (True if random.random() > 0.5 else False),
                "price": round(random.random() * 100, 2) + 0.01,
            }
        )

    # Save to file
    with open(Path.joinpath(script_folder, "create.json"), "w") as f:
        f.write(json.dumps(items, indent=4))


def generate_updates(
    start_id: int = 1,
    n: int = 1000,
):
    items = []
    for i in range(start_id, n+start_id):
        items.append(
            {
                "id": i ,
                "title": f"Product Title {i} Updated",
                "description": f"Product Description {i} Updated",
                "active": (True if random.random() > 0.5 else False),
                "price": round(random.random() * 100, 2) + 0.01,
            }
        )

    # Save to file
    with open(Path.joinpath(script_folder, "update.json"), "w") as f:
        f.write(json.dumps(items, indent=4))


n = 10000
start_id = 1
generate_create(start_id, n)
generate_updates(start_id, n)

# Curl Create
# curl -X POST -H "Content-Type: application/json" -d @./services/backend/app/src/modules/product/seeds/create.json http://localhost:8000/api/v1/product/many

# Curl Update
# curl -X PATCH -H "Content-Type: application/json" -d @./services/backend/app/src/modules/product/seeds/update.json http://localhost:8000/api/v1/product/many
