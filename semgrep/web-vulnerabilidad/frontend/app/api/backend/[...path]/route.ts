import { NextRequest, NextResponse } from "next/server";

import { BACKEND_API_URL } from "@/lib/env";

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade"
]);

function buildTargetUrl(path: string[], search: string) {
  const base = BACKEND_API_URL.endsWith("/") ? BACKEND_API_URL : `${BACKEND_API_URL}/`;
  const url = new URL(path.join("/"), base);
  url.search = search;
  return url;
}

function buildForwardHeaders(request: NextRequest) {
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  for (const header of HOP_BY_HOP_HEADERS) {
    headers.delete(header);
  }
  return headers;
}

function buildResponseHeaders(headers: Headers) {
  const responseHeaders = new Headers(headers);
  for (const header of HOP_BY_HOP_HEADERS) {
    responseHeaders.delete(header);
  }
  return responseHeaders;
}

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const targetUrl = buildTargetUrl(path, request.nextUrl.search);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  const init: RequestInit & { duplex?: "half" } = {
    method: request.method,
    headers: buildForwardHeaders(request),
    signal: controller.signal,
    redirect: "manual"
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }

  try {
    const response = await fetch(targetUrl, init);
    return new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: buildResponseHeaders(response.headers)
    });
  } catch {
    return NextResponse.json(
      { detail: "No se pudo conectar con el backend FastAPI. Verifica que http://127.0.0.1:8000 este activo." },
      { status: 502 }
    );
  } finally {
    clearTimeout(timeout);
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
