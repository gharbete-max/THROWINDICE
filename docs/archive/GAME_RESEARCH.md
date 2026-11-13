# What makes runner games addictive (research notes, 2026-11-03)

Sources are blogs, devlogs and developer guides, not controlled studies: treat the psychology claims as informed opinion.
Several searches (Subway Surfers / Jetpack Joyride coin layouts and pacing) found nothing specific, so those points are general runner practice.

## Findings and how the revamp uses them
| Finding | Source | In the game |
|---|---|---|
| Juice is non-functional feedback layered on the same rules; use it as seasoning, not noise | [Wayline: juice overload](https://www.wayline.io/blog/juice-overload-sensory-feedback-hurts-gameplay), [itch.io: juicy with simple effects](https://itch.io/blog/1059831/making-a-game-feel-juicy-with-simple-effects) | Effects are tiered (light / medium / heavy) and short; nothing changes the rules |
| Screen shake briefly (0.1-0.3 s), in tiers; stack a zoom punch with it | [Easton dev: flash, shake, floating text, sound, particles](https://eastondev.com/blog/en/posts/dev/20260521-game-feedback-feel/), [game juice checklist](https://gamejuice.pages.dev/articles/game-juice-checklist-30-techniques) | 3 shake tiers + a 4-6% camera zoom punch on checkpoints, hard landings, life loss, purple coins |
| Hit-stop: freeze 2 frames for light hits up to 8-10 for heavy | [game feel skill notes](https://skills.sh/gamedev-skills/awesome-gamedev-agent-skills/game-feel) | 2-3 frames on tier-3 coins and soft landings, 8 on losing a life |
| Combos: visible multiplier, reset on failure, reward every 5th step | [DEV: combo system devlog](https://dev.to/tanishpaul1106/the-combo-system-that-makes-neon-starfighter-addictive-a-devlog-42kf) | Coin chain (1.6 s window), multiplier x1-x5, bar, burst every 5 |
| Pitch rising with the combo; random pitch 5-15% on repeated sounds | [game feel guides](https://www.wayline.io/learn/game-feel/1), [Mega Cat juice guide](https://megacatstudios.com/blogs/game-development/mega-cat-developer-juice-guide-v1-0-08-23-17) | Coin pitch climbs with the chain; jump/land pitch varies +-7% |
| Near-misses feel better than easy wins or plain failure (blog claim, unverified) | [science of endless runners](https://tap-road-game.pages.dev/blog/science-of-endless-runners) | "PERFECT" for jumping right at an edge, "SOFT LANDING" for the saved fall, both pay bonus points |
| Coin that scales up as it is collected reads as satisfying | [game juice guides](https://gamejuice.pages.dev/articles/game-juice-checklist-30-techniques) | Coins pop and sparkle, floating +N text |
| Progressive speed is the main difficulty lever; telegraph obstacles, never unfair on first sight | [seanking11 endless runner module](https://seanking11.github.io/gamebootcamp/modules/04-endless-runner), [Gamasutra/gamedeveloper: procedural level generation](https://gamedeveloper.com/design/keep-running-procedural-level-generation-in-sure-footing) | Speed ramps per checkpoint; forecast cone telegraphs terrain; easy "breather" after each checkpoint |
| Chunk pool for variety + difficulty bands choosing which chunks appear | [SBGames paper](https://www.sbgames.org/sbgames2013/proceedings/comp/23-full-paper.pdf), [gamedeveloper](https://gamedeveloper.com/design/keep-running-procedural-level-generation-in-sure-footing) | Segment kinds are gated by distance; guide coins mark the right jump over every gap |
| Missions keep players beyond the core loop | [Jetpack Joyride review](https://www.trustedreviews.com/reviews/jetpack-joyride-iphone-game) | Three daily goals, completed ones pop up in the run and show on the game over card |

## Kept unchanged
Stock-chart theme, the cat, the music, 3 lives, double jump, coin tiers, auto-scroll and the forecast cone.
