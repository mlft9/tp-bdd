"""
views.py — Phase 2
Cree les 3 vues MongoDB pour le systeme de suivi des stocks.

Usage : python scripts/views.py
"""

from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"


def drop_view_if_exists(db, name):
    if name in db.list_collection_names():
        db.drop_collection(name)


def create_vue_stock_status(db):
    """
    vue_stock_status — etat de chaque produit avec statut calcule :
      - critique : quantite < seuil_min
      - bas       : quantite < seuil_min * 2
      - normal    : sinon
    """
    drop_view_if_exists(db, "vue_stock_status")
    db.command("create", "vue_stock_status", viewOn="products", pipeline=[
        {
            "$addFields": {
                "statut": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$lt": ["$stock.quantity", "$stock.min_threshold"]},
                                "then": "critique"
                            },
                            {
                                "case": {"$lt": ["$stock.quantity", {"$multiply": ["$stock.min_threshold", 2]}]},
                                "then": "bas"
                            }
                        ],
                        "default": "normal"
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "product_id": 1,
                "name": 1,
                "category": 1,
                "quantite": "$stock.quantity",
                "seuil_min": "$stock.min_threshold",
                "statut": 1
            }
        },
        {"$sort": {"statut": 1, "product_id": 1}}
    ])
    print("[OK] Vue 'vue_stock_status' creee")


def create_vue_commandes_en_attente(db):
    """
    vue_commandes_en_attente — commandes avec status PENDING,
    enrichies du nom produit (deja embarque dans orders).
    """
    drop_view_if_exists(db, "vue_commandes_en_attente")
    db.command("create", "vue_commandes_en_attente", viewOn="orders", pipeline=[
        {"$match": {"status": "PENDING"}},
        {
            "$project": {
                "_id": 0,
                "order_id": 1,
                "product_id": 1,
                "product_name": 1,
                "product_unit": 1,
                "quantity_ordered": 1,
                "order_date": 1,
                "expected_delivery_date": 1
            }
        },
        {"$sort": {"order_date": 1}}
    ])
    print("[OK] Vue 'vue_commandes_en_attente' creee")


def create_vue_delais_fournisseurs(db):
    """
    vue_delais_fournisseurs — tous les couples fournisseur/produit
    tries par delai de livraison croissant.
    Utile pour trouver rapidement le fournisseur le plus rapide.
    """
    drop_view_if_exists(db, "vue_delais_fournisseurs")
    db.command("create", "vue_delais_fournisseurs", viewOn="supplier_products", pipeline=[
        {
            "$project": {
                "_id": 0,
                "product_id": 1,
                "supplier_id": 1,
                "supplier_name": 1,
                "supplier_country": 1,
                "delivery_days": 1,
                "unit_price": 1
            }
        },
        {"$sort": {"product_id": 1, "delivery_days": 1}}
    ])
    print("[OK] Vue 'vue_delais_fournisseurs' creee")


def main():
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]

    print(f"Connexion a {MONGO_URI} — base : {DB_NAME}\n")

    create_vue_stock_status(db)
    create_vue_commandes_en_attente(db)
    create_vue_delais_fournisseurs(db)

    print("\nVues disponibles :")
    views = [c for c in db.list_collection_names() if c.startswith("vue_")]
    for v in sorted(views):
        count = db[v].count_documents({})
        print(f"  {v} : {count} documents")

    client.close()


if __name__ == "__main__":
    main()
