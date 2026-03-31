# Texte oral — Maxime (M)

*Projet C : Système de suivi des stocks*

---

## Slide 1 — Titre

Bonjour, on va vous présenter notre projet C : un système de suivi des stocks. Je m'appelle Maxime, et je suis avec Kelvya.

---

## Slide 2 — Présentation du sujet

Le contexte : on a un entrepôt avec 50 produits, 20 fournisseurs et 450 commandes. L'objectif, c'est d'implémenter 4 fonctionnalités précises :

- Connaître l'état du stock d'un produit
- Identifier les commandes bloquées faute de stock
- Consulter les délais de livraison par fournisseur
- Estimer la date de livraison d'une commande

*(Kelvya enchaîne)*

---

## Slide 3 — Choix technologiques

*(Kelvya commence)*

Le choix de MongoDB plutôt que SQL se justifie ici par la nature des données : les commandes, les stocks, les fournisseurs sont des entités qu'on lit souvent ensemble. MongoDB permet d'embarquer ces données et d'éviter les jointures coûteuses — ce qu'on va voir juste après.

---

## Slide 4 — Architecture des collections

On a structuré la base en 4 collections : `products`, `suppliers`, `supplier_products`, et `orders`. Les liens entre elles se font via des `product_id` et `supplier_id`. C'est une structure proche du relationnel, mais avec des ajustements importants grâce à la dénormalisation.

---

## Slide 5 — Dénormalisation

*(Kelvya commence)*

La collection `suppliers` elle, reste inchangée — elle est peu interrogée directement, donc pas besoin de la dénormaliser.

---

## Slide 6 — Validation ($jsonSchema)

MongoDB n'impose pas de schéma par défaut, mais on a ajouté de la validation via `$jsonSchema` sur les collections critiques. Par exemple sur `products`, on vérifie que `product_id` est bien une chaîne, que le statut est dans un enum défini, et que la quantité en stock est un entier positif.

*(Kelvya enchaîne)*

---

## Slide 7 — Les vues MongoDB

*(Kelvya commence)*

Les vues simplifient les requêtes côté Flask — au lieu de réécrire un pipeline à chaque appel, on interroge directement la vue comme si c'était une collection.

---

## Slide 8 — F1 : État du stock

La fonctionnalité 1. On passe un `product_id`, et on obtient : la quantité disponible, le seuil minimum, et un statut calculé.

Le pipeline fait un `$match` sur l'id, puis un `$project` avec un `$switch` : si la quantité est sous le seuil minimum, c'est CRITIQUE, si elle est légèrement au-dessus c'est BAS, sinon NORMAL.

*(Kelvya enchaîne — démo ou capture)*

---

## Slide 9 — Commandes bloquées

*(Kelvya commence)*

C'est la seule fonctionnalité qui nécessite encore un `$lookup` — parce qu'on n'a pas voulu embarquer le stock dans `orders` pour ne pas dupliquer une donnée qui change souvent.

*(démo ou capture)*

---

## Slide 10 — F3 : Délais fournisseurs

Pour un produit donné, on liste tous les fournisseurs qui peuvent le livrer, triés par délai croissant.

*(Kelvya enchaîne — démo ou capture)*

---

## Slide 11 — F4 : Date de livraison

*(Kelvya commence)*

La logique : on cherche d'abord si la commande est livrée. Sinon, on identifie le meilleur fournisseur pour ce produit via F3, et on calcule une date prévisionnelle.

*(démo ou capture)*

---

## Slide 12 — Index & Optimisation

On a créé 8 index pour couvrir les champs les plus interrogés. Par exemple : `product_id` (unique), `stock.quantity`, `status`, et un index composé `(status, product_id)` pour F2.

*(Kelvya enchaîne)*

---

## Slide 13 — Front Web Flask

*(Kelvya commence)*

L'architecture : Flask gère les routes, PyMongo exécute les requêtes, et les templates HTML affichent les résultats. Pour lancer : `python web/app.py`, et on ouvre `localhost:5000`.

---

## Slide 14 — Démonstration live

On va vous montrer l'interface en direct.

*[démo live : montrer les 4 pages, entrer quelques IDs, montrer les résultats]*

---

## Slide 15 — Conclusion

*(Kelvya commence)*

Les limites : les données sont mockées, il n'y a pas de mise à jour en temps réel. Si on avait plus de temps, on ajouterait des webhooks pour les alertes de stock bas, et peut-être un système de cache.
