# CHECK THE SHOP

A static San Jose cannabis license lookup. Python 3 and Node.js, no package dependencies.

Live: https://check-the-shop.web.app

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

Publish `dist/` to any static host; no build step is required. Set the final public address in `data/config.json` (or the `SITE_URL` environment variable) and run `python3 scripts/build.py` so canonical URLs, sitemap and llms.txt match. The scheduled workflow in `.github/workflows/` refreshes source data, rebuilds and commits the updated pages.
