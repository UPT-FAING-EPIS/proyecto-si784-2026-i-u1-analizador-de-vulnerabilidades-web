import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

import { BACKEND_API_URL } from "./env";

type BackendUser = {
  id: number;
  email: string;
  username: string;
  is_admin: boolean;
};

type LoginResponse = {
  access_token: string;
  token_type: string;
  user: BackendUser;
};

export const authOptions: NextAuthOptions = {
  session: {
    strategy: "jwt"
  },
  pages: {
    signIn: "/login"
  },
  providers: [
    CredentialsProvider({
      name: "Email y contrasena",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Contrasena", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        const body = new URLSearchParams();
        body.set("username", credentials.email);
        body.set("password", credentials.password);

        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 12000);

        let response: Response;
        try {
          response = await fetch(`${BACKEND_API_URL}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body,
            signal: controller.signal
          });
        } catch {
          return null;
        } finally {
          clearTimeout(timeout);
        }

        if (!response.ok) {
          return null;
        }

        const data = (await response.json()) as LoginResponse;
        return {
          id: String(data.user.id),
          email: data.user.email,
          name: data.user.username,
          username: data.user.username,
          isAdmin: data.user.is_admin,
          accessToken: data.access_token
        };
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.username = user.username;
        token.isAdmin = user.isAdmin;
        token.accessToken = user.accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      session.user.id = token.id;
      session.user.username = token.username;
      session.user.isAdmin = token.isAdmin;
      return session;
    }
  }
};
