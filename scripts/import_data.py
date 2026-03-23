"""
import_data.py
Importe et dénormalise les données dans MongoDB via PyMongo.

Collections créées :
  - products        : produits + stock embarqué (fusion 1:1)
  - suppliers       : fournisseurs (inchangé)
  - supplier_products : relations fournisseur-produit + nom/pays embarqués
  - orders          : commandes + snapshot produit (nom, unité)

Usage :
  pip install pymongo
  python scripts/import_data.py
"""

import json
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# ── Configuration ─────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"
DATA_DIR  = Path(__file__).parent.parent / "data"
# ──────────────────────────────────────────────────────────────

def load(filename):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)

def create_products(db):
    """Fusionne products + stock (relation 1:1)."""
    products = load("products.json")
    stocks   = load("stock.json")

    stock_by_id = {
        s["product_id"]: {
            "quantity":      s["quantity"],
            "min_threshold": s["min_threshold"],
            "last_updated":  s["last_updated"],
            "end_date":      s["end_date"],
        }
        for s in stocks
    }

    documents = [
        {
            "product_id": p["product_id"],
            "name":       p["name"],
            "category":   p["category"],
            "unit_price": p["unit_price"],
            "unit":       p["unit"],
            "stock":      stock_by_id[p["product_id"]],
        }
        for p in products
    ]

    db.products.drop()
    db.create_collection("products", validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["product_id", "name", "category", "unit_price", "unit", "stock"],
            "properties": {
                "product_id": {"bsonType": "int"},
                "name":       {"bsonType": "string", "minLength": 1},
                "category":   {"bsonType": "string", "enum": ["Electronique", "Alimentaire", "Vetement", "Outillage", "Mobilier"]},
                "unit_price": {"bsonType": "double", "minimum": 0},
                "unit":       {"bsonType": "string", "enum": ["piece", "kg", "litre", "metre", "carton"]},
                "stock": {
                    "bsonType": "object",
                    "required": ["quantity", "min_threshold", "last_updated", "end_date"],
                    "properties": {
                        "quantity":      {"bsonType": "int", "minimum": 0},
                        "min_threshold": {"bsonType": "int", "minimum": 0},
                        "last_updated":  {"bsonType": "string"},
                        "end_date":      {"bsonType": "string"},
                    }
                }
            }
        }
    })
    db.products.insert_many(documents)
    print(f"[OK] {len(documents)} produits importés (stock embarqué)")

def create_suppliers(db):
    """Importe les fournisseurs tels quels."""
    suppliers = load("suppliers.json")
    db.suppliers.drop()
    db.suppliers.insert_many(suppliers)
    print(f"[OK] {len(suppliers)} fournisseurs importés")

def create_supplier_products(db):
    """Enrichit supplier_products avec supplier_name + supplier_country."""
    sps       = load("supplier_products.json")
    suppliers = load("suppliers.json")

    supplier_by_id = {
        s["supplier_id"]: {"name": s["name"], "country": s["country"]}
        for s in suppliers
    }

    documents = [
        {
            "sp_id":            sp["sp_id"],
            "supplier_id":      sp["supplier_id"],
            "supplier_name":    supplier_by_id[sp["supplier_id"]]["name"],
            "supplier_country": supplier_by_id[sp["supplier_id"]]["country"],
            "product_id":       sp["product_id"],
            "delivery_days":    sp["delivery_days"],
            "unit_price":       sp["unit_price"],
        }
        for sp in sps
    ]

    db.supplier_products.drop()
    db.supplier_products.insert_many(documents)
    print(f"[OK] {len(documents)} relations fournisseur-produit importées (nom/pays embarqués)")

def create_orders(db):
    """Enrichit les commandes avec un snapshot produit (nom, unité)."""
    orders   = load("orders.json")
    products = load("products.json")

    product_by_id = {
        p["product_id"]: {"name": p["name"], "unit": p["unit"]}
        for p in products
    }

    documents = [
        {
            "order_id":               o["order_id"],
            "product_id":             o["product_id"],
            "product_name":           product_by_id[o["product_id"]]["name"],
            "product_unit":           product_by_id[o["product_id"]]["unit"],
            "quantity_ordered":       o["quantity_ordered"],
            "status":                 o["status"],
            "order_date":             o["order_date"],
            "expected_delivery_date": o["expected_delivery_date"],
            "actual_delivery_date":   o.get("actual_delivery_date"),
        }
        for o in orders
    ]

    db.orders.drop()
    db.orders.insert_many(documents)
    print(f"[OK] {len(documents)} commandes importées (snapshot produit embarqué)")

def main():
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]

    print(f"Connexion à {MONGO_URI} — base : {DB_NAME}\n")

    create_products(db)
    create_suppliers(db)
    create_supplier_products(db)
    create_orders(db)

    print(f"\n[OK] Import terminé. Collections dans '{DB_NAME}' :")
    for name in db.list_collection_names():
        count = db[name].count_documents({})
        print(f"   {name} : {count} documents")

    client.close()

if __name__ == "__main__":
    main()
