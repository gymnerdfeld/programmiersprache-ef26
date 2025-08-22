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

#####################
# Phase 3: Evaluate #
#####################
def evaluate(expr):
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
