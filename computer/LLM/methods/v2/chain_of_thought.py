from utils.v2.utils import run_llm, extract_and_format_value

def run_cot(question, exemplars, cpp=False):
    """
    Run the Chain of Thought (CoT) reasoning method on a question.
    
    Uses exemplars to guide the model in producing step-by-step reasoning before
    arriving at a final answer. Automatically extracts the numerical answer from
    the generated reasoning chain.
    
    Args:
        question: The mathematical problem to solve
        exemplars: CoT examples to guide the model's reasoning process
        cpp: Whether to use C++ implementation (True) or Python (False)
        
    Returns:
        Dictionary containing the prompt message, full reasoning predictions,
        and extracted concise numerical answers
    """
    message = f"{exemplars}\nQ: {question}\nA: "
    predictions = run_llm(message, ["Q:"], cpp=cpp)
    augmented_predictions = []
    concise_predictions = []
    for prediction in predictions:
        predicted_answer = prediction.split("The answer is ")[-1].strip()
        predicted_answer = extract_and_format_value(predicted_answer)
        augmented_predictions.append(prediction)
        concise_predictions.append(predicted_answer)
        print("\tCoT:", predicted_answer)
    return {
        "message": message,
        "predictions": predictions,
        "concise_predictions": concise_predictions
    }