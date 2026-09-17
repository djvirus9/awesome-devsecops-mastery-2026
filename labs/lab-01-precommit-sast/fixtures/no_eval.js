// Static scanner fixture only: input is a constant, harmless expression.
// ruleid: no-eval-javascript
const dynamicallyComputed = eval("1 + 1");

// ok: no-eval-javascript
const directlyComputed = 1 + 1;
