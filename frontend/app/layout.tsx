import type { Metadata } from "next";
import { Inter, Dancing_Script } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const dancing = Dancing_Script({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-dancing",
});

export const metadata: Metadata = {
  title: "The Aura Standard — The World's First Reality Engine for Blender",
  description:
    "Deploy any 3D model as a live AR experience in one click. Built for Blender. Powered by The Aura Standard.",
  openGraph: {
    title: "The Aura Standard",
    description: "One-click AR deployment for Blender professionals.",
    url: "https://ceo-of-aura.cloud",
    siteName: "The Aura Standard",
    images: [{ url: "/og-image.jpg", width: 1200, height: 630 }],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body
        className={`${inter.variable} ${dancing.variable} font-sans bg-black text-white antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
