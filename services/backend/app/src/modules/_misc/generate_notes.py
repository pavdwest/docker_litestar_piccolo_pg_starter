# import json

# from polyfactory.factories.pydantic_factory import ModelFactory

# # This file is in services/backend/app/src/modules/_misc/generate_products.py
# # Import product model from services/backend/app/src/models.py



# class ProductFactory(ModelFactory[Product]):
#     ...


# n = 1000

# # Generate n products to file as json array
# products = ProductFactory.batch(n)

# # Write to file
# with open('products.json', 'w') as f:
#     json.dump(products, f)

import json
import time


# Product model
product_example = {
    'title': 'test_product_title',
    'description': 'test_product_description',
    'price': 5.0
}

# Generate 10000 products each with title suffixed by id to file as json array
products = []
start = time.monotonic()
for i in range(100000):
    products.append(
        {
            'title': f'test_product_title_{i}',
            'description': 'test_product_description',
            'price': 5.0
        }
    )

with open('product.json', 'w') as f:
    json.dump(products, f)

print(f'Took {time.monotonic() - start} seconds')
# Curl to put to localhost:8000/api/v1/product/many
# curl -X POST -H "Content-Type: application/json" -d @product.json http://localhost:8000/api/v1/product/many
# 12.4s for 100_000 = 100_000 / 12.4 = 8_000 rows/s
