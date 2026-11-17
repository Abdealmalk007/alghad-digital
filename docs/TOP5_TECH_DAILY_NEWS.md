# Daily Global Top 5 Technology News

Updated: 2026-11-17

## Publishers
- The Verge — https://www.theverge.com/rss/tech/index.xml
- TechCrunch — https://techcrunch.com/feed/
- Ars Technica — https://feeds.arstechnica.com/arstechnica/index
- WIRED — https://www.wired.com/feed/tag/ai/latest/rss
- Engadget — https://www.engadget.com/rss.xml

Only HTTPS articles from the publisher's own allowed hostname are accepted. No external full-text article copying or imagery. Headlines, actual publication dates, publisher names, and direct links are displayed.

## Automated pipeline (GitHub Actions)
- Existing workflow: `.github/workflows/update-tech-news.yml`
- Primary schedule: 04:30 UTC = 07:30 Riyadh; extra best-effort backup cron triggers
- `update_news.py`: fetch feeds, exclude coupons/promotions, rank significant technology announcements, keep 2 items per available top-five publisher if eligible, then combine all sources into 36 articles (max 5 per source)
- `translate_news.py`: translate English headline text into Arabic with cached translations, prioritized for the five international publishers; never invent an Arabic translation when the API fails
- `build_seo.py`: show up to 10 selected international headlines separately at `/news/`, then render the remaining attributed news with no duplicate article links
- `build_en.py`: show the same original-language international stories at `/en/news/`
- `prerender_home.py`: retain concise news digest below ProTech software on homepage
- `build_site_search.py`: index the updated source-attributed news
- `tests/global-tech-daily-editorial-test.cjs`: regression of translation, original links, selection and schedule

## Editorial behavior
- The priority score is a **heuristic**, not a claim of objectively ranked global importance: recency, security incidents, releases, launches and important software/hardware announcements are favored.
- Exclude promotional/affiliate coupon and shopping deal headlines; deprioritize generic buying guides and review lists.
- Keep publisher diversity. An unavailable or stale feed creates **no fabricated stories** and does not prevent other sources from updating.
- Publication date is always from RSS; the site's refresh timestamp is separate.
- Translations are marked as machine translation; original English title remains visible for verification on the Arabic page.
- Display publisher and direct original-story link `rel="noopener noreferrer"`; published abstracts remain brief and linked.
- If translation is unavailable, show the original headline with an explicit Arabic notice rather than an incorrect translated headline.
- No guarantee of the exact execution minute due to GitHub scheduled workflow best-effort behavior.

## QA
Run the workflow and local checks:
```powershell
python scripts/update_news.py
python scripts/update_industry_news.py
python scripts/translate_news.py
python scripts/prerender_home.py
python scripts/build_seo.py
python scripts/build_support_pages.py
python scripts/build_en.py
python scripts/build_topic_tags.py
python scripts/build_program_experience.py
python scripts/build_contact_security.py
python scripts/build_analytics.py
python scripts/optimize_search_visibility.py
python scripts/build_site_search.py
node tests/global-tech-sources-test.cjs
node tests/global-tech-daily-editorial-test.cjs
node tests/translation-test.cjs
```
