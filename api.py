from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse
import uvicorn, tempfile, os
from pathlib import Path
from dotenv import load_dotenv

from cli_manuscript_assistant import read_file, split_sections, rough_metrics, extract_time_markers, \
    call_model, p_outline, p_rubric, p_short_rewrite, p_top_issues, p_plan, p_timeline_feedback

load_dotenv()

API_KEY = os.getenv("ARC_API_KEY", "change-me")

app = FastAPI(title="Manuscript Analyzer API")

@app.post("/analyze")
async def analyze(file: UploadFile = File(...),
                  provider: str = Form("ollama"),
                  model: str = Form("llama3.1"),
                  rewrites: str = Form("true"),
                  x_arc_key: str = Header(None)):
    if x_arc_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    data = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(data); tmp_path = tmp.name
    text = read_file(Path(tmp_path))
    os.unlink(tmp_path)

    sections = split_sections(text)
    outline = call_model(p_outline(text), provider, model, 0.2)
    results, rubs = [], []
    for s in sections:
        rub = call_model(p_rubric(s["title"], s["text"]), provider, model, 0.3)
        rubs.append(rub[:4000])
        rewrite = call_model(p_short_rewrite(s["title"], s["text"]), provider, model, 0.5) if rewrites=="true" else ""
        results.append({"title": s["title"], "metrics": rough_metrics(s["text"]), "rubric": rub, "rewrite": rewrite})

    issues = call_model(p_top_issues([f"--- {r['title']} ---\n{r['rubric']}" for r in results]), provider, model, 0.2)
    plan = call_model(p_plan(outline, issues), provider, model, 0.2)
    timeline_rows = "\n".join([f"* {s['title']}: " + ("; ".join([f\"{k}:{v}\" for (k,v) in extract_time_markers(s['text'])]) or "(geen)") for s in sections])
    timeline_feedback = call_model(p_timeline_feedback(timeline_rows), provider, model, 0.2)

    return JSONResponse({"outline": outline, "issues": issues, "plan": plan,
                         "timeline_extract": timeline_rows, "timeline_feedback": timeline_feedback,
                         "sections": results})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
