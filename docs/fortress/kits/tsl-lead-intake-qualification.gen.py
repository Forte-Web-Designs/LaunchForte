#!/usr/bin/env python3
"""
tsl-lead-intake-qualification.gen.py — SIM TSL: Lead Intake and Qualification

One-off generator, not part of kitgen's shape library. Builds the exact
workflow the card asked for: trigger with (name, email, phone, practice area,
city, message) -> a qualification step whose rules live in Set nodes, not in
a Code node -> branch on qualified/held -> two vendor stubs (NoOp), neither
connected to anything real.

Import into n8n: new workflow -> select the canvas -> paste the JSON (Cmd+V).
Leave inactive. Rename if the paste doesn't carry the workflow name.
"""

import json, os

def _id(n):
    return f"tsl0{n:03d}-0000-4000-8000-{n:012d}"

nodes = []
conns = {}
n = 0

def add(name, ntype, x, y, params=None, tv=1, extra=None):
    global n
    n += 1
    node = {
        "parameters": params or {},
        "id": _id(n),
        "name": name,
        "type": f"n8n-nodes-base.{ntype}",
        "typeVersion": tv,
        "position": [x, y],
    }
    if extra:
        node.update(extra)
    nodes.append(node)
    return name

def link(src, dst, out=0):
    conns.setdefault(src, {"main": []})
    while len(conns[src]["main"]) <= out:
        conns[src]["main"].append([])
    conns[src]["main"][out].append({"node": dst, "type": "main", "index": 0})

def assign(id_seed, name, value, atype="boolean"):
    return {"id": _id(id_seed), "name": name, "value": value, "type": atype}

PRACTICE_AREAS = [
    "personal injury", "family", "criminal defence", "estate planning",
    "hvac", "roofing", "plumbing", "electrical", "pest control",
]
areas_js = json.dumps(PRACTICE_AREAS)

y = 300
x = 0

trig = add(
    "A lead arrives", "webhook", x, y,
    {"httpMethod": "POST", "path": "sim-tsl-lead-intake", "options": {}},
    tv=2, extra={"webhookId": _id(900)},
)

# --- qualification step 1: the three rules, computed straight off the raw lead ---
x += 260
rules = add(
    "Test the rules: area, contact, message length", "set", x, y,
    {
        "mode": "manual",
        "assignments": {
            "assignments": [
                assign(101, "practice_area_served",
                       "={{ " + areas_js + ".includes((($json.practice_area || '').toString().toLowerCase().trim())) }}"),
                assign(102, "has_usable_contact",
                       "={{ (!!$json.email && /\\S+@\\S+\\.\\S+/.test($json.email)) || (!!$json.phone && $json.phone.toString().replace(/\\D/g, '').length >= 7) }}"),
                assign(103, "message_is_substantive",
                       "={{ (($json.message || '').toString().trim().split(/\\s+/).filter(w => w.length > 0).length) > 5 }}"),
            ],
        },
        "options": {},
    },
    tv=3.4,
)
link(trig, rules)

# --- qualification step 2: total the rules into a score + a human-readable hold reason ---
x += 260
score = add(
    "Score the lead and write the reason", "set", x, y,
    {
        "mode": "manual",
        "assignments": {
            "assignments": [
                assign(201, "score",
                       "={{ ($json.practice_area_served ? 1 : 0) + ($json.has_usable_contact ? 1 : 0) + ($json.message_is_substantive ? 1 : 0) }}",
                       atype="number"),
                assign(202, "qualified",
                       "={{ $json.practice_area_served && $json.has_usable_contact && $json.message_is_substantive }}"),
                assign(203, "hold_reason",
                       "={{ [ !$json.practice_area_served ? ('practice area (' + ($json.practice_area || 'none given') + ') is not one we serve') : null, !$json.has_usable_contact ? 'no usable email or phone was provided' : null, !$json.message_is_substantive ? 'the message is too short to act on' : null ].filter(Boolean).join('; ') }}",
                       atype="string"),
            ],
        },
        "options": {},
    },
    tv=3.4,
)
link(rules, score)

# --- branch ---
x += 260
branch = add(
    "Qualified or held?", "if", x, y,
    {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [{
                "id": _id(500),
                "leftValue": "={{ $json.qualified }}",
                "rightValue": "",
                "operator": {"type": "boolean", "operation": "true", "singleValue": True},
            }],
            "combinator": "and",
        },
        "options": {},
    },
    tv=2.2,
)
link(score, branch)

# --- qualified path: prep record (score + reason) -> CRM stub ---
x += 260
q_prep = add(
    "Prepare the CRM record (score + reason)", "set", x, y - 130,
    {
        "mode": "manual",
        "assignments": {
            "assignments": [
                assign(301, "crm_score", "={{ $json.score }}", atype="number"),
                assign(302, "crm_reason",
                       "={{ 'Serves ' + $json.practice_area + '; reachable at ' + ($json.email || $json.phone) + '; message gives enough to act on.' }}",
                       atype="string"),
            ],
        },
        "options": {},
    },
    tv=3.4,
)
link(branch, q_prep, 0)

x += 260
q_stub = add(
    "Stub: send to GoHighLevel CRM (not connected)", "noOp", x, y - 130,
)
link(q_prep, q_stub)

# --- held path: prep record (readable reason) -> hold stub ---
h_prep = add(
    "Prepare the hold record (reason)", "set", x - 260, y + 130,
    {
        "mode": "manual",
        "assignments": {
            "assignments": [
                assign(401, "hold_summary",
                       "={{ 'Lead from ' + ($json.name || 'unknown') + ' held: ' + $json.hold_reason + '.' }}",
                       atype="string"),
            ],
        },
        "options": {},
    },
    tv=3.4,
)
link(branch, h_prep, 1)

h_stub = add(
    "Stub: hold lead with reason (not connected)", "noOp", x, y + 130,
)
link(h_prep, h_stub)

workflow = {
    "name": "SIM TSL: Lead Intake and Qualification",
    "nodes": nodes,
    "connections": conns,
    "settings": {"executionOrder": "v1"},
    "pinData": {},
}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tsl-lead-intake-qualification.json")
with open(out, "w") as f:
    json.dump(workflow, f, indent=2)
print(f"{len(nodes)} nodes -> {out}")
