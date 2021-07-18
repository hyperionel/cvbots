# Movement/autolooting bot using computer vision

This was a pet project that was born out of curiosity on how computer vision would work to shape the next generation of bots.

## What it can do

- It tracks the "fog of war" and clicks to move the character toward the unexplored part of the map.
- It prioritizes the detection and pickup of loot over movement (detections run in sepparate threads).
- It handles "getting stuck" based on a movement history & retry attempt
- It can reset after the map is complete (port back to town and reset/re-enter the map)

This was only meant as a proof of concept therefore was not made to be user-friendly (or very optimized from a performance standpoint)

Only works with a very automated summoner build (e.g. summon everything and just let it walk around the map while your minions kill stuff)
