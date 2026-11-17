# Generated art — 2026-11-16

Images created for this update and exported to WebP for fast mobile loading:

- `ui_energizer.webp`: lavender energy drink can for the composer action and consumption animation.
- `courier_top.webp`: scooter and rider viewed strictly from above, facing north.
- `lock_face.webp`: front-facing brass lock cylinder.
- `catch_basket.webp`: lavender-lined basket.
- `portrait_female.webp`, `portrait_male.webp`: neutral adult anime base portraits without caps or headphones.

The original generated PNGs remain in the workspace image library. Personalized character portraits are generated at runtime through the configured image provider from validated hair, color, skin, eye and accessory choices. The fixed base art is a fallback, not a pre-generated image of every possible combination.

## 2026-11-17 — shop-style work sprites and instant appearance preview

The runtime portrait jobs described above are retired. Creation and appearance changes now use a deterministic local vector mannequin (`avatar_preview.py`), with live hair, skin, eyes, accessories and species changes. No model task is submitted or energy consumed by this preview. Existing uploaded avatars remain supported. Chat photographs still use the external image provider.

Twenty new `work_*.webp` sprites replace the older outlined PNG illustrations in catch, courier parcels and farm: bomb, coins, banknotes, magnet, dry/wet beds, seedling, young plant, six crops, droplet, parcel, shield, hourglass, bonus coins and watering can. The new art uses soft painted materials, natural muted colors and no neon outline, matching the shop illustrations. Total payload is approximately 296 KiB.

Original generated atlases remain in the workspace image library:

- `exec-5718e791-ea1d-46b5-8a07-d65e1dc79ad0.png` (4 × 4).
- `exec-9c487766-7527-4484-ba7f-ec188c435073.png` (2 × 2).

Export with `python scripts/extract_work_art.py first-atlas.png second-atlas.png`. Original atlases are preserved. Old PNG assets remain for compatibility but are not used by the updated work sprite renderer.
