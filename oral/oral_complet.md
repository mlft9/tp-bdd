# Texte oral — Projet C : Système de suivi des stocks

*Durée estimée : 12-15 min*
*Intervenants : M (Maxime) · K (Kelvya)*

---

## Slide 1 — Titre

**M :** Bonjour, on va vous présenter notre projet C : un système de suivi des stocks. Je m'appelle Maxime, et je suis avec Kelvya.

**K :** Le projet consiste à construire une application de gestion de stocks, fournisseurs et commandes — en utilisant MongoDB comme base de données.

---

## Slide 2 — Présentation du sujet

**M :** Le contexte : on a un entrepôt avec 50 produits, 20 fournisseurs et 450 commandes. L'objectif, c'est d'implémenter 4 fonctionnalités précises :

- Connaître l'état du stock d'un produit
- Identifier les commandes bloquées faute de stock
- Consulter les délais de livraison par fournisseur
- Estimer la date de livraison d'une commande

**K :** Ces 4 fonctionnalités sont représentatives de ce qu'un système réel devrait faire. On part de données JSON, et l'objectif est d'interroger tout ça efficacement.

---

## Slide 3 — Choix technologiques

**K :** Pour la stack technique, on a choisi MongoDB — une base NoSQL orientée documents, qui suit le modèle CP du théorème CAP. Le driver Python c'est PyMongo, et on a ajouté Flask pour exposer une interface web.

**M :** Le choix de MongoDB plutôt que SQL se justifie ici par la nature des données : les commandes, les stocks, les fournisseurs sont des entités qu'on lit souvent ensemble. MongoDB permet d'embarquer ces données et d'éviter les jointures coûteuses — ce qu'on va voir juste après.

---

## Slide 4 — Architecture des collections

**M :** On a structuré la base en 4 collections : `products`, `suppliers`, `supplier_products`, et `orders`. Les liens entre elles se font via des `product_id` et `supplier_id`. C'est une structure proche du relationnel, mais avec des ajustements importants grâce à la dénormalisation.

---

## Slide 5 — Dénormalisation

**K :** C'est le choix central du projet. En SQL, on aurait eu 5 tables séparées avec des jointures partout. Là, on a fusionné certaines données directement dans les documents.

Trois décisions clés :

- Le stock est **embarqué dans `products`** — relation 1:1, toujours lus ensemble. Résultat : zéro jointure pour interroger l'état d'un stock.
- Dans `orders`, on a embarqué `product_name` et `product_unit` — ça crée un **snapshot historique** de la commande, même si le produit change plus tard.
- Dans `supplier_products`, on a embarqué `supplier_name` et `supplier_country` — pour éviter un `$lookup` sur `suppliers` à chaque requête.

**M :** La collection `suppliers` elle, reste inchangée — elle est peu interrogée directement, donc pas besoin de la dénormaliser.

---

## Slide 6 — Validation ($jsonSchema)

**M :** MongoDB n'impose pas de schéma par défaut, mais on a ajouté de la validation via `$jsonSchema` sur les collections critiques. Par exemple sur `products`, on vérifie que `product_id` est bien une chaîne, que le statut est dans un enum défini, et que la quantité en stock est un entier positif.

**K :** Ça garantit la cohérence des données à l'insertion, sans avoir besoin d'un ORM ou de validation côté applicatif.

---

## Slide 7 — Les vues MongoDB

**K :** On a créé 3 vues en lecture seule :

- `vue_stock_status` : tous les produits avec leur statut calculé (NORMAL, BAS, CRITIQUE)
- `vue_commandes_en_attente` : commandes PENDING triées par date
- `vue_delais_fournisseurs` : fournisseurs triés par délai de livraison

**M :** Les vues simplifient les requêtes côté Flask — au lieu de réécrire un pipeline à chaque appel, on interroge directement la vue comme si c'était une collection.

---

## Slide 8 — F1 : État du stock

**M :** La fonctionnalité 1. On passe un `product_id`, et on obtient : la quantité disponible, le seuil minimum, et un statut calculé.

Le pipeline fait un `$match` sur l'id, puis un `$project` avec un `$switch` : si la quantité est sous le seuil minimum, c'est CRITIQUE, si elle est légèrement au-dessus c'est BAS, sinon NORMAL.

**K :** Grâce au stock embarqué dans `products`, cette requête ne fait aucun `$lookup`. C'est direct.

*[démo ou capture]*

---

## Slide 9 — F2 : Commandes bloquées

**K :** La fonctionnalité 2 liste toutes les commandes PENDING dont la quantité commandée dépasse le stock disponible.

Le pipeline : `$match` sur le statut PENDING, puis `$lookup` vers `products`, puis un `$match` avec `$expr $gt` pour comparer `quantity_ordered` au `stock.quantity`.
 
**M :** C'est la seule fonctionnalité qui nécessite encore un `$lookup` — parce qu'on n'a pas voulu embarquer le stock dans `orders` pour ne pas dupliquer une donnée qui change souvent.

*[démo ou capture]*

---

## Slide 10 — F3 : Délais fournisseurs

**M :** Pour un produit donné, on liste tous les fournisseurs qui peuvent le livrer, triés par délai croissant.

**K :** Et là, pas de jointure du tout — grâce au `supplier_name` et `supplier_country` déjà embarqués dans `supplier_products`. On fait juste un `$match` sur `product_id` et un `$sort`.

*[démo ou capture]*

---

## Slide 11 — F4 : Date de livraison

**K :** La dernière fonctionnalité : pour une commande donnée, on renvoie soit la date réelle de livraison si elle est DELIVERED, soit une estimation basée sur le fournisseur le plus rapide disponible.

**M :** La logique : on cherche d'abord si la commande est livrée. Sinon, on identifie le meilleur fournisseur pour ce produit via F3, et on calcule une date prévisionnelle.

*[démo ou capture]*

---

## Slide 12 — Index & Optimisation

**M :** On a créé 8 index pour couvrir les champs les plus interrogés. Par exemple : `product_id` (unique), `stock.quantity`, `status`, et un index composé `(status, product_id)` pour F2.

**K :** On peut le montrer concrètement : avant index, MongoDB faisait un COLLSCAN — scan de toute la collection. Après, c'est un IXSCAN direct. La différence de performance est visible dans les logs `explain()`.

---

## Slide 13 — Front Web Flask

**K :** On a construit une interface web avec Flask. 4 pages correspondant aux 4 fonctionnalités, avec des formulaires simples pour entrer les IDs et voir les résultats.

**M :** L'architecture : Flask gère les routes, PyMongo exécute les requêtes, et les templates HTML affichent les résultats. Pour lancer : `python web/app.py`, et on ouvre `localhost:5000`.

---

## Slide 14 — Démonstration live

**M :** On va vous montrer l'interface en direct.

*[démo live : montrer les 4 pages, entrer quelques IDs, montrer les résultats]*

---

## Slide 15 — Conclusion

**K :** Ce projet nous a permis de comprendre concrètement ce que ça change de passer du relationnel au NoSQL. La dénormalisation, c'est pas juste une astuce — c'est une vraie décision architecturale qui conditionne toutes les requêtes.

**M :** Les limites : les données sont mockées, il n'y a pas de mise à jour en temps réel. Si on avait plus de temps, on ajouterait des webhooks pour les alertes de stock bas, et peut-être un système de cache.

**K :** Des questions ?
