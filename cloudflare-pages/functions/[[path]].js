const UPSTREAM_ORIGIN = "https://safebars.onrender.com";

function upstreamUrl(requestUrl) {
  const incoming = new URL(requestUrl);
  return new URL(`${incoming.pathname}${incoming.search}`, UPSTREAM_ORIGIN);
}

function rewriteLocation(location, incomingUrl) {
  if (!location) return location;
  const upstream = new URL(UPSTREAM_ORIGIN);
  const resolved = new URL(location, upstream);
  if (resolved.origin !== upstream.origin) return location;

  const incoming = new URL(incomingUrl);
  return `${incoming.origin}${resolved.pathname}${resolved.search}${resolved.hash}`;
}

export async function onRequest(context) {
  const request = context.request;
  const target = upstreamUrl(request.url);
  const headers = new Headers(request.headers);
  const incoming = new URL(request.url);

  [
    "Host",
    "Connection",
    "Keep-Alive",
    "Proxy-Authenticate",
    "Proxy-Authorization",
    "TE",
    "Trailer",
    "Transfer-Encoding",
    "Upgrade",
    "Expect",
  ].forEach((header) => headers.delete(header));
  headers.set("X-Forwarded-Host", incoming.host);
  headers.set("X-Forwarded-Proto", incoming.protocol.replace(":", ""));
  headers.set("X-SafeBARS-Edge", "cloudflare-pages");

  const init = {
    method: request.method,
    headers,
    redirect: "manual",
  };
  if (!(["GET", "HEAD"].includes(request.method))) init.body = await request.arrayBuffer();

  try {
    const upstreamResponse = await fetch(new Request(target.toString(), init));
    const responseHeaders = new Headers(upstreamResponse.headers);
    ["Connection", "Keep-Alive", "Transfer-Encoding", "Upgrade"].forEach((header) => responseHeaders.delete(header));
    const location = responseHeaders.get("Location");
    if (location) responseHeaders.set("Location", rewriteLocation(location, request.url));

    responseHeaders.set("Cache-Control", "private, no-store");
    responseHeaders.set("X-SafeBARS-Served-By", "cloudflare-pages");

    return new Response(upstreamResponse.body, {
      status: upstreamResponse.status,
      statusText: upstreamResponse.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("SafeBARS upstream request failed", error);
    const wantsJson = incoming.pathname.startsWith("/api/");
    const message = "SafeBARS could not reach its analysis service. Please try again shortly.";
    return new Response(
      wantsJson
        ? JSON.stringify({ success: false, error: message })
        : `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SafeBARS temporarily unavailable</title><body style="font:16px/1.5 system-ui;max-width:680px;margin:12vh auto;padding:24px"><h1>SafeBARS is temporarily unavailable</h1><p>${message}</p></body></html>`,
      {
        status: 502,
        headers: {
          "Content-Type": wantsJson ? "application/json; charset=utf-8" : "text/html; charset=utf-8",
          "Cache-Control": "no-store",
        },
      },
    );
  }
}
