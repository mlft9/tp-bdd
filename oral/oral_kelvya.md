# Texte oral — Kelvya (K)

*Projet C : Système de suivi des stocks*

---

## Slide 1 — Titre

*(Maxime commence)*

Le projet consiste à construire une application de gestion de stocks, fournisseurs et commandes — en utilisant MongoDB comme base de données.

---

## Slide 2 — Présentation du sujet

*(Maxime commence)*

Ces 4 fonctionnalités sont représentatives de ce qu'un système réel devrait faire. On part de données JSON, et l'objectif est d'interroger tout ça efficacement.

---

## Slide 3 — Choix technologiques

Pour la stack technique, on a choisi MongoDB — une base NoSQL orientée documents, qui suit le modèle CP du théorème CAP. Le driver Python c'est PyMongo, et on a ajouté Flask pour exposer une interface web.

*(Maxime enchaîne)*

---

## Slide 4 — Architecture des collections

*(Maxime parle — slide de transition)*

---

## Slide 5 — Dénormalisation

C'est le choix central du projet. En SQL, on aurait eu 5 tables séparées avec des jointures partout. Là, on a fusionné certaines données directement dans les documents.

Trois décisions clés :

- Le stock est **embarqué dans `products`** — relation 1:1, toujours lus ensemble. Résultat : zéro jointure pour interroger l'état d'un stock.
- Dans `orders`, on a embarqué `product_name` et `product_unit` — ça crée un **snapshot historique** de la commande, même si le produit change plus tard.
- Dans `supplier_products`, on a embarqué `supplier_name` et `supplier_country` — pour éviter un `$lookup` sur `suppliers` à chaque requête.

*(Maxime enchaîne)*

---

## Slide 6 — Validation ($jsonSchema)

*(Maxime commence)*

Ça garantit la cohérence des données à l'insertion, sans avoir besoin d'un ORM ou de validation côté applicatif.

---

## Slide 7 — Les vues MongoDB

On a créé 3 vues en lecture seule :

- `vue_stock_status` : tous les produits avec leur statut calculé (NORMAL, BAS, CRITIQUE)
- `vue_commandes_en_attente` : commandes PENDING triées par date
- `vue_delais_fournisseurs` : fournisseurs triés par délai de livraison

*(Maxime enchaîne)*

---

## Slide 8 — F1 : État du stock

*(Maxime commence)*

Grâce au stock embarqué dans `products`, cette requête ne fait aucun `$lookup`. C'est direct.

*[démo ou capture]*

---

## Slide 9 — F2 : Commandes bloquées

La fonctionnalité 2 liste toutes les commandes PENDING dont la quantité commandée dépasse le stock disponible.

Le pipeline : `$match` sur le statut PENDING, puis `$lookup` vers `products`, puis un `$match` avec `$expr $gt` pour comparer `quantity_ordered` au `stock.quantity`.

*(Maxime enchaîne — démo ou capture)*

---

## Slide 10 — F3 : Délais fournisseurs

*(Maxime commence)*

Et là, pas de jointure du tout — grâce au `supplier_name` et `supplier_country` déjà embarqués dans `supplier_products`. On fait juste un `$match` sur `product_id` et un `$sort`.

*[démo ou capture]*

---

## Slide 11 — F4 : Date de livraison

La dernière fonctionnalité : pour une commande donnée, on renvoie soit la date réelle de livraison si elle est DELIVERED, soit une estimation basée sur le fournisseur le plus rapide disponible.

*(Maxime enchaîne — démo ou capture)*

---

## Slide 12 — Index & Optimisation

*(Maxime commence)*

On peut le montrer concrètement : avant index, MongoDB faisait un COLLSCAN — scan de toute la collection. Après, c'est un IXSCAN direct. La différence de performance est visible dans les logs `explain()`.

---

## Slide 13 — Front Web Flask

On a construit une interface web avec Flask. 4 pages correspondant aux 4 fonctionnalités, avec des formulaires simples pour entrer les IDs et voir les résultats.

*(Maxime enchaîne)*

---

## Slide 14 — Démonstration live

*(Maxime lance la démo — suivre et pointer les résultats si besoin)*

---

## Slide 15 — Conclusion

Ce projet nous a permis de comprendre concrètement ce que ça change de passer du relationnel au NoSQL. La dénormalisation, c'est pas juste une astuce — c'est une vraie décision architecturale qui conditionne toutes les requêtes.

*(Maxime enchaîne)*

Des questions ?
