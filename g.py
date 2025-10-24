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


builtins = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": div,
    "sin": math.sin,
    "cos": math.cos,
    "pi": 3.1415926535897932384626433832795,
    "e": math.e,
    "tau": math.tau,
}

#####################
# Phase 3: Evaluate #
#####################
def evaluate(expr):
    match expr:
        # Simple values
        case int(number) | float(number):
            return number
        case str(name):
            return builtins[name]
        
        # Special cases
        case ["function", ]:    # Fuktionsdefinition
            ...

        case ["sto", name, value]:     # Variable abspeichern
            value = evaluate(value)
            builtins[name] = value
            return value
        
        # Function call
        case [operator, *args]:        # Funktionsaufruf
            func = evaluate(operator)
            evaluated_args = [evaluate(arg) for arg in args]  # List comprehension
            # Unterscheidung eingebaute vs. Funktion in g
            match func:
                case []:  # Funktion in g
                    ...
                case callable(func):  # Eingebaute Funktion in Python
                    return func(*evaluated_args)
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
    print(f"Tokens: {tokens}")
    syntax_tree = parse(tokens)
    print(f"Syntax Tree: {syntax_tree}")
    result = evaluate(syntax_tree)
    print(f"Result: {result}")
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

def repl():
    print("Welcome to the g programming language. Enter 'q' to exit.")

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
