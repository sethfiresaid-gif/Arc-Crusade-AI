#!/usr/bin/env python3
import os, re, json, time, argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- optioneel .docx ondersteuning ---
try:
    from docx import Document as DocxDocument
except Exception:
    DocxDocument = None

# --- Streamlit support ---
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# --- OneDrive integration ---
try:
    from onedrive_integration import OneDriveManager
    HAS_ONEDRIVE = True
except ImportError:
    HAS_ONEDRIVE = False

# --- Enhanced analysis import ---
from enhanced_analysis import (
    analyze_character_development, analyze_pacing, analyze_style_issues, 
    analyze_show_vs_tell, p_advanced_rewrite, p_character_voice_analysis,
    p_scene_structure_analysis, p_emotional_depth_analysis, 
    p_prose_quality_analysis, p_genre_specific_analysis
)

OUTPUT_DIR = Path("outputs"); OUTPUT_DIR.mkdir(exist_ok=True)

# ====== MODEL ROUTER ======
SYSTEM_ROLE = "You are a concise, senior fiction editor and story doctor."
def rough_metrics(text):
    words = re.findall(r"\w+(?:'\w+)?", text); wc = len(words)
    sents = [s for s in re.split(r"(?<=[\.\!\?])\s+", text) if s.strip()]
    avg = (sum(len(s.split()) for s in sents)/len(sents)) if sents else 0
    dialogs = re.findall(r"[\"""\''].+?[\"""\'']", text, flags=re.S)
    dshare = (sum(len(d.split()) for d in dialogs)/wc) if wc else 0
    adverbs = re.findall(r"\b\w+ly\b", text) + re.findall(r"\b\w+lijk\b", text, flags=re.I)
    return {"words": wc, "sentences": len(sents), "avg_sentence_words": round(avg,2),
            "dialog_word_share": round(dshare,3), "adverb_count": len(adverbs)}

def enhanced_metrics(text):
    """Uitgebreide metrics inclusief stijl en karakteranalyse"""
    basic = rough_metrics(text)
    
    # Voeg geavanceerde analyses toe
    character_data = analyze_character_development(text)
    pacing_data = analyze_pacing(text)
    style_issues = analyze_style_issues(text)
    show_tell = analyze_show_vs_tell(text)
    
    return {
        **basic,
        "characters": character_data,
        "pacing": pacing_data,
        "style_issues": style_issues,
        "show_vs_tell": show_tell,
        "readability_score": calculate_readability_score(text),
        "engagement_score": calculate_engagement_score(pacing_data, show_tell, len(style_issues))
    }

def calculate_readability_score(text):
    """Bereken leesbaarheidscore gebaseerd op zinslengte en woordcomplexiteit"""
    words = text.split()
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    
    if not words or not sentences:
        return 0.0
    
    avg_words_per_sentence = len(words) / len(sentences)
    long_words = len([w for w in words if len(w) > 6])
    long_word_ratio = long_words / len(words)
    
    # Flesch-achtige score aangepast voor Nederlands
    score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * long_word_ratio)
    return max(0.0, min(100.0, round(score, 1)))

def calculate_engagement_score(pacing_data, show_tell_data, issues_count):
    """Bereken engagement score (1-10) gebaseerd op verschillende factoren"""
    pacing_score = pacing_data.get('pacing_score', 5.0)
    show_tell_score = show_tell_data.get('show_vs_tell_score', 5.0)
    
    # Penalties voor issues
    issue_penalty = min(issues_count * 0.5, 3.0)
    
    engagement = (pacing_score + show_tell_score) / 2 - issue_penalty
    return max(1.0, min(10.0, round(engagement, 1)))

MONTHS = "(jan|feb|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)"

def get_api_config():
    """Get API configuration from Streamlit secrets or environment variables"""
    def get_secret(key, default=None):
        # Try Streamlit secrets first
        if HAS_STREAMLIT:
            try:
                value = st.secrets.get(key)
                if value:
                    return value
            except (KeyError, FileNotFoundError, AttributeError):
                pass
        
        # Fallback to environment variables
        return os.getenv(key, default)
    
    config = {
        'api_key': get_secret("OPENAI_API_KEY"),
        'org': get_secret("OPENAI_ORG_ID"),
        'project': get_secret("OPENAI_PROJECT"),
        'base': get_secret("OPENAI_BASE")
    }
    
    # Ensure we have at least an API key
    if not config['api_key']:
        raise ValueError("OPENAI_API_KEY not found in secrets or environment variables")
    
    return config

