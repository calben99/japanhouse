export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">About Japan House</h1>
      
      <div className="max-w-3xl mx-auto">
        <section className="mb-10">
          <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
          <p className="text-jp-gray mb-4">
            Japan House aims to simplify the property search process in Japan by aggregating
            listings from multiple Japanese real estate websites into one easy-to-use platform.
          </p>
          <p className="text-jp-gray mb-4">
            Finding property in Japan can be challenging, especially for non-Japanese speakers.
            Our goal is to make this process more accessible and transparent for everyone.
          </p>
        </section>
        
        <section className="mb-10">
          <h2 className="text-2xl font-semibold mb-4">Data Sources</h2>
          <p className="text-jp-gray mb-4">
            We collect property data from the following Japanese real estate websites:
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="bg-jp-light p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">HOMES</h3>
              <p className="text-jp-gray mb-3">
                One of Japan's largest real estate portals with extensive listings across the country.
              </p>
              <a 
                href="https://www.homes.co.jp" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-jp-red hover:underline"
              >
                Visit HOMES →
              </a>
            </div>
            
            <div className="bg-jp-light p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">SUUMO</h3>
              <p className="text-jp-gray mb-3">
                A major real estate information service covering rentals and sales throughout Japan.
              </p>
              <a 
                href="https://suumo.jp" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-jp-red hover:underline"
              >
                Visit SUUMO →
              </a>
            </div>
            
            <div className="bg-jp-light p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">AtHome</h3>
              <p className="text-jp-gray mb-3">
                A comprehensive real estate portal featuring properties from all regions of Japan.
              </p>
              <a 
                href="https://www.athome.co.jp" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-jp-red hover:underline"
              >
                Visit AtHome →
              </a>
            </div>
            
            <div className="bg-jp-light p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Akiya-Mart</h3>
              <p className="text-jp-gray mb-3">
                Specialized in "akiya" (vacant homes) and rural properties available at affordable prices.
              </p>
              <a 
                href="https://www.akiya-mart.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-jp-red hover:underline"
              >
                Visit Akiya-Mart →
              </a>
            </div>
          </div>
        </section>
        
        <section className="mb-10">
          <h2 className="text-2xl font-semibold mb-4">Data Collection Process</h2>
          <p className="text-jp-gray mb-4">
            Our system automatically collects property listings from these websites on a regular schedule
            using GitHub Actions workflows. The data is then processed and stored in our Supabase database.
          </p>
          <p className="text-jp-gray mb-4">
            We make every effort to ensure the accuracy of the information displayed, but we recommend
            verifying details with the original listing before making any decisions.
          </p>
        </section>
        
        <section>
          <h2 className="text-2xl font-semibold mb-4">Disclaimer</h2>
          <p className="text-jp-gray mb-4">
            Japan House is not affiliated with any of the real estate websites we collect data from.
            We are simply aggregating publicly available information to make it more accessible.
          </p>
          <p className="text-jp-gray">
            All property listings remain the intellectual property of their respective owners.
            We provide links to the original listings for complete information and contact details.
          </p>
        </section>
      </div>
    </div>
  )
}
