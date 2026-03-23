// =============================================================
// 04_import_supplier_products.js
// Enrichit supplier_products avec supplier_name + supplier_country
// Évite un $lookup sur suppliers à chaque requête de délai fournisseur
// Usage : mongosh tp_stock scripts/04_import_supplier_products.js
// =============================================================

// ⚠️ Modifie DATA_DIR si ton projet est ailleurs
const DATA_DIR = "D:/Documents/Cours/bdd/tp-k/data";

const supplierProducts = JSON.parse(fs.readFileSync(`${DATA_DIR}/supplier_products.json`, "utf8"));
const suppliers        = JSON.parse(fs.readFileSync(`${DATA_DIR}/suppliers.json`,         "utf8"));

// Index fournisseurs par supplier_id
const supplierById = {};
for (const s of suppliers) {
  supplierById[s.supplier_id] = { name: s.name, country: s.country };
}

// Fusionne : ajoute supplier_name et supplier_country
const documents = supplierProducts.map(sp => {
  const sup = supplierById[sp.supplier_id] || { name: "Inconnu", country: "Inconnu" };
  return {
    sp_id:            NumberInt(sp.sp_id),
    supplier_id:      NumberInt(sp.supplier_id),
    supplier_name:    sup.name,
    supplier_country: sup.country,
    product_id:       NumberInt(sp.product_id),
    delivery_days:    NumberInt(sp.delivery_days),
    unit_price:       sp.unit_price
  };
});

const result = db.supplier_products.insertMany(documents);
print(`✅ ${result.insertedIds ? Object.keys(result.insertedIds).length : 0} relations fournisseur-produit importées`);

// La collection suppliers est importée telle quelle (pas de dénormalisation)
const suppliersData = JSON.parse(fs.readFileSync(`${DATA_DIR}/suppliers.json`, "utf8"));
const suppDocs = suppliersData.map(s => ({
  supplier_id:       NumberInt(s.supplier_id),
  name:              s.name,
  email:             s.email,
  phone:             s.phone,
  country:           s.country,
  avg_delivery_days: NumberInt(s.avg_delivery_days)
}));
db.suppliers.insertMany(suppDocs);
print(`✅ ${suppDocs.length} fournisseurs importés`);

// Vérification rapide
const sample = db.supplier_products.findOne({ supplier_id: NumberInt(1) });
print("Exemple (supplier_id=1) :");
printjson(sample);