def save_analysis_with_onedrive(analysis_data, report_content, rewrite_files=None, timestamp=None):
    """Helper function for Streamlit app to save analysis with OneDrive integration"""
    if not HAS_ONEDRIVE:
        return False, "OneDrive integration niet beschikbaar"
    
    try:
        onedrive = OneDriveManager()
        if not onedrive.is_onedrive_available():
            return False, "OneDrive niet gevonden op dit systeem"
        
        if timestamp is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        success = onedrive.save_analysis_to_onedrive(
            analysis_data=analysis_data,
            report_content=report_content,
            rewrite_files=rewrite_files or [],
            timestamp=timestamp
        )
        
        if success:
            onedrive_path = onedrive.base_path / 'Arc-Crusade-AI'
            return True, f"Succesvol opgeslagen in OneDrive: {onedrive_path}"
        else:
            return False, "OneDrive opslaan mislukt"
            
    except Exception as e:
        return False, f"OneDrive error: {str(e)}"

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
        try:
            config = get_api_config()
            
            # Create client with only non-None values
            client_args = {'api_key': config['api_key']}
            if config['org']:
                client_args['organization'] = config['org']
            if config['project']:
                client_args['project'] = config['project']
            if config['base']:
                client_args['base_url'] = config['base']
            
            client = OpenAI(**client_args)
            resp = client.chat.completions.create(
                model=model, 
                temperature=temperature,
                messages=[{"role":"system","content":system},{"role":"user","content":prompt}]
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")
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

def extract_time_markers(text):
    months = r"\b" + MONTHS + r"\b"
    times = [("Maand",months), ("Dag",r"\b\d{1,2}\s+(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\b"),
             ("Week",r"\b(?:maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)\b"),
             ("Time",r"\b\d{1,2}:\d{2}\b"), ("Age",r"\b\d{1,2}\s+jaar\s+oud\b")]
    result = []
    for label, patt in times:
        matches = re.findall(patt, text, flags=re.I)
        if matches:
            result.append((label, ", ".join(set(matches))))
    return result

# ====== PROMPTS ======
RUBRIC = """Beoordeel elk onderdeel op 0–5 (0=afwezig, 3=oké, 5=sterk) met 1–2 zinnen motivatie:

BELANGRIJK: Gebruik EXACTE karakternamen uit de tekst. Verander geen namen, verzin geen alternatieven.

1) Plot & structuur
2) Pacing & spanningsboog  
3) Personageontwikkeling & motivatie (gebruik exacte namen uit tekst)
4) Worldbuilding & consistentie
5) Stijl & toon (show, geen info-dumps)
6) Dialoog (subtekst, stemmen - gebruik exacte namen)
7) Thematiek & emotie
8) Continuïteit & logica

Lever ook: 5 micro-rewrites (zinnen/alinea's), 1 'Mini-Revision' (80–120 w), 3 vervolg-adviezen.

LET OP: Bij het bespreken van personages, kopieer hun namen LETTERLIJK uit de originele tekst.
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

    # Save locally
    report_path = OUTPUT_DIR / f"report-{ts}.md"
    results_path = OUTPUT_DIR / f"results-{ts}.json"
    
    report_path.write_text("\n\n".join(report_md), encoding="utf-8")
    results_path.write_text(json.dumps(
        {"outline": outline, "issues": top_issues, "plan": plan,
         "timeline_extract": timeline_text, "timeline_feedback": timeline_feedback,
         "sections": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Try OneDrive integration
    if HAS_ONEDRIVE:
        try:
            onedrive = OneDriveManager()
            if onedrive.is_onedrive_available():
                # Create analysis data for OneDrive
                analysis_data = {
                    'title': f'Manuscript Analysis {ts}',
                    'outline': outline,
                    'top_issues': top_issues,
                    'improvement_plan': plan,
                    'timeline_feedback': timeline_feedback,
                    'sections': results,
                    'metrics_summary': {
                        'total_sections': len(sections),
                        'total_words': sum(r['metrics']['words'] for r in results),
                        'avg_sentence_length': round(sum(r['metrics']['avg_sentence_words'] for r in results) / len(results), 2)
                    }
                }
                
                # Get rewrite files
                rewrite_files = list(rew_dir.glob(f"*-{ts}.md"))
                
                success = onedrive.save_analysis_to_onedrive(
                    analysis_data=analysis_data,
                    report_content="\n\n".join(report_md),
                    rewrite_files=rewrite_files,
                    timestamp=ts
                )
                
                if success:
                    print(f"✅ Klaar. Zie map: {OUTPUT_DIR}")
                    print(f"📁 Ook opgeslagen in OneDrive: {onedrive.base_path / 'Arc-Crusade-AI'}")
                else:
                    print(f"✅ Klaar. Zie map: {OUTPUT_DIR}")
                    print("⚠️ OneDrive opslaan mislukt - bestanden alleen lokaal opgeslagen")
            else:
                print(f"✅ Klaar. Zie map: {OUTPUT_DIR}")
                print("ℹ️ OneDrive niet gevonden - bestanden alleen lokaal opgeslagen")
        except Exception as e:
            print(f"✅ Klaar. Zie map: {OUTPUT_DIR}")
            print(f"⚠️ OneDrive error: {e}")
    else:
        print(f"✅ Klaar. Zie map: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()