# AWS Blog Scraper & Search Site

Automated scraping and high-quality search for AWS blog posts, deployed on GitHub Pages.

## Features

- Automated Scraping: Daily scraping of 5+ AWS blog sources via GitHub Actions
- Fast Search: Client-side search with Pagefind (<500ms response time)
- Modern UI: Responsive design with dark mode support
- Smart Filtering: Filter by source, AWS service, date range, and category
- Zero Backend: Fully static site hosted on GitHub Pages

## Blog Sources

- AWS News Blog - Official product announcements
- AWS Architecture Blog - Best practices and reference architectures
- AWS DevOps Blog - CI/CD and automation
- AWS Security Blog - Security best practices
- AWS Compute Blog - EC2, Lambda, containers, and serverless

## Tech Stack

- **Jekyll 4.3.3** - Static site generator (GitHub Pages compatible)
- **Python 3.11** - Web scraper
- **Pagefind** - Client-side search
- **GitHub Actions** - Automated scraping and deployment

## Setup

### Prerequisites

- Ruby 3.1+ (for Jekyll)
- Python 3.11+ (for scraper)
- Bundler (`gem install bundler`)

### Local Development

1. **Install dependencies**:
   ```bash
   # Ruby dependencies
   bundle install

   # Python dependencies
   pip install -r scraper/requirements.txt
   ```

2. **Run scraper** (optional - site works with sample data):
   ```bash
   cd scraper
   python main.py
   ```

3. **Build and serve site**:
   ```bash
   bundle exec jekyll serve
   ```

4. **Visit**: http://localhost:4000/awsrudy-vibed-01/

### Build for Production

```bash
bundle exec jekyll build
```

Site will be in `_site/` directory.

## Project Structure

```
.
├── _config.yml              # Jekyll configuration
├── _layouts/                # Page layouts
├── _includes/               # Reusable components
├── _sass/                   # Stylesheets
├── _data/                   # Data files
│   ├── sources.yml          # Blog source configuration
│   └── posts.json           # Scraped blog posts
├── assets/                  # Static assets (CSS, JS, images)
├── scraper/                 # Python scraper
│   ├── main.py              # Entry point
│   ├── scrapers/            # Individual blog scrapers
│   └── utils/               # Helper functions
└── .github/workflows/       # GitHub Actions
```

## Scraper

The scraper:
- Fetches posts from RSS feeds (primary) and HTML parsing (fallback)
- Extracts metadata (title, date, author, categories, AWS services)
- Cleans content (removes scripts, fixes links)
- Deduplicates posts across sources
- Stores data in `_data/posts.json`

Run manually:
```bash
cd scraper
python main.py
```

Runs automatically via GitHub Actions (daily at 00:00 UTC).

## Search

Powered by **Pagefind**:
- Indexes all content at build time
- Fast client-side search (<500ms)
- Supports filtering and sorting
- No backend required

## Deployment

Automatically deployed to GitHub Pages via GitHub Actions:
- **Trigger**: Push to main, or daily scraper run
- **Build**: Jekyll build + Pagefind indexing
- **Deploy**: GitHub Pages

**Live Site**: https://awsrudy.github.io/awsrudy-vibed-01/

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if applicable)
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

Built with AI-DLC (AI-Driven Lifecycle) methodology.
