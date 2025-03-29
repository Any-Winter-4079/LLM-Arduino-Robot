from config.v3.config import MODEL_TEMPLATE, STOP
from utils.v3.utils import run_llm, extract_and_format_value

# Function to run 0-shot prompting
def run_zero_shot(question, exemplars, cpp=False, iteration=0):
    """
    Run zero-shot prompting for direct mathematical problem solving.
    
    Constructs a minimal prompt without explicit reasoning guidance,
    runs inference, and extracts the final numerical answer.
    
    Args:
        question: The mathematical problem to solve
        exemplars: Minimal context or instructions for the model
        cpp: Whether to use C++ implementation (True) or Python (False)
        iteration: Current iteration number for seed management
        
    Returns:
        Tuple of (full prompt, model response, extracted numerical answer)
    """
    user_end = MODEL_TEMPLATE["user_end"]
    assistant_start = MODEL_TEMPLATE["assistant_start"]
    message = f"{exemplars}{question}{user_end}\n{assistant_start}"
    prediction = run_llm(message, STOP, cpp=cpp, iteration=iteration)
    concise_prediction = prediction.split("The answer is ")[-1].strip()
    concise_prediction = extract_and_format_value(concise_prediction)
    prediction = f"{prediction}\n#### {concise_prediction}"
    print("\t0Shot:", concise_prediction)
    return message, prediction, concise_prediction