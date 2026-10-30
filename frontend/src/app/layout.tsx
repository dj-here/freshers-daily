import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FreshersDaily — Exactly 5 Verified Fresher Jobs in India Daily",
  description: "Zero hallucination, evidence-backed software opportunities for 2026, 2027, and 2028 engineering batches in India.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col justify-between antialiased">
        {children}
      </body>
    </html>
  );
}
