import type { Metadata } from "next";
import { Anton, DM_Sans } from "next/font/google";
import Navbar from "@/components/ui/Navbar";
import Footer from "@/components/ui/Footer";
import "./globals.css";

const anton = Anton({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-anton",
  display: "swap",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Noetrix · Hybrid ATS Scorer & Ranker",
  description:
    "A transparent, deterministic ATS resume simulation engine with zero stored data. Candidate scoring, AI tailoring, and recruiter explainable shortlists.",
  icons: {
    icon: [
      { url: "/favicon.png", sizes: "any" },
      { url: "/icon-512.png", sizes: "512x512", type: "image/png" },
      { url: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon.ico" },
    ],
    shortcut: "/favicon.png",
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180" }
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${anton.variable} ${dmSans.variable}`}>
      <body className="bg-canvas text-ink font-sans antialiased min-h-screen flex flex-col selection:bg-accent-yellow selection:text-ink">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
