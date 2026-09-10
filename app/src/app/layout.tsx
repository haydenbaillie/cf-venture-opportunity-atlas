import type { Metadata } from "next";
import { IBM_Plex_Sans, Source_Serif_4 } from "next/font/google";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import "./globals.css";

const sans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ibm-plex",
});

const serif = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-source-serif",
});

export const metadata: Metadata = {
  title: "CF Venture Opportunity Atlas",
  description:
    "Public-data research on remaining unmet need, competitive white space, and possible company-formation opportunities in cystic fibrosis.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${sans.variable} ${serif.variable} font-sans`}>
        <Nav />
        <main className="mx-auto max-w-6xl px-5 py-10">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
