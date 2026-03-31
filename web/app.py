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
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient

# Acces a queries.py dans scripts/
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from queries import etat_stock, commandes_bloquees, delais_fournisseur, date_livraison

# ── Config ────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"

app    = Flask(__name__)
app.secret_key = "tp_stock_secret"
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

    produits = list(db.products.find({}, {"_id": 0, "product_id": 1, "name": 1}).sort("product_id", 1))
    return render_template("stock.html", result=result, error=error,
                           produits=produits, pid=pid)


@app.route("/stock/update", methods=["POST"])
def stock_update():
    pid      = request.form.get("product_id", "").strip()
    quantite = request.form.get("quantite", "").strip()
    try:
        pid_int = int(pid)
        qty_int = int(quantite)
        if qty_int < 0:
            raise ValueError
        res = db.products.update_one(
            {"product_id": pid_int},
            {"$set": {"stock.quantity": qty_int, "stock.last_updated": __import__("datetime").date.today().isoformat()}}
        )
        if res.matched_count == 0:
            flash(f"Produit {pid_int} introuvable.", "error")
        else:
            flash(f"Stock mis a jour : {qty_int} unites.", "success")
    except ValueError:
        flash("Valeurs invalides.", "error")
    return redirect(url_for("stock", product_id=pid))


@app.route("/commandes")
def commandes():
    resultats = commandes_bloquees(db)
    return render_template("commandes.html", commandes=resultats)


@app.route("/commandes/<int:order_id>/statut", methods=["POST"])
def commandes_update_statut(order_id):
    nouveau_statut = request.form.get("statut", "").strip()
    statuts_valides = {"PENDING", "CONFIRMED", "DELIVERED", "CANCELLED"}
    if nouveau_statut not in statuts_valides:
        flash("Statut invalide.", "error")
        return redirect(url_for("commandes"))
    update = {"$set": {"status": nouveau_statut}}
    if nouveau_statut == "DELIVERED":
        update["$set"]["actual_delivery_date"] = __import__("datetime").date.today().isoformat()
    db.orders.update_one({"order_id": order_id}, update)
    flash(f"Commande #{order_id} mise a jour : {nouveau_statut}.", "success")
    return redirect(url_for("commandes"))


@app.route("/commandes/nouvelle", methods=["GET", "POST"])
def commandes_nouvelle():
    produits = list(db.products.find({}, {"_id": 0, "product_id": 1, "name": 1, "stock.quantity": 1}).sort("product_id", 1))
    if request.method == "POST":
        try:
            pid = int(request.form["product_id"])
            qty = int(request.form["quantity_ordered"])
            if qty <= 0:
                raise ValueError
            import datetime
            today    = datetime.date.today()
            expected = today + datetime.timedelta(days=7)
            last_order = db.orders.find_one(sort=[("order_id", -1)])
            new_id = (last_order["order_id"] + 1) if last_order else 1
            db.orders.insert_one({
                "order_id":               new_id,
                "product_id":             pid,
                "product_name":           next((p["name"] for p in produits if p["product_id"] == pid), "Inconnu"),
                "product_unit":           "piece",
                "quantity_ordered":       qty,
                "status":                 "PENDING",
                "order_date":             today.isoformat(),
                "expected_delivery_date": expected.isoformat(),
                "actual_delivery_date":   None,
            })
            flash(f"Commande #{new_id} creee avec succes.", "success")
            return redirect(url_for("commandes"))
        except (ValueError, KeyError):
            flash("Donnees invalides.", "error")
    return render_template("commandes_nouvelle.html", produits=produits)


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
