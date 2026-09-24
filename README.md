# CHECK THE SHOP

A static San Jose cannabis license lookup. Python 3 and Node.js, no package dependencies.

Live: https://eugiene300-maker.github.io/check-the-shop

## Commands

```
python3 scripts/refresh.py   # fetch state (DCC) and city (SJPD) records
python3 scripts/build.py     # regenerate dist/
python3 scripts/check.py     # validate output
npm test                     # search tests
```

## Data

`data/state.json` holds selected business fields from the public API behind the DCC license search. `data/city.json` holds the dated SJPD list. `refresh.py` validates new records and keeps the last valid snapshot if a source fails; a failed fetch never advances its review date. Personal owner contact details are never displayed.

State status and city address matches are separate. An address match is not an ownership match, and a missing result is not a finding that a business is unlicensed.

## Deployment

Primary address: https://eugiene300-maker.github.io/check-the-shop/ (GitHub Pages, published by `.github/workflows/pages.yml` on every push to `main` and after each scheduled refresh). Canonical URLs, the sitemap and llms.txt point to this address; it is set in `data/config.json`.

Mirrors on other static hosts: output directory `dist`. To keep the canonical pointing at the primary address, use no build command. To give a mirror its own canonical and sitemap, use build command `python3 scripts/build.py` with Python 3.12+ and set the `SITE_URL` environment variable to that host's address.

The sponsored link stays clearly labeled. Search order is source status and alphabetic, never sponsor priority.
