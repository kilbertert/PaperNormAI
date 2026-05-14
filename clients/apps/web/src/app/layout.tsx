import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "PaperNormAI",
  description: "AI-powered paper format calibration tool",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}