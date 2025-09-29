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
SYSTEM_ROLE = """You are a concise, senior fiction editor and story doctor.

CRITICAL INSTRUCTION: When analyzing character names, you MUST use the EXACT names that appear in the text. Do NOT change, substitute, or invent character names. If a character is named "Eldrin" in the text, you MUST refer to them as "Eldrin" - never as "Ethan" or any other name.

Always double-check character names before writing your analysis. Respond in English."""

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
            
            # Create client with API key and org (skip project for compatibility)
            client_args = {'api_key': config['api_key']}
            if config['org']:
                client_args['organization'] = config['org']
            # Skip project to avoid 401 errors with project-scoped keys
            # if config['project']:
            #     client_args['project'] = config['project']
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
        return [{"title": f"Section {i+1}", "content": b} for i, b in enumerate(blocks)]
    chunks = []
    lead = parts[0].strip()
    if lead:
        chunks.append({"title":"Prologue/Lead","content":lead})
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body  = (parts[i+1].strip() if i+1 < len(parts) else "")
        chunks.append({"title": title, "content": body})
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
RUBRIC = """FIRST: Extract ALL character names from the text below BEFORE starting analysis.

Rate each component 0–5 (0=absent, 3=okay, 5=strong) with 1–2 sentences of reasoning:

⚠️ MANDATORY: Use ONLY the exact character names found in the text. If you see "Eldrin" - use "Eldrin", NOT "Ethan" or any other name. DO NOT substitute names.

1) Plot & structure
2) Pacing & tension arc
3) Character development & motivation (use exact names: if text has "Eldrin", write "Eldrin")
4) Worldbuilding & consistency
5) Style & tone (show don't tell, avoid info-dumps)
6) Dialogue (subtext, voice - use exact names from text)
7) Theme & emotion
8) Continuity & logic

Also provide: 5 micro-rewrites (sentences/paragraphs), 1 'Mini-Revision' (80–120 words), 3 follow-up suggestions.

⚠️ FINAL CHECK: Before submitting, verify ALL character names match the original text exactly.
"""

def p_outline(full_text):
    return f"""Create a 10–15 bullet point outline of this manuscript; also provide 5 bullets covering premise/protagonist/antagonist/emotional core/genre vibe.
TEXT:
{full_text[:15000]}"""

def p_rubric(title, text):
    # Extract character names from text
    import re
    # Find potential character names (capitalized words that appear multiple times)
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    name_counts = {}
    stopwords = {'Het', 'De', 'Een', 'Maar', 'En', 'Of', 'Dan', 'Dus', 'Want', 'Omdat', 'Toen', 'Als', 'Dat', 'Dit', 'Die', 'Deze', 'Wel', 'Niet', 'Ook', 'Nog'}
    
    for word in words:
        if word not in stopwords:
            name_counts[word] = name_counts.get(word, 0) + 1
    
    # Get likely character names (appearing 2+ times)
    character_names = [name for name, count in name_counts.items() if count >= 2]
    character_list = ", ".join(character_names) if character_names else "geen duidelijke karakternamen gedetecteerd"
    
    return f"""Section: {title}

CHARACTER NAMES IN THIS TEXT: {character_list}
⚠️ USE ONLY THESE EXACT NAMES - DO NOT CHANGE OR SUBSTITUTE THEM ⚠️

Rubric:
{RUBRIC}
TEXT:
{text[:12000]}"""

def p_short_rewrite(title, text):
    return f"""Rewrite this section concisely (300–400 words), preserve core events, increase micro-tension and subtext, remove info-dumps.
Section: {title}
TEXT:
{text[:6000]}"""

def p_top_issues(rubric_blobs):
    return "Summarize the 10 most important issues in 1 sentence per point:\n\n" + "\n\n".join(rubric_blobs)

def p_plan(outline, issues):
    return f"""Create a phased improvement plan (Quick Wins → Structure → Style → Polishing) with goals, actions, expected effects.
OUTLINE:
{outline}

ISSUES:
{issues}"""

