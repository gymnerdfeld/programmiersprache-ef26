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
        if token[0] in "0123456789-" and token != "-":
            if "." in token:
                return float(token)
            else:
                return int(token)
        else:
            return token

import math


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
    #return math.prod(args)

def div(a, b):
    return a / b

def block(*values):
    return values[-1]

builtins = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": div,
    "sin": math.sin,
    "block": block,
}

from pathlib import Path
library_file = Path(__file__).parent / "library.scm"
library = library_file.read_text()

# The function call stack
stack = [builtins]

#####################
# Phase 3: Evaluate #
#####################
def evaluate(expr):
    match expr:
        # Simple values
        case int(number) | float(number):
            return number
        case str(name):    # Lookup names
            # Local variables
            local_variables = stack[-1]
            if name in local_variables:
                return local_variables[name]
            elif name in builtins:
                return builtins[name]
            else:
                raise NameError(f"Variable '{name}' does not exist")
        
        # Special cases
        case ["function", params, body]:    # Fuktionsdefinition
            return ["function", params, body]

        case ["sto", name, value]:     # Variable abspeichern
            value = evaluate(value)
            local_variables = stack[-1]  # Top of the stack
            local_variables[name] = value
            return value
        
        # Function call
        case [operator, *args]:        # Funktionsaufruf
            func = evaluate(operator)
            evaluated_args = [evaluate(arg) for arg in args]  # List comprehension
            # Unterscheidung eingebaute vs. Funktion in g
            match func:
                case ["function", params, body]:  # Funktion in g
                    local_variables = {}
                    stack.append(local_variables)
                    for name, value in zip(params, evaluated_args):
                        local_variables[name] = value
                    result = evaluate(body)
                    stack.pop()
                    return result
                case _ if callable(func):  # Eingebaute Funktion in Python
                    return func(*evaluated_args)
                case _:
                    raise ValueError(f"Not a function: {func}")
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
        else:
            try:
                result = run(expr)
                print(result)
            except Exception as e:
                print(f"{e.__class__.__name__}: {str(e)}")        

if __name__ == "__main__":
    tests()
    repl()
