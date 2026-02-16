// Global variables
let allBlogs = [];
let fuse = null;
let currentCategory = '';
let currentSort = 'date-desc';

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    await loadBlogs();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Real-time search as user types (debounced)
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300);
    });
}

// Load blog data
async function loadBlogs() {
    const loading = document.getElementById('loading');
    loading.style.display = 'block';

    try {
        const response = await fetch('data/blogs.json');
        const data = await response.json();

        allBlogs = data.posts || [];

        // Initialize Fuse.js for fuzzy search
        const fuseOptions = {
            keys: [
                { name: 'title', weight: 0.4 },
                { name: 'description', weight: 0.3 },
                { name: 'category', weight: 0.2 },
                { name: 'tags', weight: 0.1 }
            ],
            threshold: 0.4,
            includeScore: true,
            minMatchCharLength: 2
        };

        fuse = new Fuse(allBlogs, fuseOptions);

        // Populate categories
        populateCategories();

        // Update last updated time
        if (data.lastUpdated) {
            const lastUpdate = document.getElementById('lastUpdate');
            const date = new Date(data.lastUpdated);
            lastUpdate.textContent = `Last updated: ${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
        }

        // Display all blogs initially
        displayBlogs(allBlogs);

    } catch (error) {
        console.error('Error loading blogs:', error);
        document.getElementById('results').innerHTML = `
            <div class="error">
                <h3>Error loading blog posts</h3>
                <p>Please try refreshing the page. If the problem persists, check if the data file exists.</p>
            </div>
        `;
    } finally {
        loading.style.display = 'none';
    }
}

// Populate category filter
function populateCategories() {
    const categories = [...new Set(allBlogs.map(blog => blog.category))].sort();
    const categoryFilter = document.getElementById('categoryFilter');

    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

// Perform search
function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    currentCategory = document.getElementById('categoryFilter').value;
    currentSort = document.getElementById('sortBy').value;

    let results = [];

    if (query === '') {
        // No search query, show all or filtered results
        results = allBlogs;
    } else {
        // Perform fuzzy search
        const fuseResults = fuse.search(query);
        results = fuseResults.map(result => result.item);
    }

    // Filter by category
    if (currentCategory) {
        results = results.filter(blog => blog.category === currentCategory);
    }

    // Sort results
    results = sortBlogs(results);

    displayBlogs(results);
}

// Sort blogs
function sortBlogs(blogs) {
    const sorted = [...blogs];

    switch(currentSort) {
        case 'date-desc':
            sorted.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate));
            break;
        case 'date-asc':
            sorted.sort((a, b) => new Date(a.publishDate) - new Date(b.publishDate));
            break;
        case 'relevance':
            // Already sorted by relevance from Fuse.js
            break;
    }

    return sorted;
}

// Display blogs
function displayBlogs(blogs) {
    const resultsContainer = document.getElementById('results');
    const noResults = document.getElementById('noResults');
    const resultCount = document.getElementById('resultCount');

    resultCount.textContent = `Showing ${blogs.length} of ${allBlogs.length} posts`;

    if (blogs.length === 0) {
        resultsContainer.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }

    resultsContainer.style.display = 'grid';
    noResults.style.display = 'none';

    resultsContainer.innerHTML = blogs.map(blog => createBlogCard(blog)).join('');
}

// Create blog card HTML
function createBlogCard(blog) {
    const date = new Date(blog.publishDate).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    const tagsHTML = blog.tags && blog.tags.length > 0
        ? `<div class="blog-tags">
            ${blog.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
           </div>`
        : '';

    return `
        <article class="blog-card">
            <div class="blog-meta">
                <span class="blog-category">${blog.category}</span>
                <span>📅 ${date}</span>
            </div>
            <h3><a href="${blog.link}" target="_blank" rel="noopener noreferrer">${blog.title}</a></h3>
            <p class="blog-description">${blog.description}</p>
            ${tagsHTML}
            <a href="${blog.link}" class="read-more" target="_blank" rel="noopener noreferrer">Read More →</a>
        </article>
    `;
}

// Clear all filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('sortBy').value = 'date-desc';
    currentCategory = '';
    currentSort = 'date-desc';
    displayBlogs(allBlogs);
}
