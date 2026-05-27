/* KaTeX 로더 — 모든 HTML 보고서가 공유.
 * jsDelivr에서 KaTeX 0.16.9를 동적으로 로드한 후, 페이지의 $...$ 및 $$...$$ 수식을 렌더한다.
 * SRI 해시를 사용하지 않으므로 버전 업그레이드나 해시 오타로 인한 렌더 실패 위험이 없다.
 */
(function () {
  var VERSION = '0.16.9';
  var CDN = 'https://cdn.jsdelivr.net/npm/katex@' + VERSION + '/dist';

  function loadCSS(href) {
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = href;
    document.head.appendChild(l);
  }

  function loadJS(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error('Failed to load ' + src)); };
      document.head.appendChild(s);
    });
  }

  function renderAll() {
    if (!window.renderMathInElement) return;
    window.renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$',  right: '$',  display: false }
      ],
      throwOnError: false,
      strict: false
    });
  }

  loadCSS(CDN + '/katex.min.css');

  loadJS(CDN + '/katex.min.js')
    .then(function () { return loadJS(CDN + '/contrib/auto-render.min.js'); })
    .then(function () {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', renderAll);
      } else {
        renderAll();
      }
    })
    .catch(function (err) {
      console.error('[katex-loader] ' + err.message);
    });
})();
