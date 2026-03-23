"""
app.py — Front Web Flask
Systeme de suivi des stocks — Projet C
Kelvya & Maxime

Usage :
  pip install flask pymongo
  python web/app.py
  -> http://localhost:5000
"""

import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

# Acces a queries.py dans scripts/
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from queries import etat_stock, commandes_bloquees, delais_fournisseur, date_livraison

# ── Config ────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"

app    = Flask(__name__)
client = MongoClient(MONGO_URI)
db     = client[DB_NAME]


# ── Helpers ───────────────────────────────────────────────────

def get_dashboard_stats():
    nb_produits  = db.products.count_documents({})
    nb_critiques = db.products.count_documents({
        "$expr": {"$lt": ["$stock.quantity", "$stock.min_threshold"]}
    })
    nb_pending   = db.orders.count_documents({"status": "PENDING"})
    nb_bloques   = len(commandes_bloquees(db))
    return {
        "nb_produits":  nb_produits,
        "nb_critiques": nb_critiques,
        "nb_pending":   nb_pending,
        "nb_bloques":   nb_bloques,
    }


# ── Routes ────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = get_dashboard_stats()
    return render_template("index.html", stats=stats)


@app.route("/stock", methods=["GET"])
def stock():
    pid    = request.args.get("product_id", "").strip()
    result = None
    error  = None

    if pid:
        try:
            result = etat_stock(db, int(pid))
            if not result:
                error = f"Produit {pid} introuvable."
        except ValueError:
            error = "Veuillez entrer un nombre entier."

    # Liste de tous les produits pour la liste deroulante
    produits = list(db.products.find({}, {"_id": 0, "product_id": 1, "name": 1}).sort("product_id", 1))
    return render_template("stock.html", result=result, error=error,
                           produits=produits, pid=pid)


@app.route("/commandes")
def commandes():
    resultats = commandes_bloquees(db)
    return render_template("commandes.html", commandes=resultats)


@app.route("/fournisseurs", methods=["GET"])
def fournisseurs():
    pid      = request.args.get("product_id", "").strip()
    resultats = []
    produit  = None
    error    = None

    if pid:
        try:
            pid_int   = int(pid)
            resultats = delais_fournisseur(db, pid_int)
            produit   = db.products.find_one({"product_id": pid_int}, {"_id": 0, "name": 1})
            if not produit:
                error = f"Produit {pid} introuvable."
        except ValueError:
            error = "Veuillez entrer un nombre entier."

    produits = list(db.products.find({}, {"_id": 0, "product_id": 1, "name": 1}).sort("product_id", 1))
    return render_template("fournisseurs.html", resultats=resultats, produit=produit,
                           error=error, produits=produits, pid=pid)


@app.route("/livraison", methods=["GET"])
def livraison():
    oid    = request.args.get("order_id", "").strip()
    result = None
    error  = None

    if oid:
        try:
            result = date_livraison(db, int(oid))
            if not result:
                error = f"Commande {oid} introuvable."
        except ValueError:
            error = "Veuillez entrer un nombre entier."

    return render_template("livraison.html", result=result, error=error, oid=oid)


# ── Lancement ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("Serveur Flask demarre sur http://localhost:5000")
    app.run(debug=True, port=5000)
