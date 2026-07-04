import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { ApiKeysClient } from "@/components/ApiKeysClient";
import { authOptions } from "@/lib/auth";

export default async function ApiKeysPage() {
  const session = await getServerSession(authOptions);
  if (!session?.accessToken) {
    redirect("/login");
  }

  return (
    <ApiKeysClient
      accessToken={session.accessToken}
      username={session.user.username ?? session.user.name ?? "Usuario"}
    />
  );
}
