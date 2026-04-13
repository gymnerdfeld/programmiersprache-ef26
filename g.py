#   .--./)     //            The g programming language.
#  /.''\\     (oo)
# | |  | |     \/            Inspired by lispy
#  \`-' /      ||            (https://www.norvig.com/lispy.html)
#  /("'`       ||
#  \ '---.     ||            For details see
#   /'""'.\     \------\     https://github.com/gymnerdfeld/programmiersprache-ef26
#  ||     ||    ||     ||
#  \'. __//     ||     ||    For an interactive interpreter run:
#   `'---'      ||     ||    $ python g.py

#####################
# Phase 1: Tokenize #
#####################
def tokenize(source_code):
    # Remove comments
    source_code = "\n".join(line.split(";")[0] for line in source_code.split("\n"))
    # Split code into tokens
    return source_code.replace("(", " ( ").replace(")", " ) ").split()

##################
# Phase 2: Parse #
##################
def parse(tokens):
    token = tokens.pop(0)
    if token == '(':
        lst = []
        while tokens[0] != ')':
            lst.append(parse(tokens))
        tokens.pop(0)
        return lst
    else:
        # Parse numbers
        if token[0] in "0123456789-" and token != "-":
            if "." in token:    # Decimal
                return float(token)
            else:               # Integer
                return int(token)
        else:
            return token



######################
# Built-in functions #
######################
def add(*args):
    result = 0
    for arg in args:
        result = result + arg
    return result

def sub(a, b):
    return a - b

def mul(*args):
    result = 1
    for arg in args:
        result = result * arg
    return result

def div(a, b):
    return a / b

def power(a, b):
    return a ** b

def eq(a, b):
    return a == b

def lt(a, b):
    return a < b

def block(*values):
    return values[-1]

import math

builtins = {
    # Math operators
    "+": add,
    "-": sub,
    "*": mul,
    "/": div,
    "**": power,
    "sin": math.sin,

    # Comparisons
    "==": eq,
    "<": lt,

    # Boolean values
    "True": True,
    "False": False,

    # Print
    "print": print,

    # Block: Execute multiple statements in order and return last value
    "block": block,
}

################
# Load library #
################
from pathlib import Path
library_file = Path(__file__).parent / "library.scm"
library = library_file.read_text()

#######################
# Function call stack #
#######################
stack = [builtins]

#####################
# Phase 3: Evaluate #
#####################
def evaluate(expr):
    match expr:
        # Simple values (numbers)
        case int(number) | float(number):
            return number
        # Names (look up in local or global scope)
        case str(name):
            local_variables = stack[-1]    # Top of the stack
            if name in local_variables:
                return local_variables[name]
            elif name in builtins:
                return builtins[name]
            else:
                raise NameError(f"Variable '{name}' does not exist")
        
        # ###############
        # Special cases #
        # ###############

        # Function definition
        case ["function", params, body]:
            if len(stack) > 1:
                return ["function", params, body, stack[-1]]   # Funktion mit den lokale Variablen
            else:
                return ["function", params, body, {}]

        # Store value under a given name
        case ["sto", name, value]:
            value = evaluate(value)
            local_variables = stack[-1]     # Top of the stack
            local_variables[name] = value
            return value
        
        # if: Conditional execution
        case ["if", condition, body_true, body_false]:
            if evaluate(condition):
                # body_false nicht evaluieren!
                return evaluate(body_true)
            else:
                # body_true nicht evaluieren!
                return evaluate(body_false)

        # Function call
        case [operator, *args]:
            func = evaluate(operator)
            # Evaluate all arguments first
            evaluated_args = [evaluate(arg) for arg in args]

            match func:
                # Function written in g
                case ["function", params, body, closure_variables]:
                    # Create new scope for local variables
                    local_variables = closure_variables.copy()
                    # Push new scope to the top of the stack
                    stack.append(local_variables)
                    # Store all arguments under correct name in new local scope
                    for name, value in zip(params, evaluated_args):
                        local_variables[name] = value
                    # Evaluate the function code
                    result = evaluate(body)
                    # Discard local scope (not needed anymore)
                    stack.pop()
                    # Return calculated result
                    return result

                # Built-in function (written in Python)
                case _ if callable(func):
                    return func(*evaluated_args)

                # Not a function
                case _:
                    raise ValueError(f"Not a function: {func}")

        # Unknown expression: empty expression ()
        case _:
            raise ValueError("Unknown expression:", expr)
    if type(expr) == int:
        return expr
    elif type(expr) == list:
        operator, val1, val2 = expr
        if operator == "+":
            return val1 + val2


###########
# Helpers #
###########
def run(source_code):
    tokens = tokenize(source_code)
    #print(f"Tokens: {tokens}")
    syntax_tree = parse(tokens)
    #print(f"Syntax Tree: {syntax_tree}")
    result = evaluate(syntax_tree)
    #print(f"Result: {result}")
    return result

def tests():
    # 1
    assert run("1") == 1
    # 4.2
    assert run("4.2") == 4.2
    # 1 + 1
    assert run("(+ 1 1)") == 2
    # 3 - 1
    assert run("(- 3 1)") == 2
    # 2 * 3
    assert run("(* 2 3)") == 6
    # 3 / 2
    assert run("(/ 3 2)") == 1.5
    # 4 - 2*7
    assert run("(- 4 (* 2 7))") == -10
    # vararg plus
    assert run("(+ 1 2 3 4 5)") == 15

def repl():
    print("Welcome to the g programming language. Enter 'q' to exit.")

    run(library)

    done = False
    while not done:
        expr = input("> ")
        if expr.strip().lower() == "q":
            done = True
        elif expr.strip():
            try:
                result = run(expr)
                print(result)
            except Exception as e:
                print(f"{e.__class__.__name__}: {str(e)}")        

if __name__ == "__main__":
    tests()
    repl()
