import type { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    user: {
      id?: string;
      username?: string;
      isAdmin?: boolean;
    } & DefaultSession["user"];
  }

  interface User {
    accessToken?: string;
    username?: string;
    isAdmin?: boolean;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    id?: string;
    username?: string;
    isAdmin?: boolean;
  }
}
