# Site source

Edit `en.html` (English) and `et.html` (Estonian), then run:

    python3 _src/build.py

This rebuilds every page (/, /work/, /services/ ... and /et/...) and sitemap.xml.
Page titles, descriptions and the film list for Google live at the top of `build.py`.
GitHub Pages does not publish folders that start with `_`.
