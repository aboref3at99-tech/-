import http from 'node:http';

const port = Number(process.env.API_PORT || 4000);

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    const body = JSON.stringify({
      service: 'restaurant-api',
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: '0.2.1'
    });
    res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' });
    res.end(body);
    return;
  }

  res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
  res.end('Restaurant ERP API is running');
});

server.listen(port, () => {
  console.log(`API running on http://localhost:${port}`);
  console.log(`Health endpoint: http://localhost:${port}/health`);
});
