# TP MongoDB — Projet C : Système de suivi des stocks

**Groupe :** Kelvya & Maxime
**Cours :** Optimisation BDD NoSQL
**Sujet :** Système pour gérer des informations sur les stocks, les fournisseurs et les commandes.

---

## Prérequis

- Python 3.10+
- MongoDB en local (`localhost:27017`)
- MongoDB Compass (optionnel, pour visualiser les données)

```bash
pip install flask pymongo
```

---

## Structure du projet

```
tp-k/
├── data/                        # Données source (JSON)
│   ├── products.json            # 50 produits
│   ├── suppliers.json           # 20 fournisseurs
│   ├── supplier_products.json   # 100 relations fournisseur-produit
│   ├── stock.json               # 50 entrées de stock
│   └── orders.json              # 450 commandes
│
├── scripts/                     # Scripts Python/MongoDB
│   ├── import_data.py           # Import + dénormalisation → MongoDB
│   ├── views.py                 # Création des 3 vues MongoDB
│   ├── indexes.py               # Création des index + démonstration explain()
│   ├── queries.py               # 4 fonctions d'agrégation (logique métier)
│   └── app.py                   # (ancien) menu console — remplacé par web/
│
└── web/                         # Front web Flask
    ├── app.py                   # Serveur Flask (routes)
    ├── static/
    │   └── style.css
    └── templates/
        ├── base.html
        ├── index.html           # Dashboard
        ├── stock.html           # F1 : état du stock
        ├── commandes.html       # F2 : commandes bloquées
        ├── fournisseurs.html    # F3 : délais fournisseurs
        └── livraison.html       # F4 : date de livraison
```

---

## Mise en place

### 1. Importer les données

```bash
python scripts/import_data.py
```

Crée la base `tp_stock` avec 4 collections dénormalisées :

| Collection | Documents | Dénormalisation |
|---|---|---|
| `products` | 50 | Stock embarqué (fusion 1:1) |
| `suppliers` | 20 | Inchangée |
| `supplier_products` | 100 | `supplier_name` + `supplier_country` embarqués |
| `orders` | 200 | `product_name` + `product_unit` embarqués (snapshot) |

### 2. Créer les vues

```bash
python scripts/views.py
```

Crée 3 vues en lecture seule :

| Vue | Description |
|---|---|
| `vue_stock_status` | Produits avec statut calculé (normal / bas / critique) |
| `vue_commandes_en_attente` | Commandes PENDING triées par date |
| `vue_delais_fournisseurs` | Relations fournisseur-produit triées par délai |

### 3. Créer les index

```bash
python scripts/indexes.py
```

Crée 8 index et affiche la démonstration COLLSCAN → IXSCAN pour chaque.

### 4. Lancer le front web

```bash
python web/app.py
```

Ouvrir **http://localhost:5000** dans le navigateur.

---

## Fonctionnalités (Projet C)

### F1 — État du stock d'un produit
- Route : `/stock?product_id=<id>`
- Affiche : quantité, seuil minimum, statut (NORMAL / BAS / CRITIQUE)
- Requête directe sans jointure grâce au stock embarqué dans `products`

### F2 — Commandes bloquées (stock insuffisant)
- Route : `/commandes`
- Affiche toutes les commandes PENDING dont `quantity_ordered > stock.quantity`
- Pipeline : `$match` → `$lookup` → `$unwind` → `$match $expr` → `$project`

### F3 — Délais de livraison par fournisseur
- Route : `/fournisseurs?product_id=<id>`
- Liste tous les fournisseurs pour un produit, triés par délai croissant
- Sans jointure grâce à `supplier_name`/`supplier_country` embarqués

### F4 — Date de livraison d'une commande
- Route : `/livraison?order_id=<id>`
- Si livrée : affiche la date réelle
- Sinon : affiche la date prévue + le fournisseur le plus rapide disponible

---

## Architecture — Choix de dénormalisation

Le schéma de départ est relationnel (5 tables normalisées). MongoDB n'étant pas optimisé pour les jointures, 3 fusions ont été appliquées :

| Décision | Justification |
|---|---|
| `stock` → `products` | Relation 1:1, toujours interrogés ensemble. Élimine tout `$lookup` pour F1 et F2. |
| `supplier_name/country` → `supplier_products` | Évite un `$lookup` sur `suppliers` à chaque requête F3. Coût faible (2 champs). |
| `product_name/unit` → `orders` | Capture le nom produit au moment de la commande (historique). Réduit les lookups. |
| `suppliers` conservée | Données de référence peu interrogées directement. |

---

## Index créés

| Collection | Index | Type |
|---|---|---|
| `products` | `product_id` | Simple, unique |
| `products` | `stock.quantity` | Simple |
| `products` | `category` | Simple |
| `orders` | `status` | Simple |
| `orders` | `product_id` | Simple |
| `orders` | `(status, product_id)` | Composé |
| `supplier_products` | `product_id` | Simple |
| `supplier_products` | `supplier_id` | Simple |
