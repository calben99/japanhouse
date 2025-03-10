# Japan House Frontend

A Next.js web application to display Japanese property listings scraped from various real estate websites.

## Features

- Browse property listings from HOMES, SUUMO, AtHome, and Akiya-Mart
- Filter properties by location, property type, price range, and size
- View detailed property information and access original listings
- Responsive design for desktop and mobile viewing

## Getting Started

### Prerequisites

- Node.js 16.8 or later
- npm or yarn
- Supabase account with property listings data

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/japanhouse.git
cd japanhouse/frontend
```

2. Install dependencies
```bash
npm install
# or
yarn install
```

3. Create a `.env.local` file based on `.env.example` and add your Supabase credentials

4. Start the development server
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

### Option 1: Deploy from Vercel Dashboard

1. Import your GitHub repository in the [Vercel Dashboard](https://vercel.com/import)
2. Select the `frontend` directory as the root directory
3. Configure environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anonymous key
4. Deploy

### Option 2: Deploy with Vercel CLI

1. Install Vercel CLI
```bash
npm i -g vercel
```

2. Log in to Vercel
```bash
vercel login
```

3. Navigate to the frontend directory and deploy
```bash
cd frontend
vercel
```

4. Follow the prompts to configure your project

## Environment Variables

The following environment variables are required for the application to work properly:

- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anonymous key

## Technology Stack

- Next.js - React framework
- Tailwind CSS - Utility-first CSS framework
- Supabase - Backend as a Service (BaaS) for database
- TypeScript - Type safety

## License

This project is private and not licensed for public use.
