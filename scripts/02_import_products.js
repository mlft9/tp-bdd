// =============================================================
// 02_import_products.js
// Fusionne products.json + stock.json en une seule collection
// Le stock est embarqué dans chaque document produit (1:1)
// Usage : mongosh tp_stock 02_import_products.js
// =============================================================

// ⚠️ Modifie DATA_DIR si ton projet est ailleurs
const DATA_DIR = "D:/Documents/Cours/bdd/tp-k/data";

const products = JSON.parse(fs.readFileSync(`${DATA_DIR}/products.json`, "utf8"));
const stocks    = JSON.parse(fs.readFileSync(`${DATA_DIR}/stock.json`,    "utf8"));

// Construit un index stock par product_id pour les lookups O(1)
const stockByProductId = {};
for (const s of stocks) {
  stockByProductId[s.product_id] = {
    quantity:      s.quantity,
    min_threshold: s.min_threshold,
    last_updated:  s.last_updated,
    end_date:      s.end_date
  };
}

// Fusionne et prépare les documents dénormalisés
const documents = products.map(p => ({
  product_id: NumberInt(p.product_id),
  name:       p.name,
  category:   p.category,
  unit_price: p.unit_price,
  unit:       p.unit,
  stock:      {
    quantity:      NumberInt(stockByProductId[p.product_id].quantity),
    min_threshold: NumberInt(stockByProductId[p.product_id].min_threshold),
    last_updated:  stockByProductId[p.product_id].last_updated,
    end_date:      stockByProductId[p.product_id].end_date
  }
}));

// Insère dans la collection
const result = db.products.insertMany(documents);
print(`✅ ${result.insertedIds ? Object.keys(result.insertedIds).length : 0} produits importés avec stock embarqué`);

// Vérification rapide
const sample = db.products.findOne({ product_id: NumberInt(1) });
print("Exemple (product_id=1) :");
printjson(sample);
