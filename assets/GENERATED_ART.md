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

## 2026-11-17 — world-specific generated portrait presets and wardrobe

The appearance preview now uses **32 generated portrait presets**, replacing the vector hair and head drawings: 8 hairstyles × 2 genders × 2 worlds. Anime uses the clearly illustrated atlas `exec-c0dbb6d9-18a8-4d80-b096-1a30904f208b.png`; realism uses `exec-3872393d-9aec-4d8f-b547-cf1a2094ceae.png`. Each world/gender has a consistent face and its own hair set. Assets are `avatar_{world}_{gender}_{hairstyle}.webp`.

Local SVG compositing adds selected hair/skin/iris colors, race details and accessories. Hair is generated raster artwork, with pigment masks for color changes. Iris changes use separate masks calibrated to the portrait's eye line. No provider job or energy charge is started by the builder. Browser pixel comparisons verify both irises change, surrounding skin stays unchanged, and hair recoloring preserves the face/neck. Previews remain approximate references for subsequent provider-generated photographs.

`wardrobe_bunny.webp`, `wardrobe_latex.webp`, `wardrobe_stockings.webp` come from the clothing-only atlas `exec-7baf6727-6112-414f-ae47-7dd45ede9df9.png`. Dress and heels reuse their existing matching shop illustrations. The fitting room is a free local, fully clothed outfit preview.

Build with `python scripts/export_avatar_presets.py anime-atlas.png realism-atlas.png wardrobe-atlas.png`. Source PNGs remain unchanged in the workspace image library; mobile WebP exports are committed.

## 24 November 2026

Generated a 4×4 sheet of sixteen opaque everyday mannequin outfit combinations and a separate plum/ivory calendar-and-clock icon. `scripts/export_nov24_assets.py` only crops/registers/resizes these originals into `nov24_look_0.webp` through `nov24_look_15.webp` and `offer_calendar_nov24.webp`. New complete looks are catalog/inventory gated; existing public look keys with identical clothes now use the newer art. `scripts/calibrate_fitting.py` includes the new whole mannequins for accessory registration. This is an expanded set of examples, not an exhaustive rendering of all clothing permutations.

## Work preview icons — 24 November 2026

Generated one transparent three-cell sheet containing a muted wicker basket, an ice snowflake, and a basket-with-expansion-arrows powerup. `scripts/export_work_v2_assets.py` only crops, registers and scales its source into `work_basket_v2.webp`, `work_freeze_v2.webp` and `work_wide_v2.webp`. The new work UI selects these assets; public legacy work retains its current visuals until release.

## Coaching and work orders — 24 November 2026

Generated an arrow-free lilac hand cursor and three states of an ordinary shipping carton (closed, intact/open, damaged), source atlas `exec-98155086-4584-4e53-971e-fc3bb8cc0b42.png`. The exported cursor uses a 96×112 canvas with its fingertip registered at (48, 8), shared by the tour and energizer. Swipe trails, fades and tap motion are UI animations, not baked arrows. Generated decorative ceramic commission `exec-33e4301e-e3d4-4f1f-a7db-7002b4ed9e11.png` supplies the mosaic reference and tile fragments.

Export: `python scripts/export_coach_assets.py cursor-cartons-atlas.png mosaic.png`. This only crops, registers and scales the original images; source originals remain in the workspace image library. Assets: `coach_finger.webp`, `work_crate_{closed,open,damaged}.webp`, `work_mosaic_order.webp`.

## Complete wearable catalog — 24 November 2026

Generated 17 eight-cell atlases covering all **96 wearable catalog keys** and every supported sex/item pair: **133 whole mannequin views**, plus two neutral white-shirt/white-shorts bases and one registration reference. This includes full outfits, separate clothes, footwear, hats, glasses, necklaces, earrings and wrist accessories. These are neutral store mannequin renders; toys have no wearable slot and remain separate product cards.

`fitting_catalog.json` records each cell's item, sex, slot, description and original source filename. One atlas with a partly opaque studio backdrop was corrected with the image generator; the manifest points to the corrected source. Originals remain in `/workspace/generated_images`. `python scripts/export_fitting_catalog.py` only crops, registers and resizes generated figures, exports 320×512 WebPs and measures fitting anchors. Use `--force-sheet N` to re-export a corrected sheet. Export rejects atlases without transparent source backgrounds. No runtime AI call or payment is required for these previews.

Existing prepared combination keys remain valid. Each single wearable has a whole render; combinations without an exact prepared render still use generated clothing/accessory layers registered to the chosen mannequin. This is catalog coverage, not a pre-render of every possible combination of 96 clothes.


## Farm, photo stage and collection packaging — 24 November 2026

`exec-897d420c-0bf9-4bf1-817a-65cb5d85ada8.png` supplies four crop sprites (strawberry, chili, pineapple, mango), fertilizer packaging/scoop and two growth states. `exec-71a8a6a3-fa65-47d0-a99f-41af5513b354.png` supplies the crimson curtain halves, podium and spotlight. `exec-458f58f4-c2b5-4087-be83-a8c313f6daa4.png` supplies eight generic closed gift packages for collection cards. Actual sex-toy illustration generation was rejected; these exports represent packaging, not depictions of the products, and the UI says so.

`scripts/export_remaining_art.py` crops/resizes these generated originals into `work_{strawberry,chili,pineapple,mango,fertilizer,fertilizer_scoop,farm_v3_seedling,farm_v3_young}.webp`, `stage_{left,right,podium,spotlight}.webp` and `collection_*.webp`. Source originals are preserved in `/workspace/generated_images`. Water splash, curtain opening and receipt animation are implemented in the UI.
