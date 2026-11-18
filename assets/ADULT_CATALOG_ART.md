# Adult wardrobe product artwork

These are static shop illustrations of clothing on featureless display forms, with transparent backgrounds. They are not character photos or character reference images.

32 images were generated as two 4x4 atlases, then cropped into WebP files. Originals remain in the execution workspace:

- `/workspace/generated_images/exec-1c8c0a0e-3fa8-4892-aef2-856c522a0986.png`
- `/workspace/generated_images/exec-7dc63b54-2441-4e2c-89ca-cca8847e145d.png`

Re-export with `scripts/export_adult_catalog_assets.py --first FIRST.png --second SECOND.png`. Tile order follows the 32 entries of `ADULT_CATALOG_ITEMS` in `profile_options.py`, first atlas then second, row by row.

Catalog entries retain `catalog_only=True` and empty `fact`. Their `tags` are stored product metadata and are not forwarded into chat image prompts. Purchases persist in inventory; fitting and chat photo generation for these products are not connected. Existing level and gender checks apply.
