import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
QUESTIONS_DIR = DATA_DIR / "questions"
PROMPTS_DIR = BASE_DIR / "prompts"
RESULTS_DIR = BASE_DIR / "results"
RAW_RESULTS_DIR = RESULTS_DIR / "raw_outputs"
SCORED_RESULTS_DIR = RESULTS_DIR / "scored_outputs"
REPORTS_DIR = RESULTS_DIR / "reports"

# Ensure directories exist
for folder in [QUESTIONS_DIR, PROMPTS_DIR, RAW_RESULTS_DIR, SCORED_RESULTS_DIR, REPORTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Default Models
DEFAULT_LLM_JUDGE = os.getenv("DEFAULT_LLM_JUDGE", "gemini/gemini-1.5-pro")

# Supported candidate models mapping (friendly_name -> litellm_name)
SUPPORTED_MODELS = {
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "claude-3-5-sonnet": "anthropic/claude-3-5-sonnet-20241022",
    "gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "gemini-1.5-flash": "gemini/gemini-1.5-flash",
    "deepseek-chat": "openrouter/deepseek/deepseek-chat", # DeepSeek-V3 via OpenRouter
    "deepseek-reasoner": "openrouter/deepseek/deepseek-r1", # DeepSeek-R1 via OpenRouter
    
    # 2026 Frontier Models (from Artificial Analysis Leaderboard)
    "claude-fable-5": "anthropic/claude-fable-5",
    "gpt-5.6-sol": "openai/gpt-5.6-sol",
    "claude-opus-4.8": "anthropic/claude-opus-4.8",
    "gpt-5.6-terra": "openai/gpt-5.6-terra",
    "gpt-5.5": "openai/gpt-5.5",
    "grok-4.5": "openrouter/x-ai/grok-4.5",
    "claude-sonnet-5": "anthropic/claude-sonnet-5"
}

