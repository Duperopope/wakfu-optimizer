import type { Metadata } from "next";
import { IBM_Plex_Sans } from "next/font/google";
import { ThemeProvider } from "next-themes";
import "./globals.css";

const ibmPlexSans = IBM_Plex_Sans({
  variable: "--font-ibm-plex-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Wakfu Optimizer | Build Planner",
  description:
    "Optimiseur de builds pour WAKFU — equipement, sorts, aptitudes, enchantements.",
  openGraph: {
    title: "Wakfu Optimizer | Build Planner",
    description:
      "Optimiseur de builds pour WAKFU — equipement, sorts, aptitudes, enchantements.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" suppressHydrationWarning className="min-h-screen flex flex-col">
      <body
        className={`${ibmPlexSans.variable} font-sans bg-bg-darker text-primary antialiased flex-1 flex flex-col overflow-hidden`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
