import { NextRequest, NextResponse } from "next/server";

// Rutas que NO requieren autenticación
const PUBLIC_PATHS = ["/login", "/register"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Permitir rutas públicas y assets de Next.js sin verificar token
  if (
    PUBLIC_PATHS.some((p) => pathname.startsWith(p)) ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon")
  ) {
    return NextResponse.next();
  }

  // El token vive en localStorage (cliente) — el middleware solo puede leer cookies.
  // Para proyectos con auth completo usaríamos cookies httpOnly.
  // Aquí dejamos pasar todo y el cliente maneja la redirección.
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
