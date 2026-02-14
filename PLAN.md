# AWS Blog Search Website - Implementation Plan

## Project Overview

Build a static website to search and serve AWS blog posts with:
- User-friendly interface
- Local storage for favorite posts and categories
- Hosted on GitHub Pages
- Deployed via GitHub Actions
- Hourly RSS feed scraping
- Lunr.js search indexing
- Vanilla JavaScript frontend

---

## Architecture

### High-Level Structure

```
awsrudy-vibed-01/
├── .github/
│   └── workflows/
│       ├── fetch-blogs.yml      # Hourly RSS scraping
│       └── deploy.yml           # GitHub Pages deployment
├── src/
│   ├── index.html               # Main page
│   ├── css/
│   │   └── styles.css          # Styling
│   ├── js/
│   │   ├── app.js              # Main application logic
│   │   ├── search.js           # Lunr.js search implementation
│   │   ├── favorites.js        # LocalStorage management
│   │   └── categories.js       # Category management
│   └── assets/
│       └── logo.svg            # Branding assets
├── data/
│   ├── blogs.json              # RSS feed data (generated)
│   └── search-index.json       # Lunr.js index (generated)
├── scripts/
│   ├── fetch-rss.js            # Node.js RSS fetcher
│   └── build-index.js          # Lunr.js index builder
├── package.json                # Dependencies
├── .gitignore
└── README.md
```

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Initialize Project Structure
- Create directory structure
- Set up `package.json` with dependencies:
  - `rss-parser` (RSS feed parsing)
  - `lunr` (search indexing)
  - Dev dependencies for building

### 1.2 Configure GitHub Actions

#### Workflow 1: `fetch-blogs.yml`
**Trigger:** Hourly (cron: `0 * * * *`)

**Steps:**
1. Checkout repository
2. Setup Node.js environment
3. Install dependencies
4. Run `scripts/fetch-rss.js` to scrape AWS blog RSS feed
5. Run `scripts/build-index.js` to generate Lunr.js search index
6. Commit updated `data/blogs.json` and `data/search-index.json`
7. Push changes back to repository
8. Trigger deployment workflow

#### Workflow 2: `deploy.yml`
**Trigger:** On push to main branch

**Steps:**
1. Checkout repository
2. Build static assets (if needed)
3. Deploy to GitHub Pages using `peaceiris/actions-gh-pages@v3`

### 1.3 GitHub Pages Configuration
- Configure repository settings for GitHub Pages
- Set source to `gh-pages` branch
- Custom domain support (optional)

---

## Phase 2: RSS Feed Scraping

### 2.1 RSS Fetcher Script (`scripts/fetch-rss.js`)

**Functionality:**
- Fetch AWS blog RSS feed(s):
  - Main AWS blog: `https://aws.amazon.com/blogs/aws/feed/`
  - Additional feeds (compute, security, architecture, etc.)
- Parse RSS entries
- Extract fields:
  - `title`
  - `description` / `excerpt`
  - `link` (URL)
  - `pubDate` (publication date)
  - `categories` / `tags`
  - `author`
  - `guid` (unique identifier)
- Deduplicate entries (by GUID)
- Sort by date (newest first)
- Output to `data/blogs.json`

**Data Schema (`blogs.json`):**
```json
{
  "lastUpdated": "2025-02-14T16:00:00Z",
  "posts": [
    {
      "id": "unique-guid",
      "title": "Post Title",
      "description": "Post description...",
      "link": "https://aws.amazon.com/blogs/...",
      "pubDate": "2025-02-14T10:00:00Z",
      "categories": ["Compute", "EC2"],
      "author": "Author Name"
    }
  ]
}
```

### 2.2 Multiple Feed Support
AWS has multiple category-specific feeds:
- `/blogs/aws/` - Main AWS blog
- `/blogs/compute/` - Compute
- `/blogs/security/` - Security
- `/blogs/architecture/` - Architecture
- `/blogs/database/` - Database
- `/blogs/developer/` - Developer tools
- `/blogs/devops/` - DevOps
- `/blogs/machine-learning/` - ML/AI
- `/blogs/networking-and-content-delivery/` - Networking
- `/blogs/storage/` - Storage

**Strategy:** Fetch from multiple feeds and merge into single dataset

---

## Phase 3: Search Index Building

### 3.1 Lunr.js Index Builder (`scripts/build-index.js`)

**Functionality:**
- Load `data/blogs.json`
- Create Lunr.js index with fields:
  - `title` (boosted weight: 3x)
  - `description` (weight: 2x)
  - `categories` (weight: 2x)
  - `author` (weight: 1x)
- Configure Lunr.js:
  - Enable stemming
  - Enable stop word removal
  - Support partial matching
- Serialize index to `data/search-index.json`

