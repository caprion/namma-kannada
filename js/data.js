// Loaded before other scripts. Fetches sentences.json and exposes as window.NAMMA_DATA
// Uses synchronous XHR as a simple loader for static deployment — no bundler needed.

(function () {
  const req = new XMLHttpRequest();
  req.open('GET', 'data/sentences.json', false); // synchronous
  req.send(null);
  if (req.status === 200) {
    window.NAMMA_DATA = JSON.parse(req.responseText);
  } else {
    console.error('Failed to load sentences.json');
    window.NAMMA_DATA = { program: {}, stages: [] };
  }
})();
