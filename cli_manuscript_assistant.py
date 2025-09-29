#!/usr/bin/env python3
import os, re, json, time, argparse
from pathlib import Path
from dotenv import load_dotenv

# --- optioneel .docx ondersteuning ---
try:
    from docx import Document as DocxDocument
except Exception:
    DocxDocument = None

OUTPUT_DIR = Path("outputs"); OUTPUT_DIR.mkdir(exist_ok=True)

# ====== MODEL ROUTER ======
SYSTEM_ROLE = "You are a concise, senior fiction editor and story doctor."
def call_model(prompt, provider="ollama", model="llama3.1", temperature=0.3, system=SYSTEM_ROLE):
    if provider == "ollama":
        import requests
        url = "http://localhost:11434/api/chat"
        payload = {"model": model, "messages":[{"role":"system","content":system},{"role":"user","content":prompt}],
                   "stream": False, "options":{"temperature": temperature}}
        r = requests.post(url, json=payload, timeout=600); r.raise_for_status()
        return (r.json().get("message") or {}).get("content","").strip()
    elif provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        org = os.getenv("OPENAI_ORG_ID")
        project = os.getenv("OPENAI_PROJECT")
        base = os.getenv("OPENAI_BASE")

        client = OpenAI(api_key=api_key, organization=org, project=project, base_url=base)
        resp = client.chat.completions.create(model=model, temperature=temperature,
                    messages=[{"role":"system","content":system},{"role":"user","content":prompt}])
        return resp.choices[0].message.content.strip()
    else:
        raise SystemExit("Unknown provider (use 'ollama' or 'openai').")

# ====== HELPERS ======
def read_file(path: Path) -> str:
    p = Path(path)
    if p.suffix.lower() in [".txt", ".md"]:
        return p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix.lower() == ".docx" and DocxDocument:
        doc = DocxDocument(str(p))
        return "\n".join(par.text for par in doc.paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")

def split_sections(text: str):
    parts = re.split(r"(?im)^\s*(hoofdstuk\s+\d+|chapter\s+\d+|#+\s+.+)\s*$", text)
    if len(parts) <= 1:
        blocks = [b.strip() for b in re.split(r"\n{3,}", text) if b.strip()]
        return [{"title": f"Section {i+1}", "text": b} for i, b in enumerate(blocks)]
    chunks = []
    lead = parts[0].strip()
    if lead:
        chunks.append({"title":"Prologue/Lead","text":lead})
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body  = (parts[i+1].strip() if i+1 < len(parts) else "")
        chunks.append({"title": title, "text": body})
    return chunks

def rough_metrics(text):
    words = re.findall(r"\w+(?:'\w+)?", text); wc = len(words)
    sents = [s for s in re.split(r"(?<=[\.\!\?])\s+", text) if s.strip()]
    avg = (sum(len(s.split()) for s in sents)/len(sents)) if sents else 0
    dialogs = re.findall(r"[\"“”\'’].+?[\"“”\'’]", text, flags=re.S)
    dshare = (sum(len(d.split()) for d in dialogs)/wc) if wc else 0
    adverbs = re.findall(r"\b\w+ly\b", text) + re.findall(r"\b\w+lijk\b", text, flags=re.I)
    return {"words": wc, "sentences": len(sents), "avg_sentence_words": round(avg,2),
            "dialog_word_share": round(dshare,3), "adverb_count": len(adverbs)}

MONTHS = "(jan|feb|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)"
def extract_time_markers(text):
    markers=[]
    for m in re.finditer(r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4})\b", text):
        markers.append(("date", m.group()))
    for m in re.finditer(rf"\b(\d{{1,2}}\s+{MONTHS}|{MONTHS}\s+\d{{1,2}})\b", text, flags=re.I):
        markers.append(("month_day", m.group()))
    for m in re.finditer(r"\b(vandaag|gisteren|morgen|eergisteren|overmorgen|vroeger|later|binnenkort|toen|nu)\b", text, flags=re.I):
        markers.append(("relative", m.group()))
    for m in re.finditer(r"\b(\d{1,2}:\d{2})\b", text):
        markers.append(("time", m.group()))
    return markers

# ====== PROMPTS ======
RUBRIC = """Beoordeel elk onderdeel op 0–5 (0=afwezig, 3=oké, 5=sterk) met 1–2 zinnen motivatie:
1) Plot & structuur
2) Pacing & spanningsboog
3) Personageontwikkeling & motivatie
4) Worldbuilding & consistentie
5) Stijl & toon (show, geen info-dumps)
6) Dialoog (subtekst, stemmen)
7) Thematiek & emotie
8) Continuïteit & logica
Lever ook: 5 micro-rewrites (zinnen/alinea’s), 1 'Mini-Revision' (80–120 w), 3 vervolg-adviezen.
"""

