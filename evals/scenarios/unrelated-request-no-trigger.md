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
None.

## Expected (all must hold)
- No stablehand skill is loaded.
- The reply contains the corrected index `arr.length - 1`.

## Must not
- Load any stablehand skill or delegate to a stablehand agent.

## Checks
- deterministic:
  - zero skill loads whose name matches a stablehand skill (scored in both arms);
  - regex `arr\.length\s*-\s*1` in the final message.
