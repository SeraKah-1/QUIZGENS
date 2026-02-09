import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner"; // <--- Import ini

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "QuizGen AI",
  description: "Generate Quiz from PDF instantly",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <Toaster /> {/* <--- Pasang di sini, di bawah children */}
      </body>
    </html>
  );
}