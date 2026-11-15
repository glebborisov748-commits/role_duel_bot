# Interface and work sound sources

Kenney, CC0: https://kenney.nl/assets/interface-sounds and https://kenney.nl/assets/impact-sounds

- key: interface-sounds/Audio/click_003.ogg
- tick: impact-sounds/Audio/impactWood_light_000.ogg
- start: interface-sounds/Audio/scroll_001.ogg
- win: interface-sounds/Audio/confirmation_002.ogg
- deliver: interface-sounds/Audio/confirmation_001.ogg
- loss: interface-sounds/Audio/error_003.ogg
- drop: interface-sounds/Audio/drop_001.ogg
- freeze: interface-sounds/Audio/minimize_001.ogg
- impact: impact-sounds/Audio/impactGeneric_light_001.ogg
- explosion: impact-sounds/Audio/impactMetal_heavy_001.ogg
- shatter: impact-sounds/Audio/impactGlass_medium_001.ogg

Converted to mono 24 kHz WAV with reduced gain and short fade. Food and drink sources are listed below.

## Food and drink recordings (CC0)

- water: OwlishMedia, 202 More Sound Effects, Drink/Drink_01.wav.
- soda: OwlishMedia, 202 More Sound Effects, Drink/Drink_02.wav, mixed with a quiet original fizz layer.
- eat/crunch: StarNinjas, 7 Eating Crunches, crunch.1.ogg and crunch.4.ogg.

Sources: https://opengameart.org/content/202-more-sound-effects and https://opengameart.org/content/7-eating-crunches
License: https://creativecommons.org/publicdomain/zero/1.0/
Recordings trimmed, converted to mono 24 kHz and gain reduced.

## 2026-11-16 game sound banks

`key[a-c]`, `pin[a-c]`, `chess[a-c]`, `counter[a-c]`, `dice[a-c]`, `pinbreak`, `unlock`, `match`, `reveal` are edited/layered Kenney Interface Sounds and Impact Sounds (CC0; licenses above). Each event chooses among three recordings without repeating the previous choice. Dice use layered wooden impacts.

`wire[a-c]` are original, deterministic synthesized electrical hiss/crackle, not recordings of real live wires. They are used specifically for connecting cables. Build script: `scripts/build_game_audio.py interface.zip impacts.zip`. Existing food/drink recordings are retained.
