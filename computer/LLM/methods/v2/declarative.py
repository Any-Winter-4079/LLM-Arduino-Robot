import re
import string
import numpy as np
from sympy import solve, sympify, Symbol
from utils.v2.utils import run_llm, extract_and_format_value
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

# (start of) Declarative -> https://github.com/joyheyueya/declarative-math-word-problem.git (adapted)
def simplify_variables(equations):
    """
    Simplify the variables longer than one character in the equations.
    
    Args:
        equations: String containing equation expressions
        
    Returns:
        Tuple of (simplified equations, variable mapping dictionary)
    """
    var_names = set(re.findall(r'\b[a-zA-Z_]\w*\b', equations))
    long_var_names = [var for var in var_names if len(var) > 1]
    unused_chars = [chr(i) for i in range(97, 123) if chr(i) not in var_names]  # a-z
    var_mapping = {var: unused_chars.pop(0) for var in long_var_names}
    
    for long_var, short_var in var_mapping.items():
        equations = re.sub(r'\b{}\b'.format(long_var), short_var, equations) 
    return equations, var_mapping

def clean_equation_text(equation_text):
    """
    Clean the equation text by removing unwanted characters.
    
    Args:
        equation_text: Raw equation text
        
    Returns:
        Cleaned equation text
    """
    cleaned_equation_text = re.sub(r'[^\w\s=+\-*/()0-9.\[\]]', '', equation_text)
    return cleaned_equation_text

def reformat_incre_equations(x):
    """
    Reformat incremental equations into a comma-separated string.
    
    Args:
        x: List of equation strings
        
    Returns:
        Reformatted equations
    """
    result = ''
    if len(x) >= 1:
        for eq in x:
            if len(result) == 0:
                result += eq[2 : -2]
            else:
                result += ', ' + eq[2 : -2]
    return result

def reformat_equations_from_peano(eq_list):
    """
    Reformat equations from Peano format to standard format.
    
    Args:
        eq_list: Comma-separated list of equations
        
    Returns:
        Reformatted equations
    """
    result = ''
    for eq in eq_list.split(','):
        if 'eq' in eq:
            if len(result) == 0:
                result += eq[eq.index('eq') + 2:]
            else:
                result += ', ' + eq[eq.index('eq') + 2:]
        elif 'answer' in eq:
            if len(result) == 0:
                result += eq[eq.index('answer') + 6:].strip() + ' = ?'
            else:
                result += ', ' + eq[eq.index('answer') + 6:].strip() + ' = ?'     
    return result

def get_declarative_equations(prediction):
    """
    Extract and format declarative equations from prediction text.
    
    Args:
        prediction: Text containing equation declarations in [[...]] format
        
    Returns:
        Reformatted equation list or original prediction if no equations found
    """
    eq_list = re.findall(r'\[\[.*?\]\]', prediction)
    
    cleaned_eq_list = []
    
    if len(eq_list) > 0:
        for eq in eq_list:
            cleaned_eq = clean_equation_text(eq)
            cleaned_eq_list.append(cleaned_eq)
        
        return reformat_equations_from_peano(reformat_incre_equations(cleaned_eq_list))
    else:
        return prediction

def get_final_using_sympy(equations):
    """
    Solve the system of equations using SymPy.
    
    Args:
        equations: String containing system of equations
        
    Returns:
        Solution value or error message
    """
    try:
        equations, _ = simplify_variables(equations)
        transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
        if str(equations) == 'nan':
            return np.nan
        equation_list = equations.split(',')
        for eq in equation_list:
            for c in range(len(eq)):
                if c < len(eq) - 2:
                    if eq[c].isalpha() and eq[c+1].isalpha() and eq[c+2].isalpha():
                        return 'invalid equations'

        goal_var = None
        goal_expression_list = []
            
        if equation_list[-1].split('=')[0].strip().isalpha() or len(equation_list[-1].split('=')[0].strip()) == 2:
            goal_var = equation_list[-1].split('=')[0].strip()
        elif '=' in equation_list[-1]:
            for l in list(string.ascii_lowercase) + list(string.ascii_uppercase):
                if l not in equation_list[-1]:
                    goal_var = l
                    break
            if goal_var is not None:
                goal_expression = goal_var + ' - (' + equation_list[-1].split('=')[0].strip() + ')'
                goal_expression = parse_expr(goal_expression, transformations=transformations)
                goal_expression = sympify(goal_expression)
                try:
                    return float(solve(goal_expression)[0])
                except Exception as e:
                    pass
                goal_expression_list.append(goal_expression)
            else:
                return 'invalid equations'

        if len(equation_list) == 1:
            try:
                goal_expression = parse_expr(equation_list[0].split('=')[0], transformations=transformations)
                return float(sympify(goal_expression))
            except Exception as e:
                return 'invalid equations'

        if goal_var == None:
            return 'no goal found'

        for i in range(len(equation_list) - 1):
            sub_eqs = equation_list[i]  
            if '?' not in sub_eqs:
                try:    
                    sub_eqs_split = sub_eqs.split('=')
                    sub_eqs = sub_eqs_split[0].strip() + ' - (' + sub_eqs_split[1].strip() + ')'
                    sub_eqs = parse_expr(sub_eqs, transformations=transformations)
                    sub_eqs = sympify(sub_eqs)
                except Exception as e:
                    return 'invalid equations'
                goal_expression_list.append(sub_eqs)

                try:
                    try:
                        return float(solve(goal_expression_list)[Symbol(goal_var)])
                    except Exception as e:
                        return float(solve(goal_expression_list)[0][Symbol(goal_var)])
                except Exception as e:
                    pass

        return 'no solution'
    except Exception as e:
        print(e)
        return 'bug'
# (end of) Declarative -> https://github.com/joyheyueya/declarative-math-word-problem.git (adapted)

def run_declarative(question, exemplars, cpp=False):
    """
    Run the Declarative method for mathematical problem solving.
    
    Constructs a prompt with exemplars and question, runs inference with the LLM,
    extracts equations from the generated output, and solves them symbolically.
    
    Args:
        question: The mathematical problem to solve
        exemplars: Examples guiding the declarative equation formulation
        cpp: Whether to use C++ implementation (True) or Python (False)
        
    Returns:
        Dictionary containing the prompt message, full predictions with solutions,
        and extracted concise numerical answers
    """
    message = f"{exemplars}\nQ: {question}\nA: "
    predictions = run_llm(message, ["Q:"], cpp=cpp)
    augmented_predictions = []
    concise_predictions = []
    for prediction in predictions:
        eq_list = get_declarative_equations(prediction)
        # print(f"\tDecl: {eq_list}")
        predicted_answer = get_final_using_sympy(eq_list)
        if predicted_answer in ["invalid equations", "no goal found", "no solution", "bug"]:
            concise_prediction = "bug"
        else:
            concise_prediction = extract_and_format_value(predicted_answer)
        concise_predictions.append(concise_prediction)
        print("\tDecl:", concise_prediction)
        prediction = f"{prediction}\n#### {concise_prediction}"
        augmented_predictions.append(prediction)

    return {
        "message": message,
        "predictions": augmented_predictions,
        "concise_predictions": concise_predictions
    }