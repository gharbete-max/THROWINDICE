# Runner game: animation plan

Integration notes for Claude Code: how every animation in the Live Ball Bounce game should blend in and out, and loop without seams. Everything here lives in `index.html` (game closure, state `R`) and the sheets in `assets/game/`.

## Principles

1. **Time comes from state, not frames.** Every loop is a function of a clock (`R.t`, `R.cpT`, distance `R.sx`), never a frame counter. That gives the same speed at 60 Hz and 120 Hz, and a clean restart when a clock resets to 0.
2. **Blend, don't switch.** When one state replaces another, ease a 0..1 weight over 120–250 ms instead of swapping on one frame. Use `k += (target - k) * (1 - Math.exp(-dt * rate))`. This is frame-rate independent.
3. **Seamless loops.** A loop is a periodic function (sin, cos, or `Math.pow(Math.max(0, sin), n)` for beats), or a sprite cycle whose last frame leads into its first. No tweens that end and jump back.
4. **One owner per channel.** Scale (squash/stretch/wobble), rotation (flip/lean), tint/form, face and particles are separate channels. Each state writes only its own channel, so states stack instead of fighting.
5. **Reduced motion** (`RMQ.matches`): keep every state change, but drop pops, beats, wobble, particles and hops. The final pose shows immediately.

## State map

