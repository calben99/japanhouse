import Link from 'next/link'

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-jp-navy to-blue-900 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Find Your Dream Home in Japan
            </h1>
            <p className="text-xl mb-8">
              Browse thousands of property listings from across Japan, all in one place.
            </p>
            <Link href="/properties" className="btn-primary inline-block text-lg">
              Browse Properties
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Properties Section */}
      <section className="py-16 bg-jp-light">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-8 text-center">Featured Properties</h2>
          <p className="text-center text-jp-gray mb-12 max-w-2xl mx-auto">
            Our database is being populated with the latest property listings from across Japan.
            Check back soon to see featured properties.
          </p>
          
          <div className="text-center">
            <Link href="/properties" className="btn-secondary inline-block">
              View All Properties
            </Link>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">About Japan House</h2>
              <p className="text-jp-gray mb-6">
                Japan House aggregates property listings from multiple Japanese real estate websites,
                making it easier for you to find your perfect home or investment property in Japan.
              </p>
              <p className="text-jp-gray mb-6">
                We collect data from HOMES, SUUMO, AtHome, and Akiya-Mart to provide you with 
                comprehensive property information in one convenient place.
              </p>
              <Link href="/about" className="text-jp-red font-semibold hover:underline">
                Learn more about our data sources →
              </Link>
            </div>
            <div className="bg-jp-light p-8 rounded-lg">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded shadow text-center">
                  <div className="text-4xl font-bold text-jp-red mb-2">HOMES</div>
                  <p className="text-sm text-jp-gray">Property listings from HOMES.co.jp</p>
                </div>
                <div className="bg-white p-4 rounded shadow text-center">
                  <div className="text-4xl font-bold text-jp-red mb-2">SUUMO</div>
                  <p className="text-sm text-jp-gray">Property listings from SUUMO.jp</p>
                </div>
                <div className="bg-white p-4 rounded shadow text-center">
                  <div className="text-4xl font-bold text-jp-red mb-2">AtHome</div>
                  <p className="text-sm text-jp-gray">Property listings from AtHome.co.jp</p>
                </div>
                <div className="bg-white p-4 rounded shadow text-center">
                  <div className="text-4xl font-bold text-jp-red mb-2">Akiya</div>
                  <p className="text-sm text-jp-gray">Listings from Akiya-Mart.com</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
