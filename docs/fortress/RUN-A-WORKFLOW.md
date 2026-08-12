# How to run a draft n8n workflow without clicking the canvas

Three cards (tsl-2, tsl-2b, tsl-2c) burned their whole turn budget trying to
execute a draft workflow through the n8n UI. This file exists so that never
happens again.

## Do not

- Open the canvas and hunt for an "Execute Workflow" button by clicking around.
- Try to `POST /webhook-test/<path>` from a script. A test webhook is only
  registered by the browser tab that clicked "Listen for test event" — a
  script-issued POST 404s because nothing is listening.

## Do this instead

Run the draft headlessly with two `fetch` calls from any page already open on
the target n8n tenant (confirm the tab's host matches the instance you were
told to use before doing anything else):

```js
const H = {'content-type':'application/json','browser-id':localStorage.getItem('n8n-browserId')};
const ID = '<workflow id>';
const TRIG = 'A lead arrives';               // the trigger node name
const FIRST = '<name of the node right after the trigger>';
const PAYLOAD = { body: {...the lead...}, headers: {}, query: {} };   // webhook node output shape

const wf = (await fetch('/rest/workflows/'+ID,{headers:H}).then(r=>r.json())).data;
const rd = {};
rd[TRIG] = [{startTime:Date.now(),executionTime:0,source:[],executionStatus:'success',data:{main:[[{json:PAYLOAD}]]}}];
const res = await fetch('/rest/workflows/'+ID+'/run?partialExecutionVersion=2',{
  method:'POST',
  headers:H,
  body:JSON.stringify({
    workflowData:wf,
    runData:rd,
    startNodes:[{name:FIRST,sourceData:{previousNode:TRIG}}],
    triggerToStartFrom:{name:TRIG,data:rd[TRIG][0]}
  })
}).then(r=>r.json());
// res.data.executionId -> wait ~2s -> GET /rest/executions/<id>
```

This runs the saved draft version of the workflow. It does **not** activate
anything — `active` stays `false` throughout.

### Reading the execution result

`GET /rest/executions/<id>` returns a flatten-encoded body:
`e.data.data` is a JSON string of an array, and any string of digits
inside that array is an index pointing back into the array itself (n8n's
"flatted" format). Resolve it recursively, e.g.:

```js
function unflatten(arr) {
  function resolve(idx, seen) {
    if (seen.has(idx)) return undefined;
    seen.add(idx);
    const v = arr[idx];
    if (typeof v === 'string' && /^\d+$/.test(v) && Number(v) < arr.length) {
      return resolve(Number(v), seen);
    }
    if (Array.isArray(v)) {
      return v.map(x => (typeof x === 'string' && /^\d+$/.test(x) && Number(x) < arr.length)
        ? resolve(Number(x), new Set(seen)) : x);
    }
    if (v && typeof v === 'object') {
      const out = {};
      for (const k in v) {
        const val = v[k];
        out[k] = (typeof val === 'string' && /^\d+$/.test(val) && Number(val) < arr.length)
          ? resolve(Number(val), new Set(seen)) : val;
      }
      return out;
    }
    return v;
  }
  return resolve(0, new Set());
}

const full = unflatten(JSON.parse(executionRes.data.data));
const perNode = full.resultData.runData[nodeName][0].data.main[0]; // array of {json, pairedItem}
```

Then read whatever field you need off `perNode[0].json`.

## What running it always catches

Two defects only surface when you actually execute the workflow with
webhook-shaped sample data — reading the node definitions in the editor is
not enough:

1. **Rules reading the wrong path.** A real POST to a webhook node puts the
   payload one level down, under `$json.body`. A rules/condition node written
   against `$json.practice_area` (etc.) directly will read `undefined` for
   every real request and silently fail closed (score 0, every lead held).
   Fix: unwrap the payload once, immediately after the trigger, with a Set
   node that reads `($json.body || $json).<field>` for each field you need.
   Leave everything downstream reading plain top-level fields — one place
   does the unwrapping, nothing else has to know.

2. **Fields disappearing downstream.** n8n's Set node (`n8n-nodes-base.set`,
   typeVersion ≥ 3.3) drops every field not explicitly assigned unless you
   turn passthrough on. By default each Set node in a chain narrows the item
   to only the fields it just computed, so by the last node in the chain the
   original lead's name/email/etc. are gone (`undefined`, "unknown").
   Fix: set `includeOtherFields: true` on every Set node in the chain that
   needs to preserve upstream fields.
   **Note the parameter location changed with node version:** for
   `typeVersion` 3.3 and above, `includeOtherFields` is a **top-level**
   node parameter (`node.parameters.includeOtherFields`), not nested under
   `node.parameters.options.includeOtherFields` — nesting it under `options`
   silently does nothing (the workflow saves fine, but the field is never
   read at execution time). Verify by checking
   `GET /types/nodes.json` → the `n8n-nodes-base.set` entry → the
   `includeOtherFields` property's `displayOptions.hide['@version']` list.

---

## How a CHECK card verifies a run

`check-tsl-3` returned `VERDICT: FAIL` on work that was correct, because it went
looking for the runs in n8n's executions list and found it empty. **Do not verify a
behavioural claim by browsing the executions list.** Manual and partial executions do
not reliably appear there, and a checker that trusts that list will fail good work and
pass bad work with equal confidence.

A check card verifies a run the same way the build card produced it: **run it again
yourself** with the recipe above, and read `GET /rest/executions/<id>` directly. Two
independent runs agreeing on the output is the proof. An empty executions list is not
evidence of anything.

If the criteria name expected values, quote the actual values you got beside them.
