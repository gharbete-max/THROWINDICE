// Single point where the app decides what data to render.
//
// Today this is always the mock dataset. Once scripts/build-data (Part 8)
// is wired into the build, swap this for the generated JSON:
//
//   import generated from "./generated.json";
//   export const store = buildStore(generated as SourceRoot);
//
// The generated JSON is produced to the exact SourceRoot shape (src/data/types.ts),
// so this is the only file that needs to change.
import { buildStore } from "../lib/build";
import { MOCK_DATA } from "./mock";

export const store = buildStore(MOCK_DATA);
export type { Store } from "./built";
export type { BuiltInstrument, BuiltFamily } from "./built";
