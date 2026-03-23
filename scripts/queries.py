"""
queries.py — Phase 3
4 fonctions d'agregation pour le systeme de suivi des stocks.

Fonctionnalites du Projet C :
  F1 : etat_stock          — etat du stock d'un produit
  F2 : commandes_bloquees  — commandes PENDING avec stock insuffisant
  F3 : delais_fournisseur  — delais de livraison par fournisseur pour un produit
  F4 : date_livraison      — date de livraison d'une commande
"""

from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"


# ── F1 : Etat du stock d'un produit ──────────────────────────────────────────

def etat_stock(db, product_id: int) -> dict | None:
    """
    Retourne l'etat du stock pour un produit donne.
    Requete directe sans jointure grace a la denormalisation (stock embarque).

    Pipeline :
      - $match  : filtre par product_id
      - $project : champs utiles + calcul du statut
    """
    pipeline = [
        {"$match": {"product_id": product_id}},
        {
            "$project": {
                "_id": 0,
                "product_id": 1,
                "nom": "$name",
                "categorie": "$category",
                "quantite": "$stock.quantity",
                "seuil_min": "$stock.min_threshold",
                "derniere_maj": "$stock.last_updated",
                "statut": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$lt": ["$stock.quantity", "$stock.min_threshold"]},
                                "then": "CRITIQUE — reapprovisionnement urgent"
                            },
                            {
                                "case": {
                                    "$lt": [
                                        "$stock.quantity",
                                        {"$multiply": ["$stock.min_threshold", 2]}
                                    ]
                                },
                                "then": "BAS — surveiller"
                            }
                        ],
                        "default": "NORMAL"
                    }
                }
            }
        }
    ]
    results = list(db.products.aggregate(pipeline))
    return results[0] if results else None


# ── F2 : Commandes bloquees par manque de stock ───────────────────────────────

def commandes_bloquees(db) -> list:
    """
    Retourne les commandes PENDING dont la quantite commandee
    depasse le stock disponible.

    Pipeline :
      - $match   : status = PENDING
      - $lookup  : joint products sur product_id
      - $unwind  : deplie le tableau produit
      - $match   : quantity_ordered > produit.stock.quantity
      - $project : champs pertinents
      - $sort    : par date de commande
    """
    pipeline = [
        {"$match": {"status": "PENDING"}},
        {
            "$lookup": {
                "from": "products",
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "produit"
            }
        },
        {"$unwind": "$produit"},
        {
            "$match": {
                "$expr": {"$gt": ["$quantity_ordered", "$produit.stock.quantity"]}
            }
        },
        {
            "$project": {
                "_id": 0,
                "order_id": 1,
                "product_id": 1,
                "produit": "$product_name",
                "quantite_commandee": "$quantity_ordered",
                "stock_disponible": "$produit.stock.quantity",
                "manque": {"$subtract": ["$quantity_ordered", "$produit.stock.quantity"]},
                "date_commande": "$order_date",
                "livraison_prevue": "$expected_delivery_date"
            }
        },
        {"$sort": {"date_commande": 1}}
    ]
    return list(db.orders.aggregate(pipeline))


# ── F3 : Delais de livraison par fournisseur pour un produit ─────────────────

def delais_fournisseur(db, product_id: int) -> list:
    """
    Retourne tous les fournisseurs pour un produit,
    tries par delai de livraison croissant.
    Pas de jointure grace a supplier_name/country embarques.

    Pipeline :
      - $match  : filtre par product_id
      - $project : champs utiles
      - $sort   : delivery_days croissant
    """
    pipeline = [
        {"$match": {"product_id": product_id}},
        {
            "$project": {
                "_id": 0,
                "fournisseur": "$supplier_name",
                "pays": "$supplier_country",
                "delai_jours": "$delivery_days",
                "prix_unitaire": "$unit_price"
            }
        },
        {"$sort": {"delai_jours": 1}}
    ]
    return list(db.supplier_products.aggregate(pipeline))


# ── F4 : Date de livraison d'une commande ─────────────────────────────────────

def date_livraison(db, order_id: int) -> dict | None:
    """
    Retourne les informations de livraison d'une commande.
    Si livree : retourne la date reelle.
    Si en cours : retourne la date prevue + le fournisseur le plus rapide.

    Pour les commandes non livrees, enrichit avec le fournisseur
    le plus rapide disponible pour ce produit (min delivery_days).
    """
    order = db.orders.find_one(
        {"order_id": order_id},
        {"_id": 0, "order_id": 1, "product_id": 1, "product_name": 1,
         "quantity_ordered": 1, "status": 1, "order_date": 1,
         "expected_delivery_date": 1, "actual_delivery_date": 1}
    )
    if not order:
        return None

    result = {
        "order_id":          order["order_id"],
        "produit":           order["product_name"],
        "quantite":          order["quantity_ordered"],
        "statut":            order["status"],
        "date_commande":     order["order_date"],
        "livraison_prevue":  order["expected_delivery_date"],
        "livraison_reelle":  order.get("actual_delivery_date"),
    }

    # Si pas encore livree, trouver le fournisseur le plus rapide
    if order["status"] != "DELIVERED":
        meilleur = db.supplier_products.find_one(
            {"product_id": order["product_id"]},
            {"_id": 0, "supplier_name": 1, "supplier_country": 1, "delivery_days": 1},
            sort=[("delivery_days", 1)]
        )
        if meilleur:
            result["fournisseur_plus_rapide"] = meilleur["supplier_name"]
            result["pays_fournisseur"]        = meilleur["supplier_country"]
            result["delai_fournisseur_jours"] = meilleur["delivery_days"]

    return result


# ── Test direct ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pprint
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]

    print("=== F1 : Etat du stock — produit 1 ===")
    pprint.pprint(etat_stock(db, 1))

    print("\n=== F2 : Commandes bloquees (stock insuffisant) ===")
    resultats = commandes_bloquees(db)
    print(f"{len(resultats)} commande(s) bloquee(s)")
    for r in resultats[:3]:
        pprint.pprint(r)

    print("\n=== F3 : Delais fournisseurs — produit 1 ===")
    pprint.pprint(delais_fournisseur(db, 1))

    print("\n=== F4 : Date de livraison — commande 1 ===")
    pprint.pprint(date_livraison(db, 1))

    client.close()
