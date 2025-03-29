from config.v3.config import MODEL_TEMPLATE, STOP
from utils.v3.utils import run_llm, extract_and_format_value

def run_decider(question, exemplars):
    """
    Run the Decider method to select the best answer from multiple candidates.
    
    Constructs a template-based prompt, runs inference, and extracts the final decision.
    
    Args:
        question: The question with candidate answers to decide between
        exemplars: Examples guiding the decision-making process
        
    Returns:
        Tuple of (full prompt, detailed reasoning with decision, extracted answer)
    """
    user_end = MODEL_TEMPLATE["user_end"]
    assistant_start = MODEL_TEMPLATE["assistant_start"]
    message = f"{exemplars}{question}{user_end}\n{assistant_start}"
    prediction = run_llm(message, STOP)
    concise_prediction = prediction.split("The answer is ")[-1].strip()
    concise_prediction = extract_and_format_value(concise_prediction)
    print("\tDecider:", concise_prediction)
    return message, prediction, concise_prediction