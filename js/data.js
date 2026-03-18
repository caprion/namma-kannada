// Loaded before other scripts. Fetches sentences.json and exposes as window.NAMMA_DATA
// Uses synchronous XHR as a simple loader for static deployment — no bundler needed.

(function () {
  var lang = 'en';
  try { lang = new URLSearchParams(location.search).get('lang') || 'en'; } catch (e) {}
  var file = lang === 'hi' ? 'data/sentences-hi.json' : 'data/sentences.json';
  window.NAMMA_LANG = lang;

  try {
    var req = new XMLHttpRequest();
    req.open('GET', file, false); // synchronous
    req.send(null);
    if (req.status === 200) {
      window.NAMMA_DATA = JSON.parse(req.responseText);
    } else {
      console.error('Failed to load ' + file + ' (status ' + req.status + ')');
      window.NAMMA_DATA = { program: {}, stages: [] };
    }
  } catch (e) {
    console.error('data.js error:', e);
    window.NAMMA_DATA = { program: {}, stages: [] };
  }
})();
