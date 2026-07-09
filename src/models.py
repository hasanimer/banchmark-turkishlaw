import os
import time
import logging
import litellm
from src import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TRLawBench.models")

# Setup litellm API keys
if config.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
if config.ANTHROPIC_API_KEY:
    os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
if config.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = config.GEMINI_API_KEY
if config.OPENROUTER_API_KEY:
    os.environ["OPENROUTER_API_KEY"] = config.OPENROUTER_API_KEY

def call_model(model_name: str, messages: list, temperature: float = 0.0, max_tokens: int = 2000, response_format = None) -> dict:
    """
    Unified API call wrapper using LiteLLM.
    Returns:
        dict: {
            "content": str,
            "prompt_tokens": int,
            "completion_tokens": int,
            "duration": float,
            "status": "success" | "error",
            "error_msg": str
        }
    """
    # Map friendly model names to LiteLLM names if needed
    full_model_name = config.SUPPORTED_MODELS.get(model_name, model_name)
    
    # Configure custom parameters for specific providers if needed
    kwargs = {}
    if response_format:
        kwargs["response_format"] = response_format

    start_time = time.time()
    try:
        logger.info(f"Calling model {full_model_name}...")
        response = litellm.completion(
            model=full_model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        duration = time.time() - start_time
        
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        
        return {
            "content": content,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "duration": duration,
            "status": "success",
            "error_msg": ""
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error calling {full_model_name}: {str(e)}")
        return {
            "content": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "duration": duration,
            "status": "error",
            "error_msg": str(e)
        }
