// Local HTTP -> mounted Unix socket. Run inside a network=none container.
// No provider credentials or external network path belong in this process.
import http from 'node:http';
const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const socketPath = value('--socket');
const port = Number(args.includes('--port') ? value('--port') : 4000);
if (!socketPath || !Number.isInteger(port) || port < 0 || port > 65535) {
  throw new Error('Expected --socket PATH and optional --port PORT');
}
const server = http.createServer((request, response) => {
  if (request.method !== 'POST' || request.url !== '/v1/chat/completions') {
    response.writeHead(404).end();
    return;
  }
  const length = Number(request.headers['content-length']);
  if (!Number.isInteger(length) || length <= 0 || length > 16 * 1024 * 1024) {
    response.writeHead(413).end();
    return;
  }
  const upstream = http.request({
    socketPath, method: 'POST', path: request.url,
    headers: { 'content-type': 'application/json', 'content-length': length },
  }, (result) => {
    response.writeHead(result.statusCode, {
      'content-type': result.headers['content-type'] ?? 'application/json',
    });
    result.pipe(response);
  });
  upstream.on('error', () => {
    if (!response.headersSent) response.writeHead(502);
    response.end(JSON.stringify({ error: 'Inference transport unavailable' }));
  });
  request.on('aborted', () => upstream.destroy());
  request.pipe(upstream);
});
server.listen(port, '127.0.0.1', () => console.log('Container inference bridge ready'));
