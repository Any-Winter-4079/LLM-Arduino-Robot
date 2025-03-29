from config.v3.config import MODEL_TEMPLATE, STOP
from utils.v3.utils import run_llm, extract_and_format_value

def run_cot(question, exemplars, cpp=False, iteration=0):
    """
    Run the Chain of Thought (CoT) reasoning method on a question.
    
    Constructs a prompt using model-specific templates, runs inference with the LLM,
    and extracts the final numerical answer from the generated reasoning chain.
    
    Args:
        question: The mathematical problem to solve
        exemplars: CoT examples to guide the model's reasoning process
        cpp: Whether to use C++ implementation (True) or Python (False)
        iteration: Current iteration number for seed management
        
    Returns:
        Tuple of (full prompt, detailed reasoning with answer, extracted numerical answer)
    """
    user_end = MODEL_TEMPLATE["user_end"]
    assistant_start = MODEL_TEMPLATE["assistant_start"]
    message = f"{exemplars}{question}{user_end}\n{assistant_start}"
    prediction = run_llm(message, STOP, cpp=cpp, iteration=iteration)
    concise_prediction = prediction.split("The answer is ")[-1].strip()
    concise_prediction = extract_and_format_value(concise_prediction)
    prediction = f"{prediction}\n#### {concise_prediction}"
    print("\tCoT:", concise_prediction)
    return message, prediction, concise_prediction