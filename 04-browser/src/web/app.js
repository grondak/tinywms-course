async function loadInventory() {
  const status = document.getElementById('status');
  const body = document.getElementById('inventory-body');
  try {
    const response = await fetch('/inventory');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    body.innerHTML = '';
    for (const item of data.inventory) {
      const row = document.createElement('tr');
      row.innerHTML = `<td>${item.sku}</td><td>${item.description}</td><td>${item.bin}</td><td>${item.quantity} ${item.unit}</td>`;
      body.appendChild(row);
    }
    status.textContent = `Loaded ${data.inventory.length} products.`;
  } catch (error) {
    status.textContent = `Failed to load inventory: ${error.message}`;
  }
}
loadInventory();
