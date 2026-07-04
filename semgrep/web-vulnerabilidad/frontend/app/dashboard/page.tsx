import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { DashboardClient } from "@/components/DashboardClient";
import { authOptions } from "@/lib/auth";

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);
  if (!session?.accessToken) {
    redirect("/login");
  }

  return (
    <DashboardClient
      accessToken={session.accessToken}
      username={session.user.username ?? session.user.name ?? "Usuario"}
      isAdmin={Boolean(session.user.isAdmin)}
    />
  );
}