def p_timeline_feedback(timeline_rows):
    return f"""Here are time markers per section. Identify max 10 possible inconsistencies with fix suggestions.
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
    ap.add_argument("files", nargs="+", help="Path to .docx/.md/.txt files")
    ap.add_argument("--provider", choices=["ollama","openai"], default="ollama")
    ap.add_argument("--model", default="llama3.1")
    ap.add_argument("--no-rewrite", action="store_true", help="Skip section rewrites")
    ap.add_argument("--client-name", help="Client name for organized export (creates client-specific folder)")
    ap.add_argument("--export-path", help="Custom export path for client folders (e.g., G:\\Mijn Drive\\The arc crusade\\Export Arc Crusade Program)")
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
        m = rough_metrics(sec["content"])
        rub = call_model(p_rubric(sec["title"], sec["content"]), args.provider, args.model, 0.3)
        rubric_blobs.append(f"--- {sec['title']} ---\n{rub[:4000]}")
        rewrite = ""
        if not args.no_rewrite:
            rewrite = call_model(p_short_rewrite(sec["title"], sec["content"]), args.provider, args.model, 0.5)
        results.append({"title": sec["title"], "metrics": m, "rubric": rub, "rewrite": rewrite})

    top_issues = call_model(p_top_issues(rubric_blobs), args.provider, args.model, 0.2)
    plan = call_model(p_plan(outline, top_issues), args.provider, args.model, 0.2)

    timeline_rows = []
    for sec in sections:
        marks = extract_time_markers(sec["content"])
        pretty = "; ".join([f"{k}:{v}" for (k,v) in marks]) if marks else "(geen)"
        timeline_rows.append(f"* {sec['title']}: {pretty}")
    timeline_text = "\n".join(timeline_rows)
    timeline_feedback = call_model(p_timeline_feedback(timeline_text), args.provider, args.model, 0.2)

    # Exports
    ts = time.strftime("%Y%m%d-%H%M%S")
    report_md = [f"# Manuscript Analysis Report – {ts}",
                 "## Outline", outline,
                 "## Top 10 Issues", top_issues,
                 "## Improvement Plan", plan,
                 "## Timeline (extraction)", "```\n"+timeline_text+"\n```",
                 "## Timeline Consistency (advice)", timeline_feedback,
                 "## Sections"]
    rew_dir = OUTPUT_DIR / "rewrites"; rew_dir.mkdir(exist_ok=True)
    for r in results:
        report_md += [f"### {r['title']}",
                      f"- Metrics: {json.dumps(r['metrics'])}",
                      "#### Analysis", r["rubric"],
                      "#### Rewrite Suggestion", r["rewrite"] or "_(disabled)_"]
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
    
    # Create analysis data structure
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
    
    # Try OneDrive integration with client-specific export
    if HAS_ONEDRIVE:
        try:
            onedrive = OneDriveManager()
            
            # Setup custom export path if provided
            if args.export_path:
                if onedrive.set_custom_export_path(args.export_path):
                    print(f"✅ Custom export path set: {args.export_path}")
                else:
                    print(f"⚠️ Custom export path not accessible: {args.export_path}")
            
            # If client name provided, use client-specific export
            if args.client_name and args.export_path:
                # Get original file for client folder
                original_file = Path(args.files[0]) if args.files else None
                
                success = onedrive.save_analysis_to_client_folder(
                    client_name=args.client_name,
                    analysis_data=analysis_data,
                    report_content="\n\n".join(report_md),
                    original_file=original_file,
                    rewrite_files=rewrite_files,
                    timestamp=ts
                )
                
                if success:
                    print(f"✅ Complete. Local files: {OUTPUT_DIR}")
                    print(f"🎯 Client export: {args.export_path}\\{args.client_name}_*_{ts[:8]}")
                    print(f"📋 Analysis organized per client with complete structure!")
                else:
                    print(f"✅ Complete. See folder: {OUTPUT_DIR}")
                    print("⚠️ Client export failed - files saved locally only")
                    
            # Standard OneDrive backup if available
            elif onedrive.is_onedrive_available():
                success = onedrive.save_analysis_to_onedrive(
                    analysis_data=analysis_data,
                    report_content="\n\n".join(report_md),
                    rewrite_files=rewrite_files,
                    timestamp=ts
                )
                
                if success:
                    print(f"✅ Complete. See folder: {OUTPUT_DIR}")
                    print(f"📁 Also saved to OneDrive: {onedrive.base_path}")
                    if args.client_name:
                        print("💡 TIP: Use --export-path with --client-name for organized client exports")
                else:
                    print(f"✅ Complete. See folder: {OUTPUT_DIR}")
                    print("⚠️ OneDrive save failed - files saved locally only")
            else:
                print(f"✅ Complete. See folder: {OUTPUT_DIR}")
                print("ℹ️ OneDrive not found - files saved locally only")
                if args.client_name:
                    print("💡 TIP: Use --export-path with --client-name for organized client exports")
                    
        except Exception as e:
            print(f"✅ Complete. See folder: {OUTPUT_DIR}")
            print(f"⚠️ OneDrive error: {e}")
    else:
        print(f"✅ Complete. See folder: {OUTPUT_DIR}")
        print("ℹ️ OneDrive integration not available")
        if args.client_name:
            print("💡 Install OneDrive integration for client-organized exports")

if __name__ == "__main__":
    main()