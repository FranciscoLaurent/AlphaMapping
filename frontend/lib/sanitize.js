/**
 * HTML 转义工具。
 *
 * 前端大量通过 innerHTML 拼接来自 FOFA / ZoomEye 的外部资产数据，
 * 以及 LLM 生成的分析报告。这些内容不可信，直接拼接会导致 XSS。
 * 本模块提供统一的转义函数，供所有 innerHTML 拼接点使用。
 *
 * UMD：浏览器挂全局 window.AlphaSanitize，Node 下 module.exports 供测试。
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AlphaSanitize = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {

  /**
   * 转义 HTML 文本内容（用于元素文本节点位置）。
   * 顺序很重要：& 必须最先转义，避免后续转义产生的 & 被二次处理。
   *
   * @param {*} value 任意值，null/undefined 返回空串
   * @returns {string} 转义后的安全字符串
   */
  function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * 转义用于 HTML 属性值的字符串（双引号包裹场景）。
   * 与 escapeHtml 一致——属性值同样需要转义 < > & " 防止逃逸。
   *
   * @param {*} value 任意值，null/undefined 返回空串
   * @returns {string} 可安全放入双引号属性的字符串
   */
  function escapeAttr(value) {
    return escapeHtml(value);
  }

  return { escapeHtml, escapeAttr };
}));
