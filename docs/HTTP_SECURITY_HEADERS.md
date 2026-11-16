# HTTP Security Headers — alghad.digital

## Verified current status

- Hosting: GitHub Pages legacy build, official custom domain alghad.digital with HTTPS enforcement.
- Domain nameservers: hyperion.dns-parking.com and atlas.dns-parking.com.
- On GitHub Pages, arbitrary HTTP response security headers cannot be configured from repository files.
- An HTML meta CSP **is effective** for supported CSP directives. The new generator enforces a stronger CSP in all 42 published Arabic/English pages.
- HSTS, frame-ancestors, X-Frame-Options, X-Content-Type-Options, Referrer-Policy header and Permissions-Policy **require an actual HTTP response header**, normally set at a configured CDN or proxy.
- No DNS, nameserver, or hosting provider changes are authorized or performed in this patch.

## Ready for a future CDN/proxy configuration

The following response headers are recommended **after** the site is behind a proxy that can set response headers:

    Strict-Transport-Security: max-age=31536000
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY
    Referrer-Policy: strict-origin-when-cross-origin
    Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
    Content-Security-Policy: default-src 'self'; script-src 'self'; script-src-attr 'none'; style-src 'self'; style-src-elem 'self'; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'none'; object-src 'none'; frame-src 'none'; frame-ancestors 'none'; worker-src 'none'; manifest-src 'self'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests

Do not apply HSTS includeSubDomains or preload without auditing all subdomains and planning rollback. Frame-ancestors is deliberately absent from HTML meta: browsers do not support it there.

The HTML meta CSP now blocks external scripts, inline script handlers, inline style elements, frames, workers and objects; it retains style-src-attr unsafe-inline only for compatibility with legacy UI style mutations. Existing HTML meta referrer stays strict-origin-when-cross-origin.

## Contact behavior

The website publishes the owner's explicitly authorized WhatsApp endpoint on every canonical page, opens it with noopener+noreferrer and no external SDK or tracking. Its position is above the search trigger on the same logical side, opposite the back-to-top control; it hides during search dialogs and program modals.

## Verification after each update

- Confirm CSP meta, contact link, CSS and 42 canonical pages with node tests/contact-security-test.cjs.
- Verify browser visual spacing at 320, 390, 768 and 1440 pixels.
- Run python scripts/build_contact_security.py after benefits generator and before search generator.
- Run curl -I https://alghad.digital/ and remember that **headers will remain absent until an authorized edge/proxy deployment**. Adding an ignored _headers file does not solve it.
