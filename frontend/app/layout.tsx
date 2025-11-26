import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Cosmic Stream | LIGO Quasi-Live Data',
  description: 'Historical LIGO gravitational-wave data replayed as a quasi-live cosmic stream.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
