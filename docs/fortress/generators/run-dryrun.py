#!/usr/bin/env python3
"""Always builds the harness from the CURRENT node file. Never from a snapshot."""
import json, subprocess
code = open("/home/claude/cockpit-evidence-node.js").read()
jobs = open("/home/claude/jobs.json").read()
harness = "function runNode($json){\n%s\n}\nconst JOBS=%s;\n" % (code, jobs) + """
let full=0, gaps=[];
for (const job of JOBS) {
  const o = runNode({jobPost: job.text, jobTitle: job.title})[0].json;
  if (o.proof_ok && o.evidence_count>=3) full++;
  console.log("\\n"+"=".repeat(74));
  console.log(job.title.slice(0,70));
  console.log("  shape :", o.evidence_shape, "->", o.product_name);
  console.log("  tool  :", (o.client_tool||"-"),
    o.client_tool_covered ? "[THEIR OWN TOOL]" : "[showing "+o.evidence_tool_shown+"]");
  (o.evidence||[]).forEach((e,i)=>console.log("   "+(i+1)+". "+e.file.split("/").pop()));
  if (o.gap_notice) { gaps.push(o.gap_notice); console.log("  GAP:", o.gap_notice); }
}
console.log("\\n"+"=".repeat(74));
console.log(full+" of "+JOBS.length+" produce a full pack | "+gaps.length+" raise a build-gap notice");
"""
open("/home/claude/dryrun.js","w").write(harness)
print(subprocess.run(["node","/home/claude/dryrun.js"],capture_output=True,text=True).stdout)
