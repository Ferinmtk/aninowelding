# Anino Welding Kenya — aninowelding.com

Static site, no framework. Python 3 + ImageMagick to build; Netlify to host.

## Edit & build

- Business details (phone, email, location, hours): `SITE` at the top of `tools/build.py`
- Pages: `src/pages/*.html` · shared header/footer: `src/partials/layout.html`
- Styles: `assets/css/style.css` · JS: `assets/js/main.js`

```bash
python3 tools/photos.py   # after adding photos to photos-original/ (edit PHOTOS list first)
python3 tools/build.py    # → dist/
cd dist && python3 -m http.server 8731   # preview at http://localhost:8731
```

## Deploy (Netlify, free)

1. Push this folder to a GitHub repo, then Netlify → *Add new site → Import from Git*.
   `netlify.toml` already sets build command + `dist/` publish folder.
   (Or: run the build and drag `dist/` onto app.netlify.com/drop.)
2. Netlify → *Forms* → enable form detection → *Form notifications* → email to the client.
3. *Domain management* → add `aninowelding.com`, follow the DNS instructions. HTTPS is automatic.

## Email (free)

`info@aninowelding.com` needs forwarding set up at the domain's DNS host:
registrar's free email forwarding, or Cloudflare DNS → *Email Routing* → forward to the client's Gmail.

## SEO — done in the site

- Unique title + description per page, keyword H1s ("welding in Syokimau")
- LocalBusiness + FAQ structured data (JSON-LD)
- `sitemap.xml`, `robots.txt`, canonical URLs, `lang="en-KE"`
- Link-preview image (`og-image.jpg`) for WhatsApp/Facebook shares
- Alt text on every photo, WebP images, lazy loading, no heavy scripts

## SEO — launch checklist (outside the site, all free)

1. **Google Business Profile** (business.google.com) — the biggest win for
   "welding near me" / Google Maps searches. Category *Welder*, workshop pin in Syokimau,
   phone, website link, upload the same photos. Needs postcard/phone/video verification.
2. **Google Search Console** — add `aninowelding.com`, submit `https://aninowelding.com/sitemap.xml`.
3. **Bing Webmaster Tools** — import from Search Console (one click).
4. Put the website link on the client's WhatsApp Business profile, Facebook, TikTok, Instagram.
5. Ask happy customers for Google reviews.

## Open items (client)

- [ ] Confirm email address
- [ ] Confirm working hours (currently a placeholder: Mon–Sat 8am–6pm)
- [ ] Exact workshop Google Maps pin (contact page map shows Syokimau generally)
- [ ] About page facts (year started, who runs it)
- [ ] Photo `p10` came from an "Odhis Chuma Syokimau" screenshot — confirm it's their work
- [ ] Social media links (add to footer + `sameAs` in the structured data)
