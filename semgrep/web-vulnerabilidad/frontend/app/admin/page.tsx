import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { AdminDashboardClient } from "@/components/AdminDashboardClient";
import { authOptions } from "@/lib/auth";

export default async function AdminPage() {
  const session = await getServerSession(authOptions);
  if (!session?.accessToken) {
    redirect("/login");
  }
  if (!session.user.isAdmin) {
    redirect("/dashboard");
  }

  return (
    <AdminDashboardClient
      accessToken={session.accessToken}
      username={session.user.username ?? session.user.name ?? "Administrador"}
    />
  );
}
