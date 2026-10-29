# Art Gallery

A static, dependency-free gallery site. Off-white background, framed pieces, wide/tall tiles sized to each artwork's shape, lazy-loaded responsive images, and a lightbox viewer (arrow keys / swipe).

## How it stays fast with lots of images

- `tools/build.py` converts each original into WebP at 480 / 960 / 1600px wide (typically 5-10x smaller than the JPEG/PNG).
- The page uses `srcset`/`sizes`, so each visitor downloads only the size their screen needs. The full 1600px version loads only in the lightbox.
- Images below the fold use `loading="lazy"`; off-screen tiles skip rendering (`content-visibility`).
- Each image's width/height is in `gallery.json`, so the layout never jumps while loading, and each tile shows the artwork's dominant colour until the image fades in.

## Adding artwork

1. Put full-size images in `originals/` (jpg, png, tiff, webp).
2. Optional: add titles etc. in `originals/metadata.json`:
   ```json
   {
     "sunset-study.jpg": { "title": "Sunset Study", "artist": "A. Painter",
                           "year": "2023", "medium": "Oil on canvas", "featured": true }
   }
   ```
   `featured: true` makes a piece a large 2x2 tile.
3. Run:
   ```bash
   pip install pillow
   python3 tools/build.py
   ```
4. Preview locally: `python3 -m http.server` then open http://localhost:8000
5. Delete the `originals/sample-*.jpg` placeholders (and their files in `images/`) once you add real work.

Tile sizes are automatic: ratio ≥ 1.55 → wide (2 columns), ≤ 0.68 → tall (2 rows), `featured` → big. Tweak the thresholds in `gallery.js` (`sizeClass`) and the row height in `style.css` (`--row`).

## Free hosting on GitHub Pages

1. Create a GitHub repo (e.g. `my-gallery`) and push this folder:
   ```bash
   git init && git add . && git commit -m "Gallery"
   git branch -M main
   git remote add origin https://github.com/<you>/my-gallery.git
   git push -u origin main
   ```
2. In the repo: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/ (root)`** → Save.
3. After a minute the site is live at `https://<you>.github.io/my-gallery/`.

`originals/` is git-ignored so your big source files stay on your computer; only the optimized `images/` are published.

### Limits and alternatives

- GitHub Pages: repo under ~1 GB, site under 1 GB, ~100 GB/month bandwidth. With optimized WebP, that's thousands of images.
- If you outgrow it: **Cloudflare Pages** (free, unlimited bandwidth, built-in CDN), **Netlify**, or put the `images/` folder in **Cloudflare R2** and point the `src` paths in `gallery.json` at it.
