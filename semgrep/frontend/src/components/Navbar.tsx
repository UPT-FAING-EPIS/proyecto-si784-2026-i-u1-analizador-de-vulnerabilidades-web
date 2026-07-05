"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield, LayoutDashboard, Search, Users, FileText,
  LogOut, ChevronDown, Bell, Settings, User, Sparkles
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["admin", "analyst", "user"] },
  { href: "/scanner", label: "Scanner", icon: Search, roles: ["admin", "analyst", "user"] },
  { href: "/solutions", label: "Soluciones", icon: Sparkles, roles: ["admin", "analyst", "user"] },
  { href: "/profile", label: "Perfil", icon: User, roles: ["admin", "analyst", "user"] },
  { href: "/admin", label: "Admin", icon: Users, roles: ["admin"] },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => { logout(); router.push("/login"); };

  const ROLE_COLORS: Record<string, string> = {
    admin: "bg-red-500/20 text-red-400 border-red-500/30",
    analyst: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    user: "bg-gray-500/20 text-gray-400 border-gray-500/30",
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0f1623]/95 backdrop-blur border-b border-gray-800/50">
      <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center justify-between">

        {/* Logo */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-white text-lg tracking-tight">
              Vuln<span className="text-blue-400">Scan</span>
              <span className="text-xs font-normal text-gray-500 ml-1">PRO</span>
            </span>
          </Link>

          {/* Nav links */}
          {user && (
            <div className="hidden md:flex items-center gap-1">
              {NAV_ITEMS.filter(i => i.roles.includes(user.role)).map(item => {
                const Icon = item.icon;
                const active = pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors ${
                      active
                        ? "bg-blue-600/20 text-blue-400 font-medium"
                        : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <button className="relative p-2 text-gray-400 hover:text-white rounded-md hover:bg-white/5">
                <Bell className="w-4 h-4" />
              </button>

              <div className="flex items-center gap-2 pl-3 border-l border-gray-800">
                <div className="text-right hidden sm:block">
                  <div className="text-sm text-white font-medium">{user.username}</div>
                  <div className={`text-xs px-1.5 py-0.5 rounded border inline-block ${ROLE_COLORS[user.role] || ROLE_COLORS.user}`}>
                    {user.role}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-red-400 px-2 py-1.5 rounded-md hover:bg-red-500/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login"
                className="text-sm text-gray-300 hover:text-white px-3 py-1.5 rounded-md hover:bg-white/5 transition-colors">
                Iniciar sesión
              </Link>
              <Link href="/register"
                className="text-sm text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-md transition-colors">
                Registrarse
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
