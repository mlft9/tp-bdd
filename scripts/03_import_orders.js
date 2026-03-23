// =============================================================
// 03_import_orders.js
// Enrichit chaque commande avec un snapshot du produit :
//   product_name et product_unit (capturés au moment de l'import)
// Usage : mongosh tp_stock scripts/03_import_orders.js
// =============================================================

// ⚠️ Modifie DATA_DIR si ton projet est ailleurs
const DATA_DIR = "D:/Documents/Cours/bdd/tp-k/data";

const orders   = JSON.parse(fs.readFileSync(`${DATA_DIR}/orders.json`,   "utf8"));
const products = JSON.parse(fs.readFileSync(`${DATA_DIR}/products.json`, "utf8"));

// Index produits par product_id
const productById = {};
for (const p of products) {
  productById[p.product_id] = { name: p.name, unit: p.unit };
}

// Fusionne : ajoute product_name et product_unit dans chaque commande
const documents = orders.map(o => {
  const prod = productById[o.product_id] || { name: "Inconnu", unit: "piece" };
  return {
    order_id:               NumberInt(o.order_id),
    product_id:             NumberInt(o.product_id),
    product_name:           prod.name,
    product_unit:           prod.unit,
    quantity_ordered:       NumberInt(o.quantity_ordered),
    status:                 o.status,
    order_date:             o.order_date,
    expected_delivery_date: o.expected_delivery_date,
    actual_delivery_date:   o.actual_delivery_date || null
  };
});

const result = db.orders.insertMany(documents);
print(`✅ ${result.insertedIds ? Object.keys(result.insertedIds).length : 0} commandes importées avec snapshot produit`);

// Vérification rapide
const sample = db.orders.findOne({ status: "DELIVERED" });
print("Exemple (première commande DELIVERED) :");
printjson(sample);
