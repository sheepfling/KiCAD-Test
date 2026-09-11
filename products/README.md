# Product integration folders

Products are optional. A standalone board only needs its project island.
When several boards form an assembly, create `products/<id>/product.json` and register
it in `catalog/products.json`, declaring the IDs of its participating projects.

Keep integration documentation, mechanical references, harness definitions and
`tests/test_*.py` alongside that product. Root CI and checks for any participating
board execute its tests. Other JSON files in its docs/tests/releases folders are
not mistaken for product definitions.

Generated variant BOMs, system/connection views and harness schedules go into that
product's ignored `build/` directory. Authored assembly definitions stay in Git;
retain exact release artifacts according to the [BOM policy](../docs/workflow/BOM_POLICY.md).
See [product workflow](../docs/workflow/PRODUCT_WORKFLOW.md) and the
[reference system](../examples/products/status-indicator-system/README.md).
