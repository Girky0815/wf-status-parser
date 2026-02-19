/**
 * Warframe Status Proxy Worker
 * 
 * GitHub Actions -> Cloudflare Worker -> Warframe API
 * 
 * Usage: https://your-worker.subdomain.workers.dev/?url=TARGET_URL
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get("url");

    if (!targetUrl) {
      return new Response("Missing 'url' parameter", { status: 400 });
    }

    // Add logging
    console.log(`Proxying request to: ${targetUrl}`);

    try {
      // Create request with headers to mimic a browser
      const proxyRequest = new Request(targetUrl, {
        method: request.method,
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
          "Accept": "application/json, text/plain, */*",
          "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
          // Add any other headers needed
        }
      });

      const response = await fetch(proxyRequest);

      // Re-create the response to modify headers (CORS) if necessary
      const newResponse = new Response(response.body, response);
      newResponse.headers.set("Access-Control-Allow-Origin", "*");
      newResponse.headers.set("X-Proxy-By", "Cloudflare-Worker");

      return newResponse;
    } catch (e) {
      return new Response(`Error fetching ${targetUrl}: ${e.message}`, { status: 500 });
    }
  },
};
