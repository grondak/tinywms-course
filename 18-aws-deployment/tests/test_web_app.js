const assert = require('node:assert');
const { test } = require('node:test');

function inventoryUrl(baseUrl) {
  return `${baseUrl.replace(/\/$/, '')}/inventory`;
}

function ordersUrl(baseUrl) {
  return `${baseUrl.replace(/\/$/, '')}/orders`;
}

test('inventoryUrl strips a trailing slash', () => {
  assert.equal(inventoryUrl('http://example.com/'), 'http://example.com/inventory');
});

test('inventoryUrl leaves a base url unchanged', () => {
  assert.equal(inventoryUrl('https://api.example.com'), 'https://api.example.com/inventory');
});

test('ordersUrl strips a trailing slash', () => {
  assert.equal(ordersUrl('http://example.com/'), 'http://example.com/orders');
});
