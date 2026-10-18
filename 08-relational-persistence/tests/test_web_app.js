import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const app = readFileSync(resolve(root, 'src/web/app.js'), 'utf8');
const index = readFileSync(resolve(root, 'src/web/index.html'), 'utf8');
const style = readFileSync(resolve(root, 'src/web/style.css'), 'utf8');

test('browser inventory uses same-origin or a runtime override', () => {
  assert.match(app, /window\.TINYWMS_API_BASE_URL/);
  assert.match(app, /window\.location\.origin/);
  assert.match(app, /new URL\('\/inventory'/);
  assert.doesNotMatch(app, /127\.0\.0\.1:8000/);
});

test('inventory page renders inventory rows from GET /inventory', () => {
  assert.match(app, /fetch\(inventoryUrl\)/);
  assert.match(app, /inventory-body/);
  assert.match(app, /renderInventory/);
  assert.match(index, /id="inventory-body"/);
  assert.match(index, /Refresh inventory/);
  assert.match(style, /table/);
});

test('inventory page shows visible failures', () => {
  assert.match(app, /Failed to load inventory/);
  assert.match(app, /error\.textContent = err\.message/);
  assert.match(index, /id="error"/);
});
