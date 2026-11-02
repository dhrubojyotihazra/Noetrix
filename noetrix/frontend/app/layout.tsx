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
  metadataBase: new URL("https://noetrix-virid.vercel.app"),
  title: {
    default: "Noetrix · Explainable ATS Resume Screener & AI Tailoring",
    template: "%s | Noetrix",
  },
  description:
    "An explainable, deterministic ATS resume simulation engine with client-side PII scrubbing and zero server-side storage. Features transparent 6-metric scoring, anti-gaming 50% Soft Knockout, and zero-fabrication AI bullet tailoring.",
  keywords: [
    "ATS Resume Checker",
    "Explainable ATS",
    "Resume Screener",
    "Applicant Tracking System",
    "Free ATS Score",
    "Deterministic AI ATS",
    "Resume Tailoring",
    "AI Resume Optimizer",
    "Anti-Gaming ATS",
    "Sentence-Transformers Resume Matching",
    "Noetrix",
  ],
  authors: [{ name: "Dhrubojyoti Hazra", url: "https://github.com/dhrubojyotihazra" }],
  creator: "Dhrubojyoti Hazra",
  publisher: "Brainware University & Ardent Computech",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://noetrix-virid.vercel.app",
    siteName: "Noetrix ATS",
    title: "Noetrix · Explainable ATS Scorer & Resume Tailoring",
    description:
      "Deterministic 6-metric ATS simulation with zero server-side storage. Overcome black-box ATS filters with mathematical explainability and guardrailed GenAI.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Noetrix Explainable ATS Interface Preview",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Noetrix · Explainable ATS Scorer & Resume Tailoring",
    description:
      "Deterministic 6-metric ATS simulation with zero server-side storage. Free candidate audit and recruiter ranking.",
    images: ["/og-image.png"],
    creator: "@dhrubojyoti",
  },
  icons: {
    icon: [
      { url: "/favicon.png", sizes: "any" },
      { url: "/icon-512.png", sizes: "512x512", type: "image/png" },
      { url: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon.ico" },
    ],
    shortcut: "/favicon.png",
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180" }],
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Noetrix",
  "url": "https://noetrix-virid.vercel.app/",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "All",
  "description":
    "An explainable, dual-portal ATS resume screening and tailoring system with deterministic 6-metric evaluation and zero credential fabrication.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
  },
  "author": {
    "@type": "Organization",
    "name": "Brainware University & Ardent Computech Pvt. Ltd.",
  },
  "featureList": [
    "Deterministic 6-Metric Resume Scoring",
    "50% Soft Knockout Anti-Gaming Ceiling",
    "Zero-Fabrication Guardrailed AI Tailoring",
    "Client-Side PII Scrubbing and Stateless Processing",
    "Recruiter Batch Screening with 6-Tier Tie-Breaking",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${anton.variable} ${dmSans.variable}`}>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="bg-canvas text-ink font-sans antialiased min-h-screen flex flex-col selection:bg-accent-yellow selection:text-ink">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
