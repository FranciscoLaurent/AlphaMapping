/**
 * risk.js 单元测试（Node 环境运行）
 *
 * 运行方式：node frontend/test/risk.test.js
 */
const { HIGH_RISK_PORTS, isHighRiskPort, countHighRiskAssets } = require('../lib/risk.js');

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

console.log('isHighRiskPort:');
assert(isHighRiskPort(22) === true, 'SSH (22) is high risk');
assert(isHighRiskPort(3389) === true, 'RDP (3389) is high risk');
assert(isHighRiskPort(6379) === true, 'Redis (6379) is high risk');
assert(isHighRiskPort(80) === false, 'HTTP (80) is not high risk');
assert(isHighRiskPort(443) === false, 'HTTPS (443) is not high risk');
assert(isHighRiskPort(null) === false, 'null → false');
assert(isHighRiskPort('') === false, 'empty string → false');
assert(isHighRiskPort('22') === true, 'string "22" → true (coerced)');
assert(isHighRiskPort('abc') === false, 'non-numeric string → false');

console.log('\ncountHighRiskAssets:');
assert(countHighRiskAssets(null) === 0, 'null → 0');
assert(countHighRiskAssets([]) === 0, 'empty array → 0');
assert(countHighRiskAssets([{ port: 80 }, { port: 443 }]) === 0, 'no risky ports → 0');
assert(countHighRiskAssets([{ port: 22 }, { port: 80 }, { port: 3389 }]) === 2, '2 risky → 2');
assert(countHighRiskAssets([{ port: '6379' }]) === 1, 'string port "6379" → 1');

console.log('\nHIGH_RISK_PORTS:');
assert(HIGH_RISK_PORTS.has(27017), 'MongoDB (27017) in set');
assert(!HIGH_RISK_PORTS.has(8080), '8080 not in set');

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
