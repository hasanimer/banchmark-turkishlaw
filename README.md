# Legaluga Law Benchmark

Legaluga Law Benchmark is a specialized evaluation benchmark designed to measure the capability of Large Language Models (LLMs) in performing daily tasks of a Turkish lawyer.

Unlike standard multiple-choice legal benchmarks (e.g. TRLawBench), this benchmark focuses on **attorney workflows**, assessing:
- **Hukuki Doğruluk & Muhakeme**: Correct application of laws to concrete cases.
- **Süre Hesaplama**: Step-by-step deadline calculations according to the Turkish Execution and Civil Procedure laws (İİK, HMK, CMK, İYUK).
- **Belge Üretimi**: Quality and style of drafting notifications (*ihtarname*), petitions, contracts, and court declarations fitting UYAP and Turkish court practice.
- **Hata Yakalama / Tuzaklar**: The model's capacity to detect legal errors, obsolete or abolished provisions, and fabricated citations (anti-hallucination).

---

## Folder Structure

- `data/questions/`: Contains JSONL question databases for each law area (İcra, Kira, İş, Ceza, Tazminat, İdare/Vergi, Avukatlık/UYAP, Aile/Miras).
- `prompts/`: Standardized prompt templates for evaluations (`closed_book`, `open_book`, `llm_judge_rubric`).
- `src/`: Core Python modules.
  - `config.py`: Environment configurations and model mapping.
  - `models.py`: API wrapper using LiteLLM.
  - `runner.py`: Orchestrates running evaluations against candidate models.
  - `evaluator.py`: Automatic deterministic (MCQ) and LLM-Judge grading pipeline.
- `results/`: Output directories for raw answers, graded outputs, and compiled reports.
- `dashboard/`: Streamlit dashboard code for leaderboards and human review.

---

## Quick Start

### 1. Installation

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 3. Seed Dataset (MVP 80 Tasks)

Generate the initial set of 80 realistic legal tasks (10 per area):
```bash
python3 scripts/seed_questions.py
```

### 4. Run Candidate Evaluations

To run evaluation on a candidate model (e.g., `gemini-1.5-flash` in `closed_book` mode):
```bash
python3 -m src.runner gemini-1.5-flash closed_book
```
This writes the candidate's raw answers to `results/raw_outputs/run_<timestamp>_gemini-1.5-flash_closed_book.json`.

*Note: The script currently defaults to running a small limit (2 questions) for testing when executed directly. To run the full set or custom options, import the `run_evaluation` function or modify the limit.*

### 5. Grade Answers (LLM-Judge)

To run the LLM-Judge evaluation against the raw outputs file:
```bash
python3 -m src.evaluator results/raw_outputs/run_<timestamp>_gemini-1.5-flash_closed_book.json
```
This automatically grades all multiple-choice questions (using exact-match regex) and calls the LLM-Judge (configured via `DEFAULT_LLM_JUDGE` in `.env`) to score open-ended questions using the strict rubrics. Graded outputs are saved to `results/scored_outputs/`.

### 6. Serve the Leaderboard & Dashboard

Run the Streamlit web dashboard:
```bash
streamlit run dashboard/app.py
```
This opens a local dashboard where you can:
- Compare model performance across a visual Leaderboard.
- Inspect the breakdown by legal area and task type.
- Open the **Detaylı Müfettiş (Detailed Inspector)** to see side-by-side questions, golden answers, candidate answers, and judge justifications.
- Use the **İnsan Değerlendirici Formu (Human Review Panel)** to toggle *Human Override*, score the criteria manually, and save the result. Overridden scores are computed using the **70% Human + 30% LLM-Judge** formula.
