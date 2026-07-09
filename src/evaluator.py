import os
import re
import json
import logging
from pathlib import Path
from src import config, models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TRLawBench.evaluator")

def evaluate_mcq(model_answer: str, expected_answer: str) -> dict:
    """Robust parser to evaluate multiple-choice answers deterministically."""
    cleaned_ans = model_answer.strip().upper()
    
    # Try finding capital letters A-E enclosed in word boundaries
    choices = re.findall(r'\b([A-E])\b', cleaned_ans)
    
    detected_choice = None
    if len(choices) == 1:
        detected_choice = choices[0]
    elif len(choices) > 1:
        # Look for explicit patterns like "Cevap: A" or "Doğru şık B"
        patterns = [
            r"(?:CEVAP|ŞIK|SEÇENEK|DOĞRU|DOĞRU YANIT)\s*[:\-]?\s*([A-E])",
            r"\b([A-E])\s*(?:ŞIKKI|SEÇENEĞİ)"
        ]
        for pat in patterns:
            m = re.search(pat, cleaned_ans)
            if m:
                detected_choice = m.group(1)
                break
        if not detected_choice:
            detected_choice = choices[0]  # Fallback to first found
            
    if not detected_choice and len(cleaned_ans) > 0:
        # Check if the very first character is a choice
        first_char = cleaned_ans[0]
        if first_char in ['A', 'B', 'C', 'D', 'E']:
            detected_choice = first_char
            
    is_correct = detected_choice == expected_answer.upper()
    score = 100 if is_correct else 0
    
    return {
        "scores": {"dogruluk": score},
        "total_score": score,
        "justifications": {"dogruluk": f"Modelin seçtiği şık: {detected_choice}. Beklenen şık: {expected_answer}."},
        "feedback": f"Modelin tespit edilen yanıtı: {detected_choice}. Beklenen: {expected_answer}.",
        "hallucination_detected": False,
        "trap_triggered": False
    }

def run_llm_judge(q_id: str, question: str, legal_basis: list, expected_answer: str, model_answer: str, rubric: dict, trap_details: str) -> dict:
    """Call LLM-Judge to grade open-ended answer using prompts/llm_judge_rubric.txt."""
    try:
        # Load template
        template_path = config.PROMPTS_DIR / "llm_judge_rubric.txt"
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # Format prompt
        prompt = template
        prompt = prompt.replace("{{question}}", question)
        prompt = prompt.replace("{{legal_basis}}", ", ".join(legal_basis) if legal_basis else "Belirtilmemiş")
        prompt = prompt.replace("{{expected_answer}}", expected_answer)
        prompt = prompt.replace("{{model_answer}}", model_answer)
        prompt = prompt.replace("{{rubric_definition}}", json.dumps(rubric, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{{trap_details}}", trap_details if trap_details else "Bu soruda özel bir yasal tuzak bulunmamaktadır.")
        
        messages = [{"role": "user", "content": prompt}]
        
        # Invoke judge model
        # Ask for JSON output if supported by model
        response = models.call_model(
            model_name=config.DEFAULT_LLM_JUDGE,
            messages=messages,
            temperature=0.0,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        content = response["content"]
        
        # Clean markdown wrappers if returned
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        eval_data = json.loads(content.strip())
        return eval_data
        
    except Exception as e:
        logger.error(f"Failed to evaluate {q_id} with LLM-Judge: {str(e)}")
        # Fallback empty rubric score
        return {
            "scores": {k: 0 for k in rubric.keys()},
            "total_score": 0,
            "justifications": {"error": f"Değerlendirme sırasında hata oluştu: {str(e)}"},
            "feedback": "Değerlendirme hatası.",
            "hallucination_detected": False,
            "trap_triggered": False
        }

def evaluate_run(raw_results_file_path: str) -> str:
    """
    Read raw results, grade each record, and output scored results.
    """
    path = Path(raw_results_file_path)
    if not path.exists():
        raise FileNotFoundError(f"Raw results file not found at {path}")
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    run_id = data["run_id"]
    model_name = data["model_name"]
    mode = data["mode"]
    timestamp = data["timestamp"]
    results = data["results"]
    
    scored_results = []
    
    print(f"Starting evaluation of run {run_id} ({len(results)} items) for model {model_name}...")
    
    for idx, r in enumerate(results):
        q_id = r["question_id"]
        task_type = r["task_type"]
        
        print(f"[{idx+1}/{len(results)}] Evaluating {q_id} ({task_type})...")
        
        if task_type == "mcq":
            eval_output = evaluate_mcq(r["model_answer"], r["expected_answer"])
        else:
            eval_output = run_llm_judge(
                q_id=q_id,
                question=r["question"],
                legal_basis=r["legal_basis"],
                expected_answer=r["expected_answer"],
                model_answer=r["model_answer"],
                rubric=r["rubric"],
                trap_details=r["trap_details"]
            )
            
        # Merge evaluation info
        evaluated_record = r.copy()
        evaluated_record["scores"] = eval_output.get("scores", {})
        evaluated_record["total_score"] = eval_output.get("total_score", 0)
        evaluated_record["justifications"] = eval_output.get("justifications", {})
        evaluated_record["feedback"] = eval_output.get("feedback", "")
        evaluated_record["hallucination_detected"] = eval_output.get("hallucination_detected", False)
        evaluated_record["trap_triggered"] = eval_output.get("trap_triggered", False)
        
        # If there's an override field, preserve or initialize it
        evaluated_record["human_override"] = False
        evaluated_record["human_scores"] = {}
        evaluated_record["human_total_score"] = None
        evaluated_record["human_feedback"] = ""
        
        scored_results.append(evaluated_record)
        
    # Compile summary metrics
    total_score_sum = sum(x["total_score"] for x in scored_results)
    avg_score = total_score_sum / len(scored_results) if scored_results else 0
    hallucination_count = sum(1 for x in scored_results if x.get("hallucination_detected", False))
    trap_triggered_count = sum(1 for x in scored_results if x.get("trap_triggered", False))
    
    summary = {
        "run_id": run_id,
        "model_name": model_name,
        "mode": mode,
        "timestamp": timestamp,
        "summary": {
            "average_score": avg_score,
            "hallucination_rate": hallucination_count / len(scored_results) if scored_results else 0.0,
            "trap_trigger_rate": trap_triggered_count / len(scored_results) if scored_results else 0.0,
            "total_items": len(scored_results)
        },
        "results": scored_results
    }
    
    output_filename = f"run_{run_id}_{model_name.replace('/', '_')}_{mode}_scored.json"
    output_path = config.SCORED_RESULTS_DIR / output_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        
    print(f"Evaluation completed. Scored outputs saved to {output_path}")
    print(f"Average Score: {avg_score:.2f} | Hallucination Rate: {summary['summary']['hallucination_rate']:.2%}")
    return str(output_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        evaluate_run(sys.argv[1])
    else:
        print("Please provide the path to the raw results file.")
