/**
 * Warframe ステータス プロキシ Worker
 * 
 * GitHub Actions -> Cloudflare Worker -> Warframe API
 * 
 * 使い方: https://your-worker.subdomain.workers.dev/?url=TARGET_URL
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get("url");

    if (!targetUrl) {
      return new Response("エラー: 'url' パラメータが不足しています", { status: 400 });
    }

    // デバッグログ: プロキシ先を表示
    console.log(`リクエストをプロキシ中: ${targetUrl}`);

    try {
      // ブラウザのリクエストを模倣するためのヘッダー群
      const proxyRequest = new Request(targetUrl, {
        method: request.method,
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
          "Accept": "application/json, text/plain, */*",
          "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
          "Cache-Control": "no-cache",
          "Pragma": "no-cache",
          "Referer": "https://www.warframe.com/",
          "Origin": "https://www.warframe.com/"
        }
      });

      const response = await fetch(proxyRequest);

      // 競合を避けるため、クリーンなレスポンスヘッダーを作成
      const responseHeaders = new Headers();
      // 必要なヘッダーのみを設定または転送
      responseHeaders.set("Content-Type", response.headers.get("Content-Type") || "application/json");
      responseHeaders.set("Access-Control-Allow-Origin", "*");
      responseHeaders.set("X-Proxy-By", "Cloudflare-Worker-Fixed-JP");
      responseHeaders.set("X-Target-Status", response.status.toString());

      // 元のレスポンスボディとステータスを保持して返す
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders
      });
    } catch (e) {
      return new Response(`取得エラー (${targetUrl}): ${e.message}`, { status: 500 });
    }
  },
};
