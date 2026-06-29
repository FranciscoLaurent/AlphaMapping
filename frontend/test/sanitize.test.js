/**
 * sanitize.js 单元测试（Node 环境运行）
 *
 * 运行方式：node frontend/test/sanitize.test.js
 */
const { escapeHtml, escapeAttr } = require('../lib/sanitize.js');

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    passed++;
    console.log(`  ✓ ${label}`);
  } else {
    failed++;
    console.error(`  ✗ ${label}`);
  }
}

console.log('escapeHtml:');
assert(escapeHtml(null) === '', 'null → empty string');
assert(escapeHtml(undefined) === '', 'undefined → empty string');
assert(escapeHtml('hello') === 'hello', 'plain text unchanged');
assert(escapeHtml('<script>') === '&lt;script&gt;', 'angle brackets escaped');
assert(escapeHtml('a&b') === 'a&amp;b', 'ampersand escaped');
assert(escapeHtml('"hi"') === '&quot;hi&quot;', 'double quotes escaped');
assert(escapeHtml("'hi'") === '&#39;hi&#39;', 'single quotes escaped');
assert(escapeHtml(123) === '123', 'number converted to string');

console.log('\nescapeAttr:');
assert(escapeAttr('<img onerror=alert(1)>') === '&lt;img onerror=alert(1)&gt;', 'attribute injection escaped');
assert(escapeAttr('safe') === 'safe', 'safe attr unchanged');

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
