# wtchtwr Data Quality Report

- Status: `attention`
- Highbury listings: `38`
- Market listings: `36403`
- Review rows: `657704`
- Schema contracts ok: `True`

## Key Checks

- Duplicate listing IDs: `{'highbury': 0, 'market': 0}`
- Invalid coordinates: `{'highbury': 0, 'market': 0}`
- Impossible prices: `{'highbury': 0, 'market': 115}`
- Inconsistent borough labels: `[]`
- Listing null rates: `{'price_null_rate': 0.0, 'occupancy_null_rate': 0.0, 'revenue_null_rate': 0.0, 'rating_null_rate': 0.0}`
- Review null rates: `{'comments_null_rate': 0.0, 'sentiment_label_null_rate': 0.0, 'compound_null_rate': 0.0}`
- Duplicate reviews: `0`

## Open Issues

- Impossible or missing prices found in listing tables.
