# Docs Template Update

Updated the `docs/` directory to use Jekyll with a custom theme, matching the kospex project documentation structure.

## Files Created

### `docs/_config.yml`
Jekyll configuration file with site title, description, and plugins.

### `docs/Gemfile`
Ruby dependencies for local development:
- `jekyll ~> 4.3` - Jekyll static site generator (Ruby 4.0+ compatible)
- `jekyll-feed` - RSS feed generation
- `jekyll-seo-tag` - SEO meta tags
- `webrick` - Local development server

**Note:** Uses Jekyll directly instead of `github-pages` gem, as `github-pages ~> 232` does not support Ruby 4.0+.

### `docs/_layouts/default.html`
Custom HTML layout with:
- Fixed navigation header with Panopticas branding
- Links to GitHub and PyPI
- Footer with quick links and related projects
- Smooth scrolling and header scroll effects

### `docs/assets/css/style.css`
Custom CSS styling including:
- Navy blue and white color scheme (matching kospex)
- Responsive navigation
- Styled tables, lists, code blocks, and blockquotes
- Mobile-friendly responsive design

### `docs/_includes/head-custom.html`
Empty include file for custom head content (analytics, fonts, etc.)

### `docs/index.md` (updated)
Added Jekyll front matter to enable layout:
```yaml
---
layout: default
title: Panopticas
---
```

## Local Testing

To test the docs locally:

```bash
cd docs

# Install dependencies (first time only)
bundle install

# Serve the site locally
bundle exec jekyll serve
```

Then open `http://localhost:4000` in your browser.

## Prerequisites

- Ruby 3.0+ (tested with Ruby 4.0.1)
- Bundler: `gem install bundler`

## Deployment

The docs automatically deploy to GitHub Pages when pushed to the repository. Since we're using Jekyll 4.x (not the github-pages gem), you may need to use GitHub Actions for deployment. The custom domain `panopticas.io` is configured via the existing `CNAME` file.

## Troubleshooting

### Ruby version errors
The `github-pages` gem requires Ruby < 4.0. This setup uses Jekyll directly to support Ruby 4.0+.

### Missing jekyll-seo-tag
Add to Gemfile plugins group and run `bundle install`.

### Missing head-custom.html
Create `docs/_includes/head-custom.html` (can be empty).

### No styling / directory listing
Ensure `index.md` has front matter with `layout: default`.