**Index Configuration:**
```javascript
lunr(function() {
  this.ref('id')
  this.field('title', { boost: 3 })
  this.field('description', { boost: 2 })
  this.field('categories', { boost: 2 })
  this.field('author')

  // Add all documents
  posts.forEach(post => this.add(post))
})
```

---

## Phase 4: Frontend Development

### 4.1 HTML Structure (`src/index.html`)

**Layout:**
```
┌─────────────────────────────────────────┐
│ Header: AWS Blog Search                │
│ [Search Bar...........................]  │
│ [🔍 Search] [Filter▼] [★ Favorites]   │
├─────────────────────────────────────────┤
│ Sidebar (Categories)  │  Main Content   │
│ ☐ All (1234)          │  ┌─────────────┐│
│ ☐ Compute (456)       │  │ Post Card   ││
│ ☐ Security (234)      │  │ Title       ││
│ ☐ Architecture (123)  │  │ Excerpt...  ││
│ ☐ Database (345)      │  │ Date | ★    ││
│ ☐ ML/AI (234)         │  └─────────────┘│
│ ...                   │  ┌─────────────┐│
│                       │  │ Post Card   ││
│ [My Categories ▼]     │  └─────────────┘│
│ • Work                │  ...            │
│ • Personal            │                 │
└─────────────────────────────────────────┘
```

**Key Elements:**
- **Header:** Logo, title, search input
- **Sidebar:** Category filter, custom categories
- **Main:** Search results / blog post cards
- **Post Card:** Title, excerpt, date, favorite button, category badges
- **Favorites View:** Toggle to show only favorited posts

### 4.2 CSS Styling (`src/css/styles.css`)

**Design Principles:**
- Modern, clean design
- Responsive layout (mobile-first)
- AWS branding colors (orange, dark gray)
- Card-based post display
- Smooth transitions and hover effects

**Responsive Breakpoints:**
- Mobile: < 768px (single column)
- Tablet: 768px - 1024px (collapsible sidebar)
- Desktop: > 1024px (full layout)

### 4.3 JavaScript Modules

#### `app.js` - Main Application
**Responsibilities:**
- Initialize application
- Load blog data and search index
- Coordinate between modules
- Handle routing/state management
- Render post cards
- Handle pagination

**Key Functions:**
```javascript
async function init()
async function loadData()
function renderPosts(posts)
function renderPostCard(post)
function handlePagination()
```

#### `search.js` - Search Functionality
**Responsibilities:**
- Load Lunr.js index
- Handle search queries
- Filter by categories
- Sort results by relevance/date

**Key Functions:**
```javascript
async function loadSearchIndex()
function search(query, filters)
function filterByCategory(posts, categories)
function sortResults(posts, sortBy)
```

#### `favorites.js` - LocalStorage Management
**Responsibilities:**
- Add/remove favorites
- Retrieve favorites list
- Persist to localStorage
- Handle favorites view

**LocalStorage Schema:**
```javascript
{
  "favorites": ["post-id-1", "post-id-2"],
  "customCategories": {
    "Work": ["post-id-3", "post-id-4"],
    "Personal": ["post-id-5"]
  }
}
```

**Key Functions:**
```javascript
function addFavorite(postId)
function removeFavorite(postId)
function isFavorite(postId)
function getFavorites()
function toggleFavoritesView()
```

#### `categories.js` - Category Management
**Responsibilities:**
- Create custom categories
- Add posts to categories
- Remove posts from categories
- Display category assignments

**Key Functions:**
```javascript
function createCategory(name)
function deleteCategory(name)
function addToCategory(postId, categoryName)
function removeFromCategory(postId, categoryName)
function getPostCategories(postId)
function getAllCustomCategories()
```

---

## Phase 5: Features Implementation

### 5.1 Search Features
- **Full-text search** using Lunr.js
- **Real-time search** (debounced input)
- **Search suggestions** (optional)
- **Highlight search terms** in results
- **Advanced filters:**
  - Date range
  - Category
  - Author

### 5.2 Favorites System
- **Star button** on each post card
- **Visual indicator** for favorited posts
- **Favorites view** (filter to show only favorites)
- **Export favorites** (JSON download)
- **Import favorites** (JSON upload)

### 5.3 Custom Categories
- **Create category** modal/form
- **Drag-and-drop** posts to categories (optional enhancement)
- **Multi-select** to add posts to categories
- **Category badges** on post cards
- **Filter by custom category**

### 5.4 User Experience
- **Loading states** (spinner, skeleton screens)
- **Empty states** (no results, no favorites)
- **Error handling** (failed to load data)
- **Keyboard shortcuts:**
  - `/` - Focus search
  - `Esc` - Clear search
  - `f` - Toggle favorites view
- **Accessibility:**
  - ARIA labels
  - Keyboard navigation
  - Screen reader support

---

## Phase 6: GitHub Actions Implementation

### 6.1 Hourly RSS Fetch Workflow

**File:** `.github/workflows/fetch-blogs.yml`

