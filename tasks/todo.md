# Plan TP MongoDB — Projet C : Système de suivi des stocks

**Groupe : Kelvya + Maxime**
**Sujet :** Système pour gérer des informations sur les stocks, les fournisseurs et les commandes.

---

## Rendu attendu

- Présentation PowerPoint de la solution proposée
- Démonstration fonctionnelle en Python (pilote natif PyMongo)

---

## Fonctionnalités obligatoires (Projet C)

- [ ] État des stocks d'un produit
- [ ] Si une commande est en attente car pas de stock
- [ ] Délais de livraison d'un fournisseur pour un produit
- [ ] Date de livraison d'une commande par rapport au dernier produit à livrer

---

## Phase 1 — Architecture & Modélisation

> Décider comment structurer les données dans MongoDB

- [ ] 1.1 Analyser les collections existantes (`products`, `suppliers`, `stock`, `supplier_products`, `orders`) et leurs relations
- [ ] 1.2 Décider de la dénormalisation : quelles données fusionner dans un même document pour éviter les jointures ?
  - Ex : imbriquer les infos fournisseur dans `supplier_products` ?
  - Ex : imbriquer le stock courant dans `products` ?
- [ ] 1.3 Justifier les choix d'architecture (à inclure dans le PowerPoint)
- [ ] 1.4 Ajouter la validation des documents (`$jsonSchema`) sur au moins une collection

---

## Phase 2 — Vues MongoDB

> Créer des vues pour simplifier les requêtes fréquentes

- [ ] 2.1 Vue "état des stocks" — produits avec quantité, seuil min, et statut (normal / bas / critique)
- [ ] 2.2 Vue "commandes en attente" — commandes PENDING avec infos produit
- [ ] 2.3 Vue "délais fournisseurs" — fournisseurs par produit avec `delivery_days`

---

## Phase 3 — Scripts de requêtes & Agrégations

> Les 4 fonctionnalités clés demandées par le sujet

- [ ] 3.1 État du stock d'un produit — quantité actuelle vs seuil minimum
- [ ] 3.2 Commandes en attente car stock insuffisant — commandes PENDING dont `quantity_ordered > stock.quantity`
- [ ] 3.3 Délai de livraison d'un fournisseur pour un produit — via `supplier_products`
- [ ] 3.4 Date de livraison d'une commande — basée sur le dernier produit à livrer (pipeline d'agrégation avec `$lookup`, `$group`, `$max`)

---

## Phase 4 — Index & Optimisation

> Démontrer la maîtrise des index (notion clé du cours)

- [ ] 4.1 Identifier les champs fréquemment requêtés (`product_id`, `status`, `supplier_id`, etc.)
- [ ] 4.2 Créer les index appropriés (simples, composés)
- [ ] 4.3 Utiliser `explain()` pour montrer COLLSCAN → IXSCAN avant/après index

---

## Phase 5 — Front Python (PyMongo)

> Interface fonctionnelle pour la démonstration

- [ ] 5.1 Connexion MongoDB avec PyMongo
- [ ] 5.2 Implémenter les 4 fonctionnalités du Projet C
- [ ] 5.3 Interface console ou menu interactif (pas besoin d'une vraie UI)
- [ ] 5.4 Préparer la démonstration live avec les données importées

---

## Phase 6 — Rendu Final

- [ ] 6.1 Présentation PowerPoint couvrant :
  - Choix d'architecture + dénormalisation justifiée
  - Schéma des collections
  - Exemples de requêtes / agrégations
  - Démonstration des index (avant/après `explain()`)
- [ ] 6.2 Démo live du front Python

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
