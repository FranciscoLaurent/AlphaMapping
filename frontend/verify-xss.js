/**
 * XSS 修复验证脚本（Node 环境运行）
 *
 * 扫描 frontend/app.js 中所有 innerHTML 拼接点，
 * 检查是否已用 escapeHtml / escapeAttr 包裹。
 *
 * 运行方式：node frontend/verify-xss.js
 */
const fs = require('fs');
const path = require('path');

const appJs = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');

// 匹配 innerHTML 赋值中的模板字符串拼接
// 找 ${...} 内容不在 escapeHtml/escapeAttr 调用中的
const lines = appJs.split('\n');
const issues = [];

let inTemplate = false;
let templateStart = 0;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const lineNum = i + 1;

  // 检查 innerHTML 赋值开始
  if (line.includes('.innerHTML') && line.includes('`')) {
    inTemplate = true;
    templateStart = lineNum;
  }

  if (inTemplate) {
    // 找 ${...} 中的变量引用（非 escapeHtml/escapeAttr 包裹）
    const interpolationPattern = /\$\{([^}]+)\}/g;
    let match;
    while ((match = interpolationPattern.exec(line)) !== null) {
      const expr = match[1].trim();
      // 跳过纯函数调用（escapeHtml/escapeAttr）
      if (expr.startsWith('escapeHtml(') || expr.startsWith('escapeAttr(')) continue;
      // 跳过纯表达式（数字、布尔、方法调用如 .toFixed()）
      if (/^\d+$/.test(expr)) continue;
      if (/^['"]/.test(expr)) continue;
      if (expr.includes('.toFixed(')) continue;
      // 跳过 getRiskColor 等返回安全值的函数
      if (expr.startsWith('getRiskColor(')) continue;
      // 跳过 formatMarkdown（内部已做 escapeHtml）
      if (expr.startsWith('formatMarkdown(')) continue;
      // 其余可能是未转义的数据拼接
      issues.push({ line: lineNum, expr });
    }

    if (line.includes('`') && lineNum > templateStart) {
      // 模板字符串结束（简单启发式：行内有反引号闭合）
      // 更精确的解析需要状态机，这里简化处理
    }
  }
}

if (issues.length === 0) {
  console.log('✓ 未发现明显的未转义 innerHTML 拼接点');
  process.exit(0);
} else {
  console.log(`✗ 发现 ${issues.length} 个可能未转义的拼接点：`);
  issues.forEach(({ line, expr }) => {
    console.log(`  行 ${line}: ${expr}`);
  });
  process.exit(1);
}
