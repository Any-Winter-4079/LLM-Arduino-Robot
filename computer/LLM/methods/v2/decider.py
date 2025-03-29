from utils.v2.utils import run_llm, extract_and_format_value

def run_decider(question, exemplars):
    """
    Run the Decider method to select the best answer from multiple candidates.
    
    Constructs a prompt with exemplars and the question, runs inference with
    special decider settings, and extracts the final answer choice.
    
    Args:
        question: The question with candidate answers to decide between
        exemplars: Examples guiding the decision-making process
        
    Returns:
        Dictionary containing the prompt message, full prediction,
        and extracted concise answer
    """
    message = f"{exemplars}\nQ: {question}\n\nA: "
    prediction = run_llm(message, ["Q:"], decider=True)[0]
    predicted_answer = prediction.split("The answer is ")[-1].strip()
    predicted_answer = extract_and_format_value(predicted_answer)
    print("\tDecider:", predicted_answer)
    return {
        "message": message,
        "prediction": prediction,
        "concise_prediction": predicted_answer
    }