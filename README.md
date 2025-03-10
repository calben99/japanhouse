# JapanHouse - Japanese Property Listing Aggregator

JapanHouse is a web application that scrapes multiple Japanese property listing websites and aggregates them into a single platform. This allows users to search across multiple sources at once, with unified filtering and display.

## Project Structure

```
japanhouse/
├── backend/             # FastAPI backend
│   ├── app/            # Main application code
│   │   ├── api/        # API endpoints
│   │   ├── core/       # Core functionality
│   │   ├── db/         # Supabase database integration
│   │   ├── models/     # Data models
│   │   ├── schemas/    # Pydantic schemas
│   │   └── services/   # Business logic services
│   ├── config/         # Configuration files
│   └── tests/          # Backend tests
│
├── scrapers/           # Web scrapers for property listings
│   ├── common/         # Shared scraper utilities
│   └── sites/          # Individual site scrapers
│
├── frontend/           # React frontend
│   ├── public/         # Static files
│   └── src/            # Source code
│       ├── assets/     # Images, fonts, etc.
│       ├── components/ # Reusable React components
│       ├── pages/      # Page components
│       ├── services/   # API service connections
│       ├── styles/     # CSS/styling
│       └── utils/      # Utility functions
│
└── docs/               # Documentation
    ├── api/            # API documentation
    ├── design/         # Design documents
    └── development/    # Development guides
```

## Technologies

### Backend
- **FastAPI**: Modern, high-performance web framework
- **Supabase**: PostgreSQL database with built-in authentication and APIs
- **Python 3.9+**: For backend and scraper code

### Scraping
- **Beautiful Soup / Selenium / Scrapy**: Web scraping tools
- **APScheduler**: For scheduling periodic scraping jobs

### Frontend
- **React**: Frontend UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Supabase JS Client**: For connecting to Supabase

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Supabase account

### Setup Instructions

Detailed setup instructions will be provided once the initial development is complete.

## Features

- Aggregate property listings from multiple Japanese websites
- Search and filter properties based on various criteria
- Display property details with images, location, and specifications
- User accounts for saving favorite properties
- Multi-language support (Japanese and English)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
