// AWS Blog Scraper - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  console.log('AWS Blog Scraper loaded');

  // Mobile navigation toggle (if needed)
  // Add any interactive features here

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Log stats if available
  const statsBar = document.querySelector('.stats-bar');
  if (statsBar) {
    console.log('Stats loaded successfully');
  }

  // Performance monitoring
  if (window.performance && window.performance.timing) {
    window.addEventListener('load', function() {
      const loadTime = window.performance.timing.domContentLoadedEventEnd - window.performance.timing.navigationStart;
      console.log('Page load time:', loadTime + 'ms');
    });
  }

  // Dark mode toggle
  const darkModeToggle = document.createElement('button');
  darkModeToggle.className = 'dark-mode-toggle';
  darkModeToggle.innerHTML = '&#127763;'; // Moon/sun emoji
  darkModeToggle.title = 'Toggle dark mode';
  darkModeToggle.setAttribute('aria-label', 'Toggle dark mode');

  darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    darkModeToggle.innerHTML = isDark ? '&#9728;' : '&#127763;'; // Sun or moon
  });

  document.body.appendChild(darkModeToggle);

  // Load dark mode preference
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    darkModeToggle.innerHTML = '&#9728;'; // Sun emoji
  }

  // Quick search functionality
  const quickSearch = document.getElementById('quick-search');
  if (quickSearch) {
    quickSearch.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const query = quickSearch.value;
        window.location.href = '{{ "/search/" | relative_url }}?q=' + encodeURIComponent(query);
      }
    });
  }
});
