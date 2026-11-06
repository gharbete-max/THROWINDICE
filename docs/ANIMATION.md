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

Press = jump as before. While the press is held, a drag of 40 px or more within 0.6 s is a flick, and a flick starts a trick (`trick(k)`). A flick on the ground jumps first. Only one trick runs at a time (`R.trk = {k, t, d, ok, land}`).

Every trick is a **rendered Blender sequence**, not a canvas transform or a fade. The body really rotates in 3D (the face turns away and comes back) and the limbs tuck or splay. The goo is a deformed mesh with rim ripples. **Frames 0 and 11 of every row are exactly the runner's `fall` frame 0**, so the game cuts from the run sheet into a trick and back with no fade and no pop.

| Flick (screen) | Key | `k` | Row | What the frames show | Playback |
|---|---|---|---|---|---|
| down-left (and left) | A / ← | `cork` | 0 | off-axis 360 (axis tilted 45° toward the run direction), knees tucked, arms hugging | 12 frames over 0.62 s |
| down-right (and right) | D / → | `spin` | 1 | flat 360 about the vertical, arms flung wide, legs together and pointed | 12 frames over 0.55 s |
| up (any up-diagonal) | E | `split` | 2 | turns to face the camera, opens a side split with arms in a V, pulses, closes | 12 frames over 0.6 s |
| straight down (within ~24°) | S / ↓ | `goo` | 3 | 0–3 melt into a pancake (tipped toward the camera so the face shows); 4–7 rippling pancake loop; 8–11 landing splat and spring back with overshoot | 0–3 in 0.22 s, 4–7 loop at 14 fps until landing, 8–11 over 0.3 s after landing |

- **Assets:** `assets/game/runner-trick{,-glass,-magnet,-x2,-rainbow}.webp`, one per power-up form. Each is 12 columns × 4 rows (cork, spin, split, goo), with a shared crop box. Drawn at the runner's pixel scale `217/182`, offset `TRICK_OFF` (crop origin minus `[118,209]`).
- **Game code:**
  - `TRK` (durations and labels), `TROW` (rows), `trickFrame(s)` (picks the cell), `flickDir`, `trick` are next to `wob()`.
  - In `player()`, `const tf=trickFrame(s)` zeroes the tilt (the frames carry the orientation), and the draw call uses the trick cell instead of the run frame.
  - Squash, wobble and power-up auras still stack on top.
  - The step block `if(R.trk)` advances, scores and drips. The landing branch starts the goo splat (`T.land`).
- **Scoring:** a trick finished in the air scores +3 and pops `NAME!`. Landing early lets it play out on the ground and scores nothing.
- **Double-jump flip:** starting a trick cancels it (`R.flip = 0`).
- **Reduced motion:** the frames still play (they are the state), but the goo loop holds one frame and there are no particles.
- **Self-check** (browser console, game open): `[[0,-80],[0,80],[-70,70],[70,70]].map(v=>_cp.flickDir(...v))` → `split,goo,cork,spin`. `_cp.trick('cork')` fires one directly.

### Re-rendering or adding a trick (recipe)

1. **Pose:** in `scripts/icons/objects.py`, add a branch to `o_trick(kind, i)`.
   - Build the pose in body space by lerping from `_rest_limbs()` with an envelope that is 0 at `u=0` and `u=1` (`sin(pi*u)` or `_ss`). That guarantees the seamless cut.
   - Put the whole-body rotation in `rot` (a quaternion, applied after the base yaw and lean).
   - Materials come from `runner_mats()`; the magnet from `head_magnet()`. Every skin works for free.
2. **Register:** add the name to the `('cork', 'spin', 'split', 'goo')` tuple in `OBJECTS`.
3. **Render all skins:** about 2 min per skin on 2 cores. Contact-sheet one skin at 8 samples first and check the frames.
   ```
   F=$(python3 -c "print(','.join(f'trick-{k}-{i}' for k in ('cork','spin','split','goo','new') for i in range(12)))")
   for sk in gold glass blue green rainbow; do RUNNER_SKIN=$sk python scripts/icons/objects.py $F out/$sk 256 32 1; done
   ```
   - Skin → file: `gold` → `runner-trick`, `glass` → `-glass` (shield), `blue` → `-magnet`, `green` → `-x2`, `rainbow` → `-rainbow` (combo).
4. **Pack:** one row per trick, 12 columns, a union crop box over all skins and frames with 2 px padding. Write `TRICK_OFF=[x0-118, y0-209]` into `index.html`.
   - Keep everything inside the 256 px render. Check the alpha bbox: a frame touching 0 or 256 is clipped, so make the pose smaller rather than moving the camera, because the pixel scale must match the runner.
5. **Game:** add `{d, n}` to `TRK`, the row to `TROW`, and a direction or key in `flickDir` and the keydown map. If it isn't a straight play-through, give it a branch in `trickFrame` (see goo: in, loop, out).
6. **Rules:** no canvas fakery (no scaleX flips, no cross-fades between poses). Motion lives in the frames, and loops must close (frame n+1 ≡ frame 0).

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
