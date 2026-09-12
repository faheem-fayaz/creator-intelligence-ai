import "./globals.css";

import { Toaster } from "react-hot-toast";

export const metadata = {
  title: "Creator AI",
  description: "AI Creator Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  return (

    <html lang="en">

      <body>

        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#18181b",
              color: "#fff",
              border: "1px solid #27272a",
            },
          }}
        />

        {children}

      </body>

    </html>
  );
}