import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EcloWork — Mobilités et emploi en Île-de-France",
  description:
    "Un récit de l’équipe Rhizome pour explorer les évolutions des transports et de l’emploi en Île-de-France. Un regard descriptif, sans conclusion causale.",
  icons: { icon: [{ url: "/favicon.svg", type: "image/svg+xml" }] },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
