import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const HERE = path.dirname(new URL(import.meta.url).pathname);
const CLIENT = path.join(HERE, '..', '..', 'client');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (url === '/world' || url === '/config') {
    res.writeHead(200, { 'content-type': 'application/json' });
    return res.end(fs.readFileSync(path.join(HERE, url.slice(1) + '.json')));
  }
  if (url === '/probe.js') {
    res.writeHead(200, { 'content-type': 'text/javascript' });
    return res.end(fs.readFileSync(path.join(HERE, 'probe.js')));
  }
  const file = url === '/' ? '/index.html' : url;
  const full = path.join(CLIENT, file);
  if (!fs.existsSync(full)) { res.writeHead(404); return res.end('no'); }
  let body = fs.readFileSync(full);
  if (file === '/index.html') {
    // Inject the probe BEFORE app.js so the socket stub is in place at boot.
    body = Buffer.from(String(body).replace('<script src="app.js"></script>', '<script src="/probe.js"></script>\n  <script src="app.js"></script>'));
  }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  res.end(body);
}).listen(8911, '0.0.0.0', () => console.log('serving on http://0.0.0.0:8911 (LAN: http://192.168.0.22:8911/)'));
