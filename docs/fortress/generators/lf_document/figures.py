"""Rule client-document-figures. Builds and checks the figures manifest for each doc type. Figures are
keyed by id; the renderer numbers them in reading order and asks caption() for the fixed caption."""
from __future__ import annotations
import datetime as _dt

REQUIRED = {
    "handoff": ["summary_tiles", "figures", "before_after", "paths_tested"],
    "audit": ["summary_tiles", "figures", "paths_tested"],
    "architecture": ["summary_tiles", "figures"],
    "proposal": ["summary_tiles", "baseline_or_week_one"],
    "quote": ["summary_tiles", "baseline_or_week_one"],
}


def date_words(iso: str) -> str:
    d = _dt.date.fromisoformat(iso[:10])
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def caption(n: int, fig: dict) -> str:
    c = "Figure %d. %s, read from your accounts on %s. No contact details." % (n, fig["shows"].rstrip("."), date_words(fig["read_at"]))
    return c + (" " + fig["note"] if fig.get("note") else "")


def _sourced(x: dict) -> bool:
    return bool(x.get("source") and x.get("read_at"))


def _proof_ok(v) -> bool:
    return isinstance(v, str) and (v.startswith("Test") or v.startswith("Real"))


def manifest_for(doc_type: str, record: dict) -> dict:
    f = record.get("figures") or {}
    problems, figs = [], {}
    for t in f.get("tiles", []):
        if not _sourced(t):
            problems.append("Summary tile '%s' has no source and read date." % t.get("label"))
    for fid, fig in (f.get("figures") or {}).items():
        if not _sourced(fig):
            problems.append("Figure '%s' has no source and read date." % fid)
        for tb in fig.get("tables", []):
            cols = [c.lower() for c in tb["columns"]]
            if fig.get("kind") == "paths_tested":
                if "proof" not in cols:
                    problems.append("Figure '%s' has no Test or Real proof column." % fid)
                else:
                    i = cols.index("proof")
                    for r in tb["rows"]:
                        if not _proof_ok(r[i]):
                            problems.append("Figure '%s' path '%s' has no Test or Real proof." % (fid, r[1] if len(r) > 1 else r[0]))
        if fig.get("kind") == "before_after" and not any({"before", "after"} <= {c.lower() for c in tb["columns"]} for tb in fig.get("tables", [])):
            problems.append("Figure '%s' has no before and after counts." % fid)
        figs[fid] = fig
    kinds = {fig.get("kind") for fig in figs.values()}
    need = REQUIRED.get(doc_type, [])
    if "summary_tiles" in need and not f.get("tiles"):
        problems.append("No one page summary number tiles.")
    if "figures" in need and not figs:
        problems.append("No figures.")
    if "before_after" in need and record.get("changed_anything", True) and "before_after" not in kinds:
        problems.append("Something was changed but no before and after counts are shown.")
    if "paths_tested" in need and record.get("paths_tested_expected", True) and "paths_tested" not in kinds:
        problems.append("Paths were tested but no Test or Real proof table is shown.")
    if "baseline_or_week_one" in need:
        base, week1 = f.get("baseline") or [], f.get("week_one_measurements") or []
        if base:
            pa = record.get("price_set_at")
            for b in base:
                if not _sourced(b):
                    problems.append("Baseline '%s' has no source and read date." % b.get("label"))
                elif pa and b["read_at"] > pa:
                    problems.append("Baseline '%s' was read after the price was set." % b.get("label"))
        elif not week1:
            problems.append("A proposal needs baseline figures read before the price was set, or the numbers measured in week one. It has neither.")
    return {"doc_type": doc_type, "required": need, "tiles": f.get("tiles", []), "figures": figs,
            "baseline": f.get("baseline") or [], "week_one_measurements": f.get("week_one_measurements") or [],
            "status": "OK" if not problems else "FAIL", "problems": problems}