| State | Trigger | Visual | Loop / clock | In | Out |
|---|---|---|---|---|---|
| Walk → jog → run | level (`R.lvl`) | gait sheet row | frames driven by distance `R.sx` (stride length per gait) | cross-fade the row over 200 ms at a level change | same |
| Take-off | jump press | `tko` frame + squash | one-shot 90 ms | instant (anticipation squash 60 ms) | into rise |
| Rise / fall | `R.air`, sign of `vy` | rise/fall frames, leg flail | flail = `sin(R.t*14)` | switch at the apex, weight blended over 100 ms by `vy` near 0 | landing |
| Landing | ground contact | squash `R.sq`, bounce `R.bnc` | damped spring | instant | spring decays to 0 |
| Flip | power-up pickup | rotation channel `R.flip` | one-shot 360° ease-out | instant | ends at exactly 0 rad (snap so there's no drift) |
| Jelly wobble | landing / pickup / proximity | `wob(a,f)` → `wbA` decays | `wbA*sin(wbT*wbF)` | additive | exponential decay |
| Shield / magnet / 2x form | `R.shield`, `R.magT`, `R.x2T` | skin sheet swap + glow | glow pulse `sin(R.t*4)` | **todo:** cross-fade old→new skin over 250 ms (draw both with globalAlpha) | same, plus a blink at the last 1.5 s of the timer |
| Combo | two or more forms at once | rainbow skin + hue-rotate | hue = `R.t*120 deg` mod 360 | as above | as above |
| Checkpoint love flight | `R.cpFly` | love sheet, heart eyes, pink aura, floating hearts | `R.cpT`; `heartBeat()` lub-dub at 7.5 rad/s | heart pop: `1-e^(-9t)cos(18t)` overshoot | land: heart burst plus wobble; **todo:** shrink the hearts back into the head over 150 ms |
| Coin near | within 320 px ahead | scale up, faster spin, lean, glow | spin is part of the coin's own `t` | proximity weight `1 - d/320` (continuous, no jump) | same |
| Power-up near | within 420 px | +18% size, faster spin, glow, runner wiggle once | `p.nr` latches the wiggle | proximity weight | same |
| Briefcase near | within 1100 px | hop `abs(sin(t*7))*55*w`, +8% size, glow | sine | proximity weight | same |
| Pickups | collision | coin sparkles (6 fx), power-up flip and wobble | fx particles with gravity `g`, life `l` | instant | life fade |
| Game-over dance | `R.dead` | dance sheet on the results card | sheet loop, sway `sin` | **todo:** fade the card in 200 ms, start the dance on frame 0 | — |

## Flick tricks (real 3D frames)

Swipes snap to 4 directions, and each also sets the market position (long/short/cash/all in). See `MARKET.md` §1.

Press = jump as before. While the press is held, a drag of 40 px or more within 0.6 s is a flick, and a flick starts a trick (`trick(k)`). A flick on the ground jumps first. Only one trick runs at a time (`R.trk = {k, t, d, ok, land}`).

Every trick is a **rendered Blender sequence**, not a canvas transform or a fade. The body really rotates in 3D (the face turns away and comes back) and the limbs tuck or splay. The goo is a deformed mesh with rim ripples. **Frames 0 and 23 of every row are exactly the runner's `fall` frame 0**, so the game cuts from the run sheet into a trick and back with no fade and no pop.

| Flick (screen) | Key | `k` | Row | What the frames show | Playback |
|---|---|---|---|---|---|
| ← left | A / ← | `cork` | 0 | off-axis 360 (axis tilted 45° toward the run direction), knees tucked, arms hugging | 24 frames over 0.62 s |
| → right | D / → | `spin` | 1 | flat 360 about the vertical, arms flung wide, legs together and pointed | 24 frames over 0.55 s |
| ↑ up | E | `split` | 2 | turns to face the camera, opens a side split with arms in a V, pulses, closes | 24 frames over 0.6 s |
| ↓ down | S / ↓ | `goo` | 3 | 0–7 melt into a pancake (tipped toward the camera so the face shows); 8–15 rippling pancake loop; 16–23 landing splat and spring back with overshoot | 0–7 in 0.22 s, 8–15 loop at 28 fps until landing, 16–23 over 0.3 s after landing |

- **Assets:** `assets/game/runner-trick{,-glass,-magnet,-x2,-rainbow}.webp`, one per power-up form. Each is 24 columns × 4 rows (cork, spin, split, goo), with a shared crop box. Drawn at the runner's pixel scale `217/182`, offset `TRICK_OFF` (crop origin minus `[118,209]`).
- **Game code:**
  - `TRK` (durations and labels), `TROW` (rows), `trickFrame(s)` (picks the cell), `flickDir`, `trick` are next to `wob()`.
  - In `player()`, `const tf=trickFrame(s)` zeroes the tilt (the frames carry the orientation), and the draw call uses the trick cell instead of the run frame.
  - Squash, wobble and power-up auras still stack on top.
  - The step block `if(R.trk)` advances, scores and drips. The landing branch starts the goo splat (`T.land`).
- **Scoring:** a trick finished in the air scores +3 and pops `NAME!`. Landing early lets it play out on the ground and scores nothing.
- **Double-jump flip:** starting a trick cancels it (`R.flip = 0`).
- **Reduced motion:** the frames still play (they are the state), but the goo loop holds one frame and there are no particles.
- **Self-check** (browser console, game open): `[[0,-80],[0,80],[-80,10],[80,10]].map(v=>_cp.flickDir(...v))` → `split,goo,cork,spin`. `_cp.trick('cork')` fires one directly.

### Re-rendering or adding a trick (recipe)

1. **Pose:** in `scripts/icons/objects.py`, add a branch to `o_trick(kind, i)`.
   - Build the pose in body space by lerping from `_rest_limbs()` with an envelope that is 0 at `u=0` and `u=1` (`sin(pi*u)` or `_ss`). That guarantees the seamless cut.
   - Put the whole-body rotation in `rot` (a quaternion, applied after the base yaw and lean).
   - Materials come from `runner_mats()`; the magnet from `head_magnet()`. Every skin works for free.
2. **Register:** add the name to the `('cork', 'spin', 'split', 'goo')` tuple in `OBJECTS`.
3. **Render all skins:** about 2 min per skin on 2 cores. Contact-sheet one skin at 8 samples first and check the frames.
   ```
   F=$(python3 -c "print(','.join(f'trick-{k}-{i}' for k in ('cork','spin','split','goo','new') for i in range(24)))")
   for sk in gold glass blue green rainbow; do RUNNER_SKIN=$sk python scripts/icons/objects.py $F out/$sk 256 32 1; done
   ```
   - Skin → file: `gold` → `runner-trick`, `glass` → `-glass` (shield), `blue` → `-magnet`, `green` → `-x2`, `rainbow` → `-rainbow` (combo).
4. **Pack:** one row per trick, 12 columns, a union crop box over all skins and frames with 2 px padding. Write `TRICK_OFF=[x0-118, y0-209]` into `index.html`.
   - Keep everything inside the 256 px render. Check the alpha bbox: a frame touching 0 or 256 is clipped, so make the pose smaller rather than moving the camera, because the pixel scale must match the runner.
5. **Game:** add `{d, n}` to `TRK`, the row to `TROW`, and a direction or key in `flickDir` and the keydown map. If it isn't a straight play-through, give it a branch in `trickFrame` (see goo: in, loop, out).
6. **Rules:** no canvas fakery (no scaleX flips, no cross-fades between poses). Motion lives in the frames, and loops must close (frame n+1 ≡ frame 0).

## Trick combos: plan (built; rendered bridges skipped)

Goal: flicking several times in one jump chains tricks together. The same direction twice continues and speeds up the current trick (double cork, 720 spin). Back and forth reverses it or combines two tricks into one move (a cork that flows into a spin). Every chain still lands cleanly. Build in the phases below; each phase is shippable on its own.

### 1. Input: a gesture stream instead of one flick

- After a flick, don't clear `fl`. **Re-anchor** it at the current pointer position and time, so the same press can produce more flicks. Each further 40 px segment is a new flick.
- A **reversal** (angle change > 120° from the previous flick) counts as back-and-forth. A same-direction repeat (< 45°) counts as "again".
- **Buffer:** flicks during a running trick go into `R.chain.q` (max 2). Older inputs drop off the end, so mashing never piles up.
- **Keyboard:** the same key again = "again"; the opposite key (←/→) = reversal.
- Self-check: extend the `flickDir` console check with a recorded sequence (down-left, down-left, down-right) → `cork, again, reverse`.

### 2. Model: segments on a pose graph

Every trick is cut into **segments** that join at named key poses. Chaining is always legal because segments only ever connect at a shared pose.

```
poses:    REST (runner fall 0) · TUCK · WIDE (arms out, legs together) · SPLIT · PANCAKE
cork:     cork-in   REST→TUCK  (rotation 0→90°, 3 fr)   cork-loop  TUCK, 360° (12 fr, seamless)   cork-out  TUCK→REST (270→360°, 3 fr)
spin:     spin-in   REST→WIDE  (3)                      spin-loop  WIDE, 360° (12)                spin-out  WIDE→REST (3)
split:    split-in  REST→SPLIT (4)                      split-hold SPLIT pulse loop (8)           split-out SPLIT→REST (4)
goo:      goo-in    REST→PANCAKE (4, as now)            goo-loop   ripple (4)                     goo-land  splat + spring (4, as now)
bridges:  cork→spin TUCK→WIDE while the axis tilts upright (6) · spin→split WIDE→SPLIT ("star spin", 6)
          split→goo SPLIT→PANCAKE ("splat split", 6) · goo→split PANCAKE→SPLIT ("pop", 6)
```

- **A single trick is unchanged:** in + loop frames 3–9 + out = 12 frames, the same timing as today.
- **Loop entry and exit phases:** loops are entered at the 90° phase (frame 3) and exited at the 270° phase (frame 9), so in/out rotations line up.
- **Bridges start at the loop's identity phase** (frame 0, facing the camera). A switch waits for the loop to reach frame 0, and the wait is shortened by the acceleration below.
- **State:** `R.chain = {seg, f (float frame), rate, q:[], n, names:[]}` replaces `R.trk`. `trickFrame()` becomes a lookup of `SEG[seg].row`, `floor(f)`.

### 3. Continuation and acceleration (same direction again)

- **"Again" during a loop:** add one more loop pass (cork → double cork → triple) and `boost += 0.6`.
  - Playback `f += dt * 20 * rate`, where `rate = 1 + boost` and `boost *= exp(-3 * dt)`, capped at `rate ≤ 2.6`.
  - The trick visibly winds up, then settles.
- **"Again" on split:** extends the hold by one pulse loop, and the pulse amplitude grows. On goo it slams: gravity ×1.8 until landing, with a bigger splat.
- **Reverse on spin:** play `spin-loop` backwards. A reversed yaw sequence is a true opposite spin, so no new frames are needed. `rate` goes through 0 with a 120 ms ease, so the spin brakes and then turns back the other way ("rewind").
- **Reverse on cork:** a cork's axis is tilted, so reversed frames would look wrong. Instead it bridges into the spin (`cork→spin`) and reverses there: the "twister".
- **Back and forth repeatedly:** alternates the bridge pairs (spin ⇄ split, split ⇄ goo) as long as there's air time.

### 4. Combined movement (physics coupling)

Tricks nudge the arc slightly, so combos feel physical:

| Trick | Effect on the arc |
|---|---|
| spin loop | gravity ×0.85 (hang time) |
| split hold | ×0.7 (float) |
| goo | ×1.6 (drop); goo "again" slams |
| cork "again" | one extra hop `vy -= 140`, once per jump |
| reversal | a small sideways squash pulse |

- **Air budget:** at most +0.35 s of extra hang time per jump in total, so chains can't make the runner fly forever.

### 5. Land-aware time warp (no snaps)

- Every step, estimate time to ground `tg` from `y`, `vy` and the current gravity.
- Remaining frames = the current segment, plus queued passes, plus the out segment. If they won't finish before landing, **raise `rate`** so the out segment ends exactly at touchdown, and drop queued extras that can't fit.
- If even `rate = 2.6` can't make it, cut to the nearest out/bridge entry at the next phase point, then warp.
- The runner never lands mid-rotation, and nothing pops back to the run sheet.

### 6. Scoring and feedback

- Chain count `n` per jump. Points `3·n·n` (1 → 3, 2 → 12, 3 → 27), paid on a clean landing. A goo slam always lands clean.
- **Names, built from the segments:** DOUBLE CORK, 720, TWISTER (cork→spin), STAR SPIN (spin→split), SPLAT SPLIT, POP. Shown as one growing label above the runner that updates with each link instead of stacking pops.
- The chain counter pulses with a growing pitch (`sfx` rate `1 + 0.12n`) and `vib(6+4n)`.

### 7. Assets and rendering

- **In `o_trick(kind, i)`:** add `kind` values for each segment (`cork-in`, `cork-loop`, …, `bridge-cork-spin`, …). Loops use the held pose with `env = 1` and `u` covering exactly one period with the endpoint excluded (`u = i/n`, not `i/(n-1)`), so frame n ≡ frame 0.
- **Sheet:** 12 columns × about 13 rows per skin. Short segments share a row (in | out | bridge). This is roughly 100 frames per skin, about 4 min of rendering per skin on this box.
- **Size:** about 0.6 MB per skin. Load the gold sheet with the game, and lazy-load the other four the first time that power-up is picked up (prefetch while the shield/magnet/2x is on screen).
- **Continuity check script** (keep it in `scripts/icons/`): for every pair of segments that join, the mean absolute RGBA difference between the last frame of A and the first of B (and loop frame n−1 → 0) must be below a threshold. This catches pose mismatches before they ship.

### Stage 1: what's built (Nov 2026)

- **Input** (`#gameLayer` listeners):
  - The anchor follows a stroke while it keeps going the same way (dot > 0.5). A turn of 40 px or more, or a new press-and-swipe, is the next flick. A stroke slower than 0.6 s re-anchors.
  - A press while a trick is in the air waits: a release within 250 ms with no flick is the double jump. It calls `tap()` and skips `release()`'s short-hop cut via `stopImmediatePropagation`.
- **`trick(k)`:** starts a trick, or queues it into `R.cq` (max 2).
  - Each queued flick adds `boost` to the current trick: +0.6 for the same trick, +0.3 otherwise. `rate = min(2.6, 1 + boost)`, and boost decays as `exp(-3·dt)`.
  - Goo ends a chain; goo again sets `R.slam` (gravity ×1.8 until landing).
- **Hand-off:** when the current trick reaches its last frame (the shared rest pose), the next queued trick starts with half the boost. This chains through REST, which is seamless because every row starts and ends there.
- **Land-aware warp:** in the step's `if(R.trk)` block, time to ground is estimated from `gy`, `vy` and the current gravity.
  - Queued tricks that can't fit even at 2.6× are dropped.
  - Otherwise the rate is raised so the chain ends at touchdown.
- **Scoring:**
  - `R.cn` and `R.cnames` count tricks completed in the air. The live label `R.clbl` above the runner grows and punches on each link.
  - On landing the chain pays `3·n²` if clean (no trick mid-rotation; a goo landing is always clean), with the name from `chainName()`: DOUBLE/TRIPLE, spin degrees, CORKSPIN + SPIN → TWISTER, otherwise joined with `+`. A landing that isn't clean pays nothing.
- **Stage 3 (Nov 14):** combo names only: SPLIT then PANCAKE = SPLAT SPLIT (`chainName`). Rendered bridges are skipped (decision): the only reachable pair is split → goo, which already chains cleanly through REST, and the bridge frames would not change play.

### Stages 2 and 4: what's built (Nov 14 2026)

- **Double / triple cork:** `o_trick('corkloop', i)` renders 16 frames (`CORK_LOOP_N`) of cork frame 11's held pose turning one more 360 at the cork's mid speed (22.5° a frame). They are row 4 of every `runner-trick*.webp` (sheets are now 5 rows; `th = naturalHeight/5`), HEADS.trick 96-111. Crop box for trick cells: `(30, 32, 215, 216)` of the 256 px render.
- **Runtime:** `LP = {cork: [11, 96, 16], split: [15, 56, 8]}` = [after trick frame, first sheet frame, frames]. The same flick again before that frame (or during a loop) adds a pass (`T.ex`, max 2); the trick holds at that frame, plays the loop (`T.lp`, `T.lt`), and resumes half a frame later, so no pose repeats. Each pass counts as a chain link (DOUBLE / TRIPLE CORKSPIN, DOUBLE SPLIT); the land-aware warp counts and drops passes like queued tricks. A longer split replays its hold frames 8-15 (the pulse is near zero at both ends).
- **Spin rewind / 720:** not built: → is ALL IN (the skateboard), so the ball spin is not reachable in play.
- **Physics (stage 4):** `trkG()`: spin x.85, split x.7 gravity, at most +.35 s extra hang a jump (`R.hang`); cork again = one hop (`vy -= 140`, `R.hop`). Goo x1.6 was left out (a short swipe over a gap would drop you in). Sheets already load per skin on demand (`ldSkin`). Not done: the continuity script and the 30/120 fps checks.

### 8. Build order

1. ✅ **Input stream, queue, acceleration and chaining through REST, with today's sheets** (every trick already starts and ends at REST, so any chain works via its out segment), plus the land-aware warp and `n·n` scoring. *No renders.*
2. ✅ **Loop segments:** double/triple cork (rendered), split extension (replayed hold). Spin rewind/720 dropped (spin is not reachable).
3. ✅ (names only) **Combo names**; rendered bridges skipped, see Stage 3 above.
4. ✅ (mostly) **Physics coupling, lazy loading of the skin sheets**; the continuity script and checks at 30/120 fps are open.

## Blending under spam (built)

Players swipe and jump constantly, so every switch in `player()` must blend. The rules:

1. **Sheet or move change → 0.11 s fade.**
   - Every draw branch sets `D` (drawImage args) and a family key `fam`: `run<skin><cash>`, `tr<skin>`, `love<skin>`, or `sk<ride|ollie|kick|trick>`.
   - When `fam` changes, the previous frame (`s.lastD`) is drawn on top at alpha `fadeT/0.11` while it fades out (`R.fadeT`, ticked in step). This covers skin/position changes, trick in and out, board on and off, ollie → kickflip, and the bull flight.
   - The hat anchor interpolates from the old frame's anchor (`s.fadeH`), so hats never jump.
   - Normal gait frames inside one family don't fade; they're already continuous.
2. **Tilt is eased; spins are not.**
   - `rot` (arc tilt, slope lean, the zeroing for tricks/board) eases toward its target with `1 − e^(−16·dt)` into `s.rs`.
   - Full-turn spins (double-jump flip, power-up and checkpoint reaction spins) go in `spin` and are added after easing, so they never unwind.
3. **Flips are never cut:**
   - A trick swiped during a double-jump flip is held in `R.pend`, while the flip runs 3× faster, then the trick starts.
   - A double jump during a trick doesn't start a flip.
   - The bull launch lets a running flip finish.
4. **Queues reset on landing** (`R.cq`, `R.pend`), so stale inputs never fire on the next jump.
5. **Position changes add a small jelly wobble** (`wob(.09,15)`) as a cue alongside the colour fade.
6. **Reduced motion:** no fades and no easing; instant states.
7. **Stress check** (headless, no errors expected): fire `_cp.tap()` / `_cp.trick(random)` every 60–150 ms for 10 s, and record `__R.rs` each animation frame. The largest per-frame change should stay under about 0.12 rad at 30 fps (before blending it reached 0.35 rad).
8. **New animations must join this system:** set `D` + `fam` (+ `hd`), and never call `drawImage` for the body directly.

## Transition rules (priority)

When states fight over a channel, higher wins:

1. Dead / dance
2. Checkpoint love flight (face, sheet)
3. Flick trick (owns the sprite and its orientation; squash, wobble and auras still add on top)
4. Take-off / landing squash (scale)
5. Power-up form (skin, tint): orthogonal to 2 and 3. The love sheet exists per skin (`runner-love-<skin>.webp`), so the form persists through the flight.
6. Gait (sheet row)

Additive channels (wobble, proximity glow, particles) never get priority. They sum, then clamp: scale ±35%, glow alpha ≤ 0.6.

## Loop checklist (per animation)

- Period is set by a clock, and the function at t = period equals t = 0.
- Sprite cycles: the last frame leads into the first. Gait frames are indexed by `floor(distance / stride) % n`, so feet don't skate.
- Beats use `pow(max(0, sin), 8)` pairs (lub-dub), so the rest phase is flat and the loop has no visible seam.
- Clocks that drive one-shots (`cpT`, flip) reset to 0 on trigger, and their effect at t = 0 equals the non-animated pose.

## To do

- [ ] Skin cross-fade on a power-up gain or loss (250 ms, both sheets drawn with globalAlpha).
- [ ] Expiry warning: the form blinks or flickers in the last 1.5 s of a power-up timer.
- [ ] Heart eyes retract on landing (reverse pop, 150 ms) instead of disappearing.
- [ ] Gait cross-fade at a level change (currently a hard switch of the row).
- [ ] Results card fade-in and dance start sync.
- [ ] Optional: a shared `ease(k, target, rate, dt)` helper once there are three or more blended weights. Inline until then.
- [ ] Test at 30, 60 and 120 fps (throttle `dt`) to confirm that no loop depends on the frame rate.

## Frame rate and frame counts (60 fps pass)

The game runs at the display rate (60 fps on phones); sprite loops are timed in seconds, so more frames means smoother motion, not faster motion.

| Sheet | Frames | Playback |
|---|---|---|
| `runner*.webp`, `runner-cash.webp` | 105: walk/jog/run 24 each, take-off 9, rise 12, fall 12 (2 rows of 53) | gaits by distance (30–75 fps), rise 36 fps, fall 45 fps |
| `runner-trick*.webp` | 24 per trick (24 × 4 grid, `TRICK_N` in objects.py) | stretched over the trick duration |
| `dance.webp` (menu) | 54 | 60 fps (0.9 s loop), CSS `steps(54)` on a transform layer |
| `runner-skate-{ggreen,gred}.webp` | ride 5 slopes × 12, ollie 12, kickflip 16, shove-it/tre/indy/jesus 20 (168, 10 columns) | ride loop 18 fps; tricks stretched over their duration |
| `cp-bull.webp`, `cp-bear.webp` | 96 | 24 fps (one turn every 4 s) |

- **No main-thread decode:** `ok(im)` only reports a sheet ready once an `ImageBitmap` built from the fetched blob exists (`bmMake`; decode happens off the main thread). `cx.drawImage` is patched to draw `im._bm`. Bitmaps are evicted LRU past `BM_BUDGET` (110 MB). New sheets need no extra code: `GIMG`/`ld` do it.
- **Cached effects:** glows (`glowSprite`) and auras (`AURAC`) are pre-rendered sprites, not per-frame gradients. Keep new effects as cached sprites.
- **Theme palette:** `pal()` (cached in `PALC` per theme and size) holds the background wash, candle and line colours for light and dark. Canvas colours come from `P_`, never hard-coded, so the scene follows the site's glass theme.
- **Bigger sheets:** a 60 fps target does not mean 60 unique frames per second of animation; keep each skin under ~30 MB decoded (phones).
