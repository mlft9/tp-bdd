# Plan TP MongoDB — Projet C : Système de suivi des stocks

**Groupe : Kelvya + Maxime**
**Sujet :** Système pour gérer des informations sur les stocks, les fournisseurs et les commandes.

---

## Rendu attendu

- Présentation PowerPoint de la solution proposée
- Démonstration fonctionnelle en Python (pilote natif PyMongo)

---

## Fonctionnalités obligatoires (Projet C)

- [x] État des stocks d'un produit → `queries.py::etat_stock()`
- [x] Si une commande est en attente car pas de stock → `queries.py::commandes_bloquees()`
- [x] Délais de livraison d'un fournisseur pour un produit → `queries.py::delais_fournisseur()`
- [x] Date de livraison d'une commande → `queries.py::date_livraison()`

---

## Phase 1 — Architecture & Modélisation ✅

- [x] 1.1 Analyser les collections existantes
- [x] 1.2 Dénormalisation : `stock` dans `products`, snapshot produit dans `orders`, nom/pays dans `supplier_products`
- [x] 1.3 Architecture justifiée (5 collections → 4)
- [x] 1.4 Validation `$jsonSchema` sur `products`
- **Script :** `scripts/import_data.py`

---

## Phase 2 — Vues MongoDB ✅

- [x] 2.1 `vue_stock_status` — statut critique / bas / normal
- [x] 2.2 `vue_commandes_en_attente` — commandes PENDING
- [x] 2.3 `vue_delais_fournisseurs` — triée par delivery_days
- **Script :** `scripts/views.py`

---

## Phase 3 — Agrégations ✅

- [x] 3.1 `etat_stock(db, product_id)` — stock embarqué, 0 jointure
- [x] 3.2 `commandes_bloquees(db)` — PENDING + `$lookup` + `$expr $gt`
- [x] 3.3 `delais_fournisseur(db, product_id)` — sans jointure
- [x] 3.4 `date_livraison(db, order_id)` — livraison réelle ou prévue + meilleur fournisseur
- **Script :** `scripts/queries.py`

---

## Phase 4 — Index & Optimisation ✅

- [x] 4.1 Index sur `product_id`, `stock.quantity`, `category` (products)
- [x] 4.2 Index sur `status`, `product_id`, composé `(status, product_id)` (orders)
- [x] 4.3 Index sur `product_id`, `supplier_id` (supplier_products)
- [x] 4.4 Démonstration COLLSCAN → IXSCAN via `explain()`
- **Script :** `scripts/indexes.py`

---

## Phase 5 — Front Python ✅

- [x] 5.1 Connexion PyMongo partagée
- [x] 5.2 4 fonctionnalités implémentées via `queries.py`
- [x] 5.3 Menu console interactif avec saisie utilisateur
- **Script :** `scripts/app.py`

---

## Phase 6 — Rendu Final

- [ ] 6.1 Présentation PowerPoint :
  - Schéma des collections + dénormalisation justifiée
  - Exemples de requêtes / pipelines d'agrégation
  - Captures COLLSCAN → IXSCAN (depuis `indexes.py`)
- [ ] 6.2 Démo live : `python scripts/app.py`

---

## Répartition suggérée

| Partie                          | Kelvya | Maxime |
|---------------------------------|--------|--------|
| Architecture & dénormalisation  | ✓      | ✓ (ensemble) |
| Vues + Validation               | ✓      |        |
| Scripts agrégations             |        | ✓      |
| Index + explain                 | ✓      |        |
| Front Python                    |        | ✓      |
| PowerPoint                      | ✓      | ✓ (ensemble) |

---

## Données disponibles (déjà importées dans MongoDB)

| Collection          | Documents | Description |
|---------------------|-----------|-------------|
| `products`          | 50        | Produits avec catégorie et prix |
| `suppliers`         | 20        | Fournisseurs européens |
| `supplier_products` | 100       | Relations fournisseur ↔ produit (N-N) |
| `stock`             | 50        | Inventaire avec seuil minimum |
| `orders`            | 450       | Commandes (PENDING / CONFIRMED / DELIVERED / CANCELLED) |
