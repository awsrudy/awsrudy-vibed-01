# 🚀 AWS Blog Search - Automated Blog Aggregator

A GitHub Pages site that automatically scrapes AWS blogs daily and provides a high-quality search and retrieval interface.

## 🌟 Features

- **Automated Daily Updates**: GitHub Actions automatically scrapes 19+ AWS blog feeds every day
- **Powerful Search**: Fuzzy search powered by Fuse.js for finding relevant content
- **Multi-Category Filtering**: Filter by blog categories (Security, Machine Learning, DevOps, etc.)
- **Smart Tagging**: Automatically extracts AWS service names and topics from posts
- **Responsive Design**: Beautiful, mobile-friendly interface with AWS branding
- **Real-time Search**: Search results update as you type
- **Sort Options**: Sort by date (newest/oldest) or relevance
- **Direct Links**: Click through to read full articles on AWS blogs

## 📋 AWS Blog Sources

The scraper aggregates content from 19 official AWS blog feeds:

- AWS News Blog
- Architecture Blog
- Big Data Blog
- Business Intelligence
- Compute Blog
- Database Blog
- DevOps Blog
- Machine Learning
- Mobile Blog
- Networking & Content Delivery
- Security Blog
- Serverless Blog
- Storage Blog
- Startups Blog
- Public Sector
- Gaming
- IoT
- Containers
- Front-End Web & Mobile

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           GitHub Actions (Daily Cron)           │
│                                                 │
│  1. Fetch RSS feeds from AWS blogs              │
│  2. Parse and clean content                     │
│  3. Extract tags and metadata                   │
│  4. Generate blogs.json                         │
│  5. Commit and push to main branch              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              GitHub Pages                       │
│                                                 │
│  • Static HTML/CSS/JS site                     │
│  • Fuse.js for client-side search              │
│  • Reads from data/blogs.json                  │
└─────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- GitHub account
- Python 3.11+ (for local testing)

### Setup

1. **Enable GitHub Pages**:
   - Go to your repository settings
   - Navigate to "Pages" section
   - Source: Deploy from a branch
   - Branch: `main` / `root`
   - Save

2. **Configure GitHub Actions**:
   - The workflow is already configured in `.github/workflows/scrape-blogs.yml`
   - It runs automatically daily at 6 AM UTC
   - You can also trigger it manually from the Actions tab

3. **First Run**:
   - Trigger the workflow manually to populate initial data
   - Go to Actions → "Scrape AWS Blogs" → "Run workflow"
   - Wait for the workflow to complete
   - Your site will be live at `https://awsrudy.github.io/awsrudy-vibed-01/`

## 🧪 Local Development

### Run the scraper locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scraper.py

# This will create data/blogs.json
```

### Test the website locally:

```bash
# Using Python's built-in server
python -m http.server 8000

# Visit http://localhost:8000
```

Or use any static file server like `live-server`, `serve`, etc.

## 📊 Data Structure

The scraper generates `data/blogs.json` with the following structure:

```json
{
  "lastUpdated": "2024-02-16T12:00:00",
  "totalPosts": 380,
  "posts": [
    {
      "title": "Introducing Amazon S3 Express One Zone",
      "link": "https://aws.amazon.com/blogs/...",
      "description": "Clean text description...",
      "category": "AWS News Blog",
      "publishDate": "2024-02-16T08:00:00",
      "tags": ["S3", "Storage", "Performance"],
      "author": "AWS"
    }
  ]
}
```

## 🎨 Customization

### Styling

Edit `styles.css` to customize the appearance:
- Change colors in CSS variables (`:root`)
- Modify layout and spacing
- Adjust responsive breakpoints

### Search Configuration

Edit `app.js` to customize search behavior:
- Adjust Fuse.js options (threshold, weights)
- Change sort options
- Modify filtering logic

### Add More Feeds

Edit `scraper.py` to add more AWS blog feeds:

```python
AWS_FEEDS = {
    "Your Category": "https://aws.amazon.com/blogs/your-feed/feed/",
    # Add more feeds here
}
```

## 🔧 Configuration

### GitHub Actions Schedule

Modify `.github/workflows/scrape-blogs.yml` to change the update frequency:

```yaml
on:
  schedule:
    # Current: Daily at 6 AM UTC
    - cron: '0 6 * * *'

    # Twice daily: 6 AM and 6 PM UTC
    # - cron: '0 6,18 * * *'

    # Every 6 hours
    # - cron: '0 */6 * * *'
```

## 📈 Features Breakdown

### Search Capabilities

- **Fuzzy Matching**: Finds results even with typos
- **Multi-field Search**: Searches titles, descriptions, categories, and tags
- **Weighted Results**: Prioritizes title matches over description matches
- **Real-time**: Updates as you type (debounced)

### Filtering

- **Category Filter**: Show only posts from specific blog categories
- **Sort Options**:
  - Newest First
  - Oldest First
  - Most Relevant (based on search score)

### Performance

- **Client-side**: All search and filtering happens in the browser
- **Fast**: No server-side processing required
- **Cached**: Fuse.js index is built once on page load
- **Lightweight**: Data file is typically under 1MB

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Workflow not running

- Check if GitHub Actions is enabled in repository settings
- Verify the workflow file syntax
- Check Actions tab for error messages

### No data showing

- Ensure the scraper has run at least once
- Check if `data/blogs.json` exists
- Verify GitHub Pages is enabled and deployed from correct branch

### Search not working

- Check browser console for JavaScript errors
- Verify Fuse.js is loading (check Network tab)
- Ensure blogs.json is accessible

## 🔮 Future Enhancements

- [ ] Add bookmarking/favorites feature (localStorage)
- [ ] Export search results to CSV/JSON
- [ ] Email notifications for new posts in specific categories
- [ ] RSS feed of filtered results
- [ ] Advanced filters (date range, author, multiple categories)
- [ ] Reading progress tracking
- [ ] Dark mode toggle
- [ ] Analytics dashboard

## 📧 Contact

For questions or suggestions, open an issue on GitHub.

---

**Built with ❤️ for the AWS community**
