# Setup Guide

Follow these steps to get your AWS Blog Search site up and running.

## Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings**
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

Your site will be published at: `https://awsrudy.github.io/awsrudy-vibed-01/`

## Step 2: Run Initial Scrape

The scraper needs to run once to populate the blog data:

### Option A: Trigger GitHub Action (Recommended)

1. Go to the **Actions** tab in your repository
2. Click on **"Scrape AWS Blogs"** workflow
3. Click **"Run workflow"** button
4. Select branch: `main`
5. Click **"Run workflow"**

Wait 2-3 minutes for the workflow to complete. It will:
- Fetch posts from 19 AWS blog RSS feeds
- Generate `data/blogs.json`
- Commit and push the changes

### Option B: Run Locally

If you want to run the scraper locally first:

```bash
# Clone the repository
git clone https://github.com/awsrudy/awsrudy-vibed-01.git
cd awsrudy-vibed-01

# Install Python dependencies
pip install -r requirements.txt

# Run the scraper
python scraper.py

# Commit and push
git add data/blogs.json
git commit -m "Initial blog data"
git push
```

## Step 3: Verify Your Site

1. Wait 1-2 minutes after the workflow completes for GitHub Pages to rebuild
2. Visit your site: `https://awsrudy.github.io/awsrudy-vibed-01/`
3. You should see the blog posts loaded
4. Try searching for keywords like "Lambda", "S3", or "Security"

## Step 4: Customize (Optional)

### Change Update Frequency

Edit `.github/workflows/scrape-blogs.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

Change to:
- `'0 */6 * * *'` for every 6 hours
- `'0 6,18 * * *'` for twice daily (6 AM and 6 PM)
- `'0 6 * * 1'` for weekly on Mondays

### Add More AWS Feeds

Edit `scraper.py` and add to the `AWS_FEEDS` dictionary:

```python
AWS_FEEDS = {
    "Your Category": "https://aws.amazon.com/blogs/your-category/feed/",
    # ... existing feeds
}
```

### Customize Appearance

Edit `styles.css` to change colors, fonts, and layout:

```css
:root {
    --aws-orange: #FF9900;  /* Change to your preferred color */
    --aws-dark: #232F3E;
    /* ... other variables */
}
```

## Troubleshooting

### Site shows "404 Not Found"

- Wait 2-3 minutes after enabling GitHub Pages
- Check that GitHub Pages is enabled for the correct branch
- Verify the repository is public or you have GitHub Pro

### No blog posts showing

- Check if `data/blogs.json` exists in the repository
- Look at the Actions tab to see if the workflow ran successfully
- Check browser console for JavaScript errors (F12)

### Workflow fails

- Go to Actions tab and click on the failed workflow
- Check the error logs
- Common issues:
  - Rate limiting from RSS feeds (will resolve on next run)
  - Network timeouts (retry the workflow)

### Search not working

- Clear browser cache
- Check browser console for errors
- Verify `data/blogs.json` is accessible at:
  `https://awsrudy.github.io/awsrudy-vibed-01/data/blogs.json`

## Monitoring

### Check Workflow Status

Go to **Actions** tab to see:
- Last run time
- Success/failure status
- Logs for debugging

### View Data File

Check the generated data:
```
https://awsrudy.github.io/awsrudy-vibed-01/data/blogs.json
```

### Workflow Runs

The workflow will automatically run daily at 6 AM UTC. You can also:
- Trigger it manually from the Actions tab
- It will run on push to main branch (for testing)

## Next Steps

1. ⭐ Star the repository
2. 📢 Share with your team
3. 🎨 Customize the styling to match your brand
4. 📊 Add analytics (Google Analytics, Plausible, etc.)
5. 🔔 Set up notifications for workflow failures

## Support

If you encounter issues:
1. Check this guide again
2. Review the README.md
3. Check existing GitHub Issues
4. Open a new Issue with details

Happy searching! 🚀
