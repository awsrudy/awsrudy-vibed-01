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
});
