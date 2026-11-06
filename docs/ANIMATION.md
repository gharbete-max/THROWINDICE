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

## Transition rules (priority)

When states fight over a channel, higher wins:

1. Dead / dance
2. Checkpoint love flight (face, sheet)
3. Take-off / landing squash (scale)
4. Power-up form (skin, tint): orthogonal to 2 and 3. The love sheet exists per skin (`runner-love-<skin>.webp`), so the form persists through the flight.
5. Gait (sheet row)

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