```yaml
name: Fetch AWS Blogs

on:
  schedule:
    - cron: '0 * * * *'  # Every hour
  workflow_dispatch:  # Manual trigger

jobs:
  fetch-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: node scripts/fetch-rss.js
      - run: node scripts/build-index.js
      - name: Commit and push if changed
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update AWS blog data [skip ci]" && git push)
```

### 6.2 GitHub Pages Deployment

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./src
          publish_branch: gh-pages
```

---

## Phase 7: Testing & Optimization

### 7.1 Testing
- **Manual testing:** All features across browsers
- **Performance testing:** Load time, search speed
- **Mobile testing:** Responsive design
- **LocalStorage testing:** Data persistence

### 7.2 Performance Optimization
- **Minify CSS/JS** (optional, can use CDN)
- **Lazy load images** (if blog posts include images)
- **Pagination** for large result sets
- **Debounce search input** (300ms delay)
- **Cache search results** (in memory)

### 7.3 SEO & Metadata
- Meta tags (title, description, og:tags)
- Sitemap generation (optional)
- Robots.txt

---

## Phase 8: Documentation & Deployment

### 8.1 Documentation
- **README.md:**
  - Project description
  - Features list
  - Local development setup
  - Deployment instructions
  - Contributing guidelines
- **User Guide:** (in-app or separate page)
  - How to search
  - How to use favorites
  - How to create categories

### 8.2 Initial Deployment
1. Enable GitHub Pages in repository settings
2. Trigger initial RSS fetch workflow
3. Verify deployment to GitHub Pages
4. Test live site

---

## Technology Stack Summary

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling, Flexbox/Grid
- **Vanilla JavaScript** - No framework dependencies
- **Lunr.js** - Client-side search

### Build & Deploy
- **Node.js** - RSS fetching and index building
- **GitHub Actions** - CI/CD automation
- **GitHub Pages** - Static site hosting

### Dependencies
```json
{
  "dependencies": {
    "rss-parser": "^3.13.0",
    "lunr": "^2.3.9"
  },
  "devDependencies": {}
}
```

---

## Implementation Order

1. **Project Setup** (30 min)
   - Initialize directory structure
   - Create package.json
   - Basic .gitignore

2. **RSS Scraper** (1 hour)
   - Implement fetch-rss.js
   - Test with AWS blog feeds
   - Generate blogs.json

3. **Search Index Builder** (45 min)
   - Implement build-index.js
   - Configure Lunr.js
   - Generate search-index.json

4. **GitHub Actions** (1 hour)
   - Create fetch-blogs.yml workflow
   - Create deploy.yml workflow
   - Test workflows

5. **HTML Structure** (1 hour)
   - Create index.html
   - Semantic markup
   - Accessibility attributes

6. **CSS Styling** (2 hours)
   - Create styles.css
   - Responsive layout
   - Component styles

7. **Core JavaScript** (3 hours)
   - app.js - Main logic
   - search.js - Search implementation
   - favorites.js - LocalStorage
   - categories.js - Category management

8. **Polish & Testing** (2 hours)
   - Cross-browser testing
   - Mobile responsive testing
   - Performance optimization
   - Bug fixes

9. **Documentation** (1 hour)
   - README.md
   - Code comments
   - User guide

**Total Estimated Time:** ~12 hours

---

## Future Enhancements (Post-MVP)

- **Dark mode** toggle
- **RSS feed export** (of favorites)
- **Social sharing** buttons
- **Print-friendly** view
- **Advanced filters:** author, date range picker
- **Keyboard shortcuts** help modal
- **Analytics** (privacy-friendly, optional)
- **PWA support** (offline access)
- **Multi-language** support
- **Comment system** (Disqus/Utterances)

---

## Risk Mitigation

### Risk 1: AWS Changes RSS Feed Format
**Mitigation:** Regular testing, fallback to cached data, error logging

### Risk 2: GitHub Actions Rate Limiting
**Mitigation:** Hourly schedule is well within limits, add retry logic

### Risk 3: Large Dataset Performance
**Mitigation:** Pagination, lazy loading, index optimization

### Risk 4: LocalStorage Quota (5-10MB)
**Mitigation:** Limit favorites, compress data, warn user when near quota

---

## Success Criteria

✅ Users can search AWS blog posts with Lunr.js
✅ Search results are relevant and fast (<1s)
✅ Users can favorite posts (persisted in localStorage)
✅ Users can create custom categories for posts
✅ Site updates hourly with new AWS blog posts
✅ Site is responsive on mobile, tablet, desktop
✅ GitHub Actions workflows run successfully
✅ Site is deployed to GitHub Pages
✅ Documentation is complete and accurate

---

## Conclusion

This plan provides a comprehensive roadmap for building a static AWS blog search website with modern features, automated updates, and excellent user experience. The vanilla JavaScript approach ensures fast load times and no framework lock-in, while Lunr.js provides powerful client-side search without requiring a backend.
