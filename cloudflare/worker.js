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

    console.log(`Proxying request to: ${targetUrl}`);

    try {
      const proxyRequest = new Request(targetUrl, {
        method: request.method,
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
          "Accept": "application/json, text/plain, */*",
          "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
          "Cache-Control": "no-cache",
          "Pragma": "no-cache",
          "Referer": "https://www.warframe.com/",
          "Origin": "https://www.warframe.com/"
        }
      });

      const response = await fetch(proxyRequest);

      // Create a clean response without forwarding potentially problematic headers
      const responseHeaders = new Headers();
      // Only forward necessary headers or set new ones
      responseHeaders.set("Content-Type", response.headers.get("Content-Type") || "application/json");
      responseHeaders.set("Access-Control-Allow-Origin", "*");
      responseHeaders.set("X-Proxy-By", "Cloudflare-Worker-Fixed");
      responseHeaders.set("X-Target-Status", response.status);

      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders
      });
    } catch (e) {
      return new Response(`Error fetching ${targetUrl}: ${e.message}`, { status: 500 });
    }
  },
};
