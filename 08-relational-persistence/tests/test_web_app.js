const assert = require('node:assert');
const { test } = require('node:test');

function inventoryUrl(baseUrl) {
  return `${baseUrl.replace(/\/$/, '')}/inventory`;
}

test('inventoryUrl strips a trailing slash', () => {
  assert.equal(inventoryUrl('http://example.com/'), 'http://example.com/inventory');
});

test('inventoryUrl leaves a base url unchanged', () => {
  assert.equal(inventoryUrl('https://api.example.com'), 'https://api.example.com/inventory');
});
