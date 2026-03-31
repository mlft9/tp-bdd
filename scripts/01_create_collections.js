// =============================================================
// 01_create_collections.js
// Drop et recrée les 4 collections avec validation $jsonSchema
// Usage : mongosh tp_stock 01_create_collections.js
// =============================================================

// ---------- products ----------
db.products.drop();
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["product_id", "name", "category", "unit_price", "unit", "stock"],
      properties: {
        product_id: {
          bsonType: "int",
          description: "Identifiant unique du produit — requis, entier"
        },
        name: {
          bsonType: "string",
          minLength: 1,
          description: "Nom du produit — requis, non vide"
        },
        category: {
          bsonType: "string",
          enum: ["Electronique", "Alimentaire", "Vetement", "Outillage", "Mobilier"],
          description: "Catégorie — doit être une valeur autorisée"
        },
        unit_price: {
          bsonType: "double",
          minimum: 0,
          exclusiveMinimum: true,
          description: "Prix unitaire catalogue — requis, > 0"
        },
        unit: {
          bsonType: "string",
          enum: ["piece", "kg", "litre", "metre", "carton"],
          description: "Unité de mesure — doit être une valeur autorisée"
        },
        stock: {
          bsonType: "object",
          required: ["quantity", "min_threshold", "last_updated", "end_date"],
          properties: {
            quantity: {
              bsonType: "int",
              minimum: 0,
              description: "Quantité en stock — entier >= 0"
            },
            min_threshold: {
              bsonType: "int",
              minimum: 0,
              description: "Seuil minimum de réapprovisionnement — entier >= 0"
            },
            last_updated: {
              bsonType: "string",
              description: "Date de dernière mise à jour (YYYY-MM-DD)"
            },
            end_date: {
              bsonType: "string",
              description: "Date de fin de validité du stock (YYYY-MM-DD)"
            }
          }
        }
      }
    }
  },
  validationAction: "error",
  validationLevel: "strict"
});
print("✓ Collection 'products' créée avec validation $jsonSchema");

// ---------- suppliers ----------
db.suppliers.drop();
db.createCollection("suppliers");
print("✓ Collection 'suppliers' créée");

// ---------- supplier_products ----------
db.supplier_products.drop();
db.createCollection("supplier_products");
print("✓ Collection 'supplier_products' créée");

// ---------- orders ----------
db.orders.drop();
db.createCollection("orders");
print("✓ Collection 'orders' créée");

print("\n✅ Toutes les collections sont prêtes. Lance 02, 03, 04 pour importer les données.");

