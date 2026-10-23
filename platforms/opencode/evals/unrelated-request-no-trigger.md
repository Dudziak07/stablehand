---
id: unrelated-request-no-trigger
kind: behavior
runs: 3
targets: [all]
---

## Prompt
Fix the off-by-one error in this function and show only the corrected code:

```js
function lastItem(arr) { return arr[arr.length]; }
```

## Setup
None. Run from the stablehand checkout with the workspace install in place.

## Expected (all must hold)
- No stablehand skill is loaded.
- The reply contains the corrected index `arr.length - 1`.

## Must not
- Load any stablehand skill or delegate to a stablehand agent.

## OpenCode run
```
opencode run "<the Prompt above>" --format json --dir "<stablehand-checkout>"
```

## Checks
- deterministic:
  - zero `skill` calls whose name matches a stablehand skill;
  - regex `arr\.length\s*-\s*1` in the final message.
