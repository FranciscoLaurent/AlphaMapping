/**
 * 资产风险判定工具。
 *
 * 此前前端「高危资产」数量用 Math.random() 编造，每次刷新都变，
 * 对安全态势感知平台是误导性假数据。后端 /stats 未提供高危统计，
 * 因此前端基于「暴露的敏感端口」做启发式判定——真实、可解释、稳定。
 *
 * 口径：开放数据库 / 远程访问 / 文件共享等敏感端口的资产计为高危。
 * 与后端 AI 单资产分析（analyze-asset）的 risk_level 口径可能不同，
 * 仅为大屏快览提供可量化的风险信号。
 *
 * UMD：浏览器挂全局 window.AlphaRisk，Node 下 module.exports 供测试。
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AlphaRisk = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {

  // 敏感端口集合：数据库 / 远程访问 / 文件共享 / 管理服务
  const HIGH_RISK_PORTS = new Set([
    22,    // SSH
    23,    // Telnet
    135,   // Windows RPC
    139,   // NetBIOS
    445,   // SMB
    1433,  // MSSQL
    1521,  // Oracle
    3306,  // MySQL
    3389,  // RDP
    5432,  // PostgreSQL
    5900,  // VNC
    5901,  // VNC
    6379,  // Redis
    9200,  // Elasticsearch
    27017  // MongoDB
  ]);

  /**
   * 判断端口是否属于高危敏感端口。
   *
   * @param {*} port 端口号，可为数字或字符串
   * @returns {boolean}
   */
  function isHighRiskPort(port) {
    if (port === null || port === undefined || port === '') return false;
    const num = Number(port);
    if (!Number.isFinite(num)) return false;
    return HIGH_RISK_PORTS.has(num);
  }

  /**
   * 统计资产列表中暴露敏感端口的高危资产数量。
   * 结果稳定（非随机），相同输入恒等输出。
   *
   * @param {Array<{port:*}>} assets 资产列表
   * @returns {number} 高危资产数量
   */
  function countHighRiskAssets(assets) {
    if (!Array.isArray(assets)) return 0;
    return assets.reduce((count, a) => count + (isHighRiskPort(a && a.port) ? 1 : 0), 0);
  }

  return { HIGH_RISK_PORTS, isHighRiskPort, countHighRiskAssets };
}));
