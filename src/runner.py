import os
import json
import time
from datetime import datetime
from pathlib import Path
from src import config, models

def load_prompt_template(mode: str) -> str:
    """Load prompt template from file based on mode."""
    file_path = config.PROMPTS_DIR / f"{mode}.txt"
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template for mode '{mode}' not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_questions(areas=None) -> list:
    """
    Load questions from JSONL files in the data directory.
    Args:
        areas (list): List of area names to load (e.g. ['icra', 'kira']). If None, load all.
    """
    questions = []
    files = list(config.QUESTIONS_DIR.glob("*.jsonl"))
    
    if not files:
        raise FileNotFoundError(f"No question files found in {config.QUESTIONS_DIR}")
        
    for file in files:
        area_name = file.stem
        if areas and area_name not in areas:
            continue
            
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line.strip()))
                    
    return questions

def run_evaluation(model_name: str, mode: str = "closed_book", areas: list = None, limit: int = None) -> str:
    """
    Run evaluation for a specific model and mode.
    Returns:
        str: Path to the generated raw results JSON file.
    """
    questions = load_questions(areas)
    if limit:
        questions = questions[:limit]
        
    template = load_prompt_template(mode)
    
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp = datetime.now().isoformat()
    
    records = []
    
    print(f"Loaded {len(questions)} questions. Starting run for model {model_name} in {mode} mode...")
    
    for idx, q in enumerate(questions):
        print(f"[{idx+1}/{len(questions)}] Running {q['id']} ({q['area']})...")
        
        # Prepare prompt
        prompt = template.replace("{{question}}", q["question"])
        if mode == "open_book":
            ref_text = q.get("reference_text", "")
            prompt = prompt.replace("{{reference_text}}", ref_text)
            
        # Call model
        messages = [{"role": "user", "content": prompt}]
        response = models.call_model(model_name, messages)
        
        record = {
            "question_id": q["id"],
            "area": q["area"],
            "task_type": q["task_type"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "expected_answer": q["expected_answer"],
            "legal_basis": q.get("legal_basis", []),
            "reference_text": q.get("reference_text", ""),
            "rubric_type": q["rubric_type"],
            "rubric": q.get("rubric", {}),
            "trap_type": q.get("trap_type"),
            "trap_details": q.get("trap_details", ""),
            "tags": q.get("tags", []),
            "prompt": prompt,
            "model_answer": response["content"],
            "prompt_tokens": response["prompt_tokens"],
            "completion_tokens": response["completion_tokens"],
            "duration": response["duration"],
            "status": response["status"],
            "error_msg": response["error_msg"]
        }
        
        records.append(record)
        # Sleep slightly to avoid aggressive rate limits
        time.sleep(0.5)
        
    output_data = {
        "run_id": run_id,
        "model_name": model_name,
        "mode": mode,
        "timestamp": timestamp,
        "results": records
    }
    
    output_filename = f"run_{run_id}_{model_name.replace('/', '_')}_{mode}.json"
    output_path = config.RAW_RESULTS_DIR / output_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"Run completed. Raw outputs saved to {output_path}")
    return str(output_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TRLawBench-Practice Runner")
    parser.add_argument("model", nargs="?", default="gemini-1.5-flash", help="Candidate model name (e.g. gemini-1.5-flash)")
    parser.add_argument("mode", nargs="?", default="closed_book", help="Evaluation mode (closed_book or open_book)")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of questions to evaluate (default: None for full run)")
    args = parser.parse_args()
    
    run_evaluation(args.model, args.mode, limit=args.limit)