def p_outline(full_text):
    return f"""Maak 10–15 bullets outline van dit manuscript; geef daarnaast 5 bullets met premisse/protagonist/antagonist/emotionele kern/genre vibe.
TEKST:
{full_text[:15000]}"""

def p_rubric(title, text):
    return f"""Sectie: {title}
Rubriek:
{RUBRIC}
TEKST:
{text[:12000]}"""

def p_short_rewrite(title, text):
    return f"""Herschrijf compact (300–400 woorden) deze sectie, behoud kerngebeurtenissen, verhoog micro-tension en subtekst, verwijder info-dumps.
Sectie: {title}
TEKST:
{text[:6000]}"""

def p_top_issues(rubric_blobs):
    return "Vat de 10 belangrijkste problemen in 1 zin per punt:\n\n" + "\n\n".join(rubric_blobs)

def p_plan(outline, issues):
    return f"""Maak een gefaseerd verbeterplan (Quick Wins → Structure → Style → Polishing) met doelen, acties, verwacht effect.
OUTLINE:
{outline}

ISSUES:
{issues}"""

def p_timeline_feedback(timeline_rows):
    return f"""Hier zijn tijdsmarkeringen per sectie. Noem max 10 mogelijke inconsistenties met fix-suggesties.
{timeline_rows}"""

# ====== MAIN ======
def main():
    load_dotenv = True
    try:
        if load_dotenv:
            from dotenv import load_dotenv as _ld
            _ld()
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Manuscript analyzer (CLI)")
    ap.add_argument("files", nargs="+", help="Pad naar .docx/.md/.txt")
    ap.add_argument("--provider", choices=["ollama","openai"], default="ollama")
    ap.add_argument("--model", default="llama3.1")
    ap.add_argument("--no-rewrite", action="store_true", help="Sla sectie-herschrijf over")
    args = ap.parse_args()

    # Combineer input
    full_text = ""
    sections = []
    for f in args.files:
        txt = read_file(Path(f))
        full_text += f"\n\n=== FILE: {Path(f).name} ===\n\n{txt}"
        sections += split_sections(txt)

    outline = call_model(p_outline(full_text), args.provider, args.model, 0.2)
    results = []
    rubric_blobs = []

    for sec in sections:
        m = rough_metrics(sec["text"])
        rub = call_model(p_rubric(sec["title"], sec["text"]), args.provider, args.model, 0.3)
        rubric_blobs.append(f"--- {sec['title']} ---\n{rub[:4000]}")
        rewrite = ""
        if not args.no_rewrite:
            rewrite = call_model(p_short_rewrite(sec["title"], sec["text"]), args.provider, args.model, 0.5)
        results.append({"title": sec["title"], "metrics": m, "rubric": rub, "rewrite": rewrite})

    top_issues = call_model(p_top_issues(rubric_blobs), args.provider, args.model, 0.2)
    plan = call_model(p_plan(outline, top_issues), args.provider, args.model, 0.2)

    timeline_rows = []
    for sec in sections:
        marks = extract_time_markers(sec["text"])
        pretty = "; ".join([f"{k}:{v}" for (k,v) in marks]) if marks else "(geen)"
        timeline_rows.append(f"* {sec['title']}: {pretty}")
    timeline_text = "\n".join(timeline_rows)
    timeline_feedback = call_model(p_timeline_feedback(timeline_text), args.provider, args.model, 0.2)

    # Exports
    ts = time.strftime("%Y%m%d-%H%M%S")
    report_md = [f"# Manuscript Rapport – {ts}",
                 "## Outline", outline,
                 "## Top 10 Issues", top_issues,
                 "## Verbeterplan", plan,
                 "## Tijdlijn (extractie)", "```\n"+timeline_text+"\n```",
                 "## Tijdlijn-consistentie (advies)", timeline_feedback,
                 "## Secties"]
    rew_dir = OUTPUT_DIR / "rewrites"; rew_dir.mkdir(exist_ok=True)
    for r in results:
        report_md += [f"### {r['title']}",
                      f"- Metrics: {json.dumps(r['metrics'])}",
                      "#### Rubriek", r["rubric"],
                      "#### Herschrijfsuggestie", r["rewrite"] or "_(uit)_"]
        if r["rewrite"]:
            safe = re.sub(r"[^a-zA-Z0-9_-]+","-", r["title"])[:60]
            (rew_dir / f"{safe}-{ts}.md").write_text(r["rewrite"], encoding="utf-8")

    (OUTPUT_DIR / f"report-{ts}.md").write_text("\n\n".join(report_md), encoding="utf-8")
    (OUTPUT_DIR / f"results-{ts}.json").write_text(json.dumps(
        {"outline": outline, "issues": top_issues, "plan": plan,
         "timeline_extract": timeline_text, "timeline_feedback": timeline_feedback,
         "sections": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Klaar. Zie map: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
