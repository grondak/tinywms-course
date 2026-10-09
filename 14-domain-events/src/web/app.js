function inventoryUrl(baseUrl) {
  return `${baseUrl.replace(/\/$/, '')}/inventory`;
}

function ordersUrl(baseUrl) {
  return `${baseUrl.replace(/\/$/, '')}/orders`;
}

async function loadInventory() {
  const status = document.getElementById('status');
  const body = document.getElementById('inventory-body');
  const baseUrl = document.getElementById('base-url').value;
  try {
    const response = await fetch(inventoryUrl(baseUrl));
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
    status.textContent = `Loaded ${data.inventory.length} products from ${baseUrl}.`;
  } catch (error) {
    status.textContent = `Failed to load inventory from ${baseUrl}: ${error.message}`;
  }
}

function orderPayloadFromForm() {
  return {
    customer: document.getElementById('order-customer').value,
    lines: [
      {
        sku: document.getElementById('order-sku').value,
        quantity: Number(document.getElementById('order-quantity').value)
      }
    ]
  };
}

async function submitOrder() {
  const result = document.getElementById('order-result');
  const payloadEl = document.getElementById('order-json');
  const baseUrl = document.getElementById('base-url').value;
  const payload = orderPayloadFromForm();
  payloadEl.textContent = JSON.stringify(payload, null, 2);

  try {
    const response = await fetch(ordersUrl(baseUrl), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    result.textContent = `HTTP ${response.status}\n${JSON.stringify(data, null, 2)}`;
    if (response.ok) {
      await loadInventory();
    }
  } catch (error) {
    result.textContent = `Order request failed: ${error.message}`;
  }
}

document.getElementById('reload-button').addEventListener('click', loadInventory);
document.getElementById('submit-order-button').addEventListener('click', submitOrder);
loadInventory();
