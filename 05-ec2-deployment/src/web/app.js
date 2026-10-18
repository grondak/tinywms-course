const apiBase = window.TINYWMS_API_BASE_URL || window.location.origin;
const inventoryUrl = new URL('/inventory', apiBase).toString();
const status = document.getElementById('status');
const body = document.getElementById('inventory-body');
const error = document.getElementById('error');
const refreshButton = document.getElementById('refresh-button');
const apiBaseLabel = document.getElementById('api-base');

apiBaseLabel.textContent = apiBase;

function renderInventory(items) {
  status.textContent = `Loaded ${items.length} items`;
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${item.sku}</td>
          <td>${item.description}</td>
          <td>${item.bin_location}</td>
          <td>${item.quantity}</td>
          <td>${item.unit}</td>
        </tr>`,
    )
    .join('');
}

function loadInventory() {
  error.textContent = '';
  status.textContent = 'Loading inventory...';
  return fetch(inventoryUrl)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(renderInventory)
    .catch((err) => {
      status.textContent = 'Failed to load inventory';
      error.textContent = err.message;
    });
}

refreshButton.addEventListener('click', loadInventory);
loadInventory();
