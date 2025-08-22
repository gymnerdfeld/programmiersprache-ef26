#   __ _      //            The g programming language.
#  / _` |    (oo)           Inspired by lispy
# | (_| |     \/------\     (https://www.norvig.com/lispy.html)
#  \__, |      ||     ||
#  |___/       ||     ||    For an interactive interpreter run:
#              ||     ||    $ python g.py
#
# For details see https://github.com/gymnerdfeld/programmiersprache-ef26

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
    ...


###########
# Helpers #
###########
def run(source_code):
    tokens = tokenize(source_code)
    # print(f"Tokens: {tokens}")
    syntax_tree = parse(tokens)
    # print(f"Syntax Tree: {syntax_tree}")
    result = evaluate(syntax_tree)
    # print(f"Result: {result}")
    return result

def tests():
    ...

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
