"""
app.py — Phase 5
Interface console PyMongo pour le systeme de suivi des stocks.
Projet C — Kelvya & Maxime

Usage : python scripts/app.py
"""

from pymongo import MongoClient
from queries import etat_stock, commandes_bloquees, delais_fournisseur, date_livraison

MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "tp_stock"

SEP  = "-" * 55
SEP2 = "=" * 55


def afficher_titre(titre: str):
    print(f"\n{SEP2}")
    print(f"  {titre}")
    print(SEP2)


def afficher_separateur():
    print(SEP)


# ── Option 1 : Etat du stock ──────────────────────────────────

def menu_etat_stock(db):
    afficher_titre("ETAT DU STOCK D'UN PRODUIT")
    try:
        pid = int(input("  Entrez le product_id (1-50) : "))
    except ValueError:
        print("  [Erreur] Entrez un nombre entier.")
        return

    res = etat_stock(db, pid)
    if not res:
        print(f"  Produit {pid} introuvable.")
        return

    print()
    print(f"  Produit     : {res['nom']} (ID {res['product_id']})")
    print(f"  Categorie   : {res['categorie']}")
    print(f"  Quantite    : {res['quantite']} unites")
    print(f"  Seuil min   : {res['seuil_min']} unites")
    print(f"  Derniere MAJ: {res['derniere_maj']}")
    print(f"  Statut      : {res['statut']}")


# ── Option 2 : Commandes bloquees ─────────────────────────────

def menu_commandes_bloquees(db):
    afficher_titre("COMMANDES EN ATTENTE — STOCK INSUFFISANT")
    resultats = commandes_bloquees(db)

    if not resultats:
        print("  Aucune commande bloquee. Tous les stocks sont suffisants.")
        return

    print(f"  {len(resultats)} commande(s) bloquee(s) :\n")
    for r in resultats:
        afficher_separateur()
        print(f"  Commande #{r['order_id']} — {r['produit']}")
        print(f"    Quantite commandee : {r['quantite_commandee']}")
        print(f"    Stock disponible   : {r['stock_disponible']}")
        print(f"    Manque             : {r['manque']} unites")
        print(f"    Date commande      : {r['date_commande']}")
        print(f"    Livraison prevue   : {r['livraison_prevue']}")
    afficher_separateur()


# ── Option 3 : Delais fournisseurs ────────────────────────────

def menu_delais_fournisseur(db):
    afficher_titre("DELAIS DE LIVRAISON PAR FOURNISSEUR")
    try:
        pid = int(input("  Entrez le product_id (1-50) : "))
    except ValueError:
        print("  [Erreur] Entrez un nombre entier.")
        return

    # Nom du produit
    produit = db.products.find_one({"product_id": pid}, {"_id": 0, "name": 1})
    if not produit:
        print(f"  Produit {pid} introuvable.")
        return

    resultats = delais_fournisseur(db, pid)
    if not resultats:
        print(f"  Aucun fournisseur pour le produit {pid}.")
        return

    print(f"\n  Produit : {produit['name']} (ID {pid})")
    print(f"  {len(resultats)} fournisseur(s) disponible(s) :\n")
    afficher_separateur()
    for i, r in enumerate(resultats, 1):
        label = " <- le plus rapide" if i == 1 else ""
        print(f"  {i}. {r['fournisseur']} ({r['pays']})")
        print(f"     Delai : {r['delai_jours']} jour(s){label}")
        print(f"     Prix  : {r['prix_unitaire']:.2f} EUR/unite")
    afficher_separateur()


# ── Option 4 : Date de livraison ──────────────────────────────

def menu_date_livraison(db):
    afficher_titre("DATE DE LIVRAISON D'UNE COMMANDE")
    try:
        oid = int(input("  Entrez le order_id (1-200) : "))
    except ValueError:
        print("  [Erreur] Entrez un nombre entier.")
        return

    res = date_livraison(db, oid)
    if not res:
        print(f"  Commande {oid} introuvable.")
        return

    print()
    print(f"  Commande    : #{res['order_id']}")
    print(f"  Produit     : {res['produit']}")
    print(f"  Quantite    : {res['quantite']}")
    print(f"  Statut      : {res['statut']}")
    print(f"  Commandee le: {res['date_commande']}")
    print(f"  Livr. prevue: {res['livraison_prevue']}")

    if res['livraison_reelle']:
        print(f"  Livr. reelle: {res['livraison_reelle']}  [LIVREE]")
    else:
        print(f"  Livr. reelle: en attente")
        if "fournisseur_plus_rapide" in res:
            print(f"\n  Fournisseur le plus rapide disponible :")
            print(f"    {res['fournisseur_plus_rapide']} ({res['pays_fournisseur']})")
            print(f"    Delai : {res['delai_fournisseur_jours']} jour(s)")


# ── Menu principal ────────────────────────────────────────────

def afficher_menu():
    print(f"\n{SEP2}")
    print("  SYSTEME DE SUIVI DES STOCKS")
    print("  Projet C — BDD NoSQL / MongoDB")
    print(SEP2)
    print("  1. Etat du stock d'un produit")
    print("  2. Commandes bloquees (stock insuffisant)")
    print("  3. Delais de livraison par fournisseur")
    print("  4. Date de livraison d'une commande")
    print("  5. Quitter")
    print(SEP)


def main():
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]

    actions = {
        "1": menu_etat_stock,
        "2": menu_commandes_bloquees,
        "3": menu_delais_fournisseur,
        "4": menu_date_livraison,
    }

    while True:
        afficher_menu()
        choix = input("  Votre choix : ").strip()

        if choix == "5":
            print("\n  Au revoir !")
            break
        elif choix in actions:
            actions[choix](db)
            try:
                input("\n  [Appuyez sur Entree pour continuer]")
            except EOFError:
                break
        else:
            print("  Choix invalide. Entrez un nombre entre 1 et 5.")

    client.close()


if __name__ == "__main__":
    main()
