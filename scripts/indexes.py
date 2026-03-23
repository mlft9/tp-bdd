"""
indexes.py — Phase 4
Cree les index sur les collections et demontre leur impact
avec explain() : COLLSCAN -> IXSCAN.

Usage : python scripts/indexes.py
"""

from pymongo import MongoClient, ASCENDING

MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"


def get_winning_stage(db, collection: str, query: dict) -> str:
    """Retourne le type de plan gagnant (COLLSCAN, IXSCAN, etc.)."""
    result = db.command("explain", {
        "find": collection,
        "filter": query
    }, verbosity="queryPlanner")
    plan = result.get("queryPlanner", {}).get("winningPlan", {})
    # Cherche recursivement le stage de base
    while "inputStage" in plan:
        plan = plan["inputStage"]
    return plan.get("stage", "INCONNU")


def demo_explain(db, collection: str, query: dict, label: str):
    """Affiche le plan avant et apres creation d'index."""
    avant = get_winning_stage(db, collection, query)
    print(f"  {label}")
    print(f"    Avant index : {avant}")


def create_indexes(db):
    print("=== Creation des index ===\n")

    # ── products ──────────────────────────────────────────────
    print("-- Collection : products")

    demo_explain(db, "products", {"product_id": 1}, "Recherche par product_id")
    db.products.create_index([("product_id", ASCENDING)], unique=True, name="idx_product_id")
    apres = get_winning_stage(db, "products", {"product_id": 1})
    print(f"    Apres  index idx_product_id : {apres}\n")

    demo_explain(db, "products", {"stock.quantity": {"$lt": 20}}, "Stock faible (quantity < seuil)")
    db.products.create_index([("stock.quantity", ASCENDING)], name="idx_stock_quantity")
    apres = get_winning_stage(db, "products", {"stock.quantity": {"$lt": 20}})
    print(f"    Apres  index idx_stock_quantity : {apres}\n")

    demo_explain(db, "products", {"category": "Electronique"}, "Filtre par categorie")
    db.products.create_index([("category", ASCENDING)], name="idx_category")
    apres = get_winning_stage(db, "products", {"category": "Electronique"})
    print(f"    Apres  index idx_category : {apres}\n")

    # ── orders ────────────────────────────────────────────────
    print("-- Collection : orders")

    demo_explain(db, "orders", {"status": "PENDING"}, "Filtre par statut")
    db.orders.create_index([("status", ASCENDING)], name="idx_order_status")
    apres = get_winning_stage(db, "orders", {"status": "PENDING"})
    print(f"    Apres  index idx_order_status : {apres}\n")

    demo_explain(db, "orders", {"product_id": 1}, "Recherche par product_id")
    db.orders.create_index([("product_id", ASCENDING)], name="idx_order_product_id")
    apres = get_winning_stage(db, "orders", {"product_id": 1})
    print(f"    Apres  index idx_order_product_id : {apres}\n")

    demo_explain(db, "orders",
                 {"status": "PENDING", "product_id": 1},
                 "Index compose (status, product_id) — utilise par F2")
    db.orders.create_index(
        [("status", ASCENDING), ("product_id", ASCENDING)],
        name="idx_order_status_product"
    )
    apres = get_winning_stage(db, "orders", {"status": "PENDING", "product_id": 1})
    print(f"    Apres  index idx_order_status_product : {apres}\n")

    # ── supplier_products ─────────────────────────────────────
    print("-- Collection : supplier_products")

    demo_explain(db, "supplier_products", {"product_id": 1}, "Recherche par product_id")
    db.supplier_products.create_index([("product_id", ASCENDING)], name="idx_sp_product_id")
    apres = get_winning_stage(db, "supplier_products", {"product_id": 1})
    print(f"    Apres  index idx_sp_product_id : {apres}\n")

    demo_explain(db, "supplier_products", {"supplier_id": 1}, "Recherche par supplier_id")
    db.supplier_products.create_index([("supplier_id", ASCENDING)], name="idx_sp_supplier_id")
    apres = get_winning_stage(db, "supplier_products", {"supplier_id": 1})
    print(f"    Apres  index idx_sp_supplier_id : {apres}\n")


def list_indexes(db):
    print("=== Index en place ===\n")
    for col in ["products", "orders", "supplier_products"]:
        print(f"-- {col} :")
        for idx in db[col].list_indexes():
            name = idx["name"]
            key  = dict(idx["key"])
            unique = " [unique]" if idx.get("unique") else ""
            print(f"   {name} : {key}{unique}")
        print()


def main():
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]

    print(f"Connexion a {MONGO_URI} — base : {DB_NAME}\n")
    create_indexes(db)
    list_indexes(db)
    client.close()


if __name__ == "__main__":
    main()
