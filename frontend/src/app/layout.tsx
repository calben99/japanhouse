import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Japan House - Japanese Property Listings',
  description: 'Browse Japanese property listings from various sources',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col">
          <header className="bg-jp-navy text-white shadow-md">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold">🏠 Japan House</h1>
              </div>
              <nav>
                <ul className="flex space-x-6">
                  <li><a href="/" className="hover:text-jp-red transition-colors">Home</a></li>
                  <li><a href="/properties" className="hover:text-jp-red transition-colors">Properties</a></li>
                  <li><a href="/about" className="hover:text-jp-red transition-colors">About</a></li>
                </ul>
              </nav>
            </div>
          </header>
          
          <main className="flex-grow">
            {children}
          </main>
          
          <footer className="bg-jp-navy text-white py-6">
            <div className="container mx-auto px-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Japan House</h3>
                  <p className="text-sm">Connecting you with the best properties across Japan.</p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
                  <ul className="space-y-2 text-sm">
                    <li><a href="/" className="hover:text-jp-red transition-colors">Home</a></li>
                    <li><a href="/properties" className="hover:text-jp-red transition-colors">Properties</a></li>
                    <li><a href="/about" className="hover:text-jp-red transition-colors">About</a></li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-4">Data Sources</h3>
                  <ul className="space-y-2 text-sm">
                    <li><a href="https://www.homes.co.jp" target="_blank" rel="noopener noreferrer" className="hover:text-jp-red transition-colors">HOMES</a></li>
                    <li><a href="https://suumo.jp" target="_blank" rel="noopener noreferrer" className="hover:text-jp-red transition-colors">SUUMO</a></li>
                    <li><a href="https://www.athome.co.jp" target="_blank" rel="noopener noreferrer" className="hover:text-jp-red transition-colors">AtHome</a></li>
                    <li><a href="https://www.akiya-mart.com" target="_blank" rel="noopener noreferrer" className="hover:text-jp-red transition-colors">Akiya-Mart</a></li>
                  </ul>
                </div>
              </div>
              <div className="mt-8 pt-6 border-t border-gray-700 text-center text-sm">
                <p>&copy; {new Date().getFullYear()} Japan House. All rights reserved.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
