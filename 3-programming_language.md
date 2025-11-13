# 3 Programmiersprache

## 3.1 Funktionen, erste Version

Jetzt wollen wir unseren "Rechner" zu einem programmierbaren Rechner erweitern. Wir wollen also eigene Funktionen in unserer eigenen Sprache schreiben, welche wir danach aufrufen können. In der ersten Version werden unsere Funktionen noch nicht ganz so funktionieren, wie wir das von den bekannten Programmiersprachen her gewohnt sind.

Bevor wir loslegen können, müssen wir uns Gedanken zur Syntax machen. Mit `sto` haben wir bereits einen Weg gefunden, um etwas unter einem Namen abzuspeichern. Wir brauchen also zusätzlich noch einen Weg, wie wir eine Funktion mit ihren Parametern definieren könne. Dazu betrachten wir zuerst die Definition und das Ausführen von Funktionen in Python, um uns danach für unsere eigene Syntax zu entscheiden.

![](funktionen.png)

Als Schlüsselwort verwenden wir `function`, gefolgt von der Liste mit den Parametern und zuletzt dem Body der Funktion, also dem eigentlichen Code der ausgeführt werden soll.

Ein weiteres Beispiel könnte so aussehen:

```scheme
(sto square        ; <- Unter dem Namen `square` abspeichern
    (function (x)      ; <- Definition einer Funktion (ohne Namen) mit einem Parameter mit dem Namen `x`
        (* x x)    ; <- Body der Funktion
    )
)

(square 5)         ; <- Die oben definierte Funktion ausführen, mit 5 als Argument
```

Denselben Code auf jeweils einer Zeile:

```scheme
(sto square (function (x) (* x x)))
(square 5)
```

Der Code einer Funktion wird bei der Definition nicht ausgeführt, sondern abgespeichert. Darum muss die Definition einer Funktion mit `function` ist ein Spezialkonstrukt unserer Sprache sein. Der Code dazu ist sehr einfach. Wir können einfach die Liste mit den Namen der Parameter und den Body der Funktion unverändert zurück geben. Der _Body_ der Funktion ist der Code, welcher ausgeführt werden soll, wenn die Funktion aufgerufen wird.

```py
def evaluate(expr):
    match expr:
        ...
        # Spezialkonstrukte
            ...
        case ["function", params, body]:
            return ["function", params, body]
```

Beim Ausführen der Funktion wird es etwas komplizierter. Am Anfang bleibt alles wie gehabt. Wir holen die Funktion aus den `builtins` und evaluieren alle Argumente. Danach müssen wir unterscheiden, um was für eine Funktion es sich handelt:

- Eine Funktion, welche in unserer Sprache geschrieben wurde
- Eine in Python geschriebene _eingebaute Funktion_

Unsere eigenen Funktionen sind Listen aus dem Schlüsselwort `function`, den Namen der Parameter und dem Body der Funktion. Alles andere ist dann (hoffentlich) eine in Python geschriebene Funktion:

```py
def evaluate(expr):
    match expr:
        ...
        # Function call
        case [operator, *args]:
            func = evaluate(operator)

            evaluated_args = [evaluate(arg) for arg in args]

            match func:
                # "Eigene" Funktion
                case ["function", params, body]:
                    for name, value in zip(params, evaluated_args):
                        builtins[name] = value
                    return evaluate(body)

                # Python Funktion
                case _ if callable(func):
                    return func(*evaluated_args)
```

Bei den eingebauten Python-Funktionen ganz unten ist alles wie bisher: Direkt aufrufen.

Bei unseren "eigenen" Funktionen sind zwei Schritte nötig:

1. Die übergebenen Werte (Argumente) müssen unter den in der Funktionsdefinition angegebenen Parameternamen abgespeichert werden.
2. Der Body wird evaluiert und das erhaltene Resultat zurück gegeben.

_Bemerkung:_ Bei den beiden Begriffe Parameter und Argumente einer Funktion droht Verwechslungsgefahr. Als Parameter bezeichnet man die Liste von Namen bei der _Definition_ einer Funktion. Die konkreten Werte, welche dann beim _Aufruf_ einer Funktion übergeben werden, nennt man hingegen Argumente. Sie zu verwechseln ist aber oft nicht weiter schlimm, denn meistens ist trotzdem klar, was gemeint ist. In der Python-Welt werden diese beiden Begriffe aber ziemlich konsistent wie beschrieben verwendet.

## 3.2 Funktionen mit lokalen Variablen

<!-- Leakt Variablen

Beispiel, dass nicht funktioniert:
```scheme
(sto incr (function (a) (+ a 1)))
(sto a 10)
(sto b 1)
(+ (incr b) a)
```
Gibt 3 anstatt 12. -->

Mit obigen Version gibt es jedoch ein unschönes Problem:

```scheme
> (sto square (function (x) (* x x)))
[ ... ]
> (square 5)
25
> x
5
```

Nach dem Aufruf der Funktion `square` existiert plötzlich die Variable `x`. Eventuell wurde durch den Aufruf von `square` eine bereits existierende Variable `x` überschrieben. Dies weil es nur einen einzigen Ort gibt, an dem Variablen abgespeichert werden können: `everything`.

Die Erwartung ist aber, dass Variablen einer Funktion nur innerhalb dieser Funktion existieren. So ist es zum Beispiel in Python:

```py
>>> def square(x):
...     return x * x
...
>>> square(5)
25
>>> x
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'x' is not defined
```

Bei jedem Aufruf einer Funktion wollen wir also einen neuen Ort erstellen, an welchem die lokalen Variablen gespeichert werden können. Wir nennen diesen Ort _lokalen Scope_. Nach der Ausführen der Funktion brauchen wir die erstellten lokalen Variablen nicht mehr. Es ist wie ein frisches Blatt Papier, auf welchem wir die Variablen der Funktion notieren. Am Ende der Funktionsausführung zerknüllen wir das Papier, und schmeissen es weg.

Den neuen `dict` für die lokalen Variablen erstellen wir in einer Liste. Zuhinterst in dieser Liste kommen die lokalen Variablen, und weiter vorne kommen die globalen Variablen und eingebaute Funktionen. Wenn wir den Wert für einen Namen suchen, gehen wir diese Liste von hinten nach vorne durch, und schauen, ob in den jeweiligen `dicts` etwas unter dem Namen abgespeichert ist. Diese ganze Liste mit `dicts` nennen wir _Stack_. Also Stapel, weil er wächst und schrumpft wie ein Stapel Papier auf unserem Pult.

Wir müssen unseren Code dazu an einigen Stellen umbauen.

Zuerst kreieren wir den Stack, in welchem wir die lokalen Variablen der Funktionsaufrufe abspeichern. Ganz am Anfang des Stacks befinden sich die eingebauten Funktionen von `builtins`, als zweites der Dict mit den globalen Variablen, welcher initial leer ist:

```py
stack = [builtins]
```

Beim Nachschlagen einer Variable schauen wir zuerst im Scope zuoberst auf dem Stack, also bei den lokalen Variablen. Als zweites suchen wir die Variable in den `builtins`, also den globalen Variablen. Wenn sich die Variable nirgends wo finden lässt, geben wir eine entsprechende Fehlermeldung aus:

```py
def evaluate(expr):
    match expr:
        ...
        case str(name):
            local_variables = stack[-1]    # Top of the stack
            if name in local_variables:
                return local_variables[name]
            elif name in builtins:
                return builtins[name]
            else:
                raise NameError(f"Variable '{name}' does not exist")
        case ["sto", name, value]:         # Einen Wert unter einem Namen abspeichern
            value = evaluate(value)
            scope = stack[-1]
            scope[name] = value
            return value
```

Auch das Abspeichern mit `sto` ändert sich leicht. Wir speichern eine Variable immer im lokalen Scope, also im Scope zuoberst auf dem Stack ab.

Jetzt kommen wir zum wichtigsten Teil unserer Änderungen, dem Aufruf von Funktionen. Und zwar folgendermassen:

```py
def evaluate(expr):
    match expr:
        ...
        # Funktionen aufrufen
        case [operator, *args]:
            evaluated_args = []
            func = evaluate(operator)

            evaluated_args = [evaluate(arg) for arg in args]

            # Unterscheide Funktion in Python oder Schemepy
            match func:
                case ["function", params, body]:  # Schemepy Funktion
                    # 1. Neuer Scope für lokale Variablen erstellen
                    local_variables = {}
                    stack.append(local_variables)

                    # 2. Parameter abspeichern (in neuem Scope)
                    for name, value in zip(params, evaluated_args):
                        local_variables[name] = value

                    # 3. Funktion ausführen
                    result = evaluate(body)

                    # 4. Lokaler Scope nach dem Funktionsaufruf wieder löschen
                    stack.pop()

                    # 5. Resultat zurück geben
                    return result
                case _ if callable(func):  # In Python geschriebene Funktion
                    return func(*evaluated_args)
```

Treffen wir nun auf eine Funktion, welche in unserer eigenen Programmiersprache geschrieben wurde, erstellen wir ein neues `dict` für die lokalen Variablen, und speichern dort die Werte (Argumente) unter den Korrekten Namen (Parameternamen) ab.

Mit dem neuen `dict` namens `local_variables` als letzter Eintrag auf dem Stack führen wir jetzt den Body der Funktion aus. Danach müssen wir wieder aufräumen und das Resultat zurück geben.

## 3.3 Funktionen nutzen (Blöcke und Library)

In unserer Konsole können wir schrittweise Rechnungen ausführen, dabei Zwischenresultate unter eigenen Namen abspeichern. Innerhalb von Funktionen ist das momentan noch nicht möglich, da der Body einer Funktion nur einen einzige Anweisung sein kann. Anstatt die Definition von Funktionen anzupassen, führen wir eine neue `block`-Anweisung ein, welche wir dann an ganz verschiedenen Orten einsetzen können.

Alle Anweisung innerhalb einer `block`-Anweisung werden der Reihe nach ausgeführt, und am Ende das Resultat der letzten Anweisung zurück gegeben. Zum Beispiel die folgende Rechnung:

```scheme
(block
    (sto a 4)
    (sto b 3)
    (sto c2 (+ (* a a) (* b b)))
    (sqrt c2)
)
```

Den `block` können wir als Spezialkonstrukt implementieren:
```py
def evaluate(expr, env=global_env):
    match expr:
        ...

        # Spezialkonstrukte
        ...
        case ["block", *statements, last]:
            for statement in statements:
                evaluate(statement, env)
            return evaluate(last, env)
```

Aber da bei uns die Argumente eines Funktionsaufrufs immer der Reihe nach ausgewertet werden, können wir den `block` auch ganz einfach als eingebaute Funktion implementieren:

```py
def block(*values):
    return values[-1]

...

builtins = {
    ...

    # Block: Execute multiple statements in order and return last value
    "block": block,
}
```

Und wir wollen unsere neue `block`-Anweisung anwenden. Unserer Programmiersprache unterstützt nun Funktionen, und so können wir häufig gebrauchte Funktionen auch in unserer eigenen Programmiersprache schreiben, und müssen dabei nur noch in Ausnahmefällen auf Python zurück greifen. Diese Funktionen (und auch Definitionen von Konstanten) sammeln wir dann in der Standardbibliothek (engl. _standard library_ oder kurz _library_):
```py
library = """
(block
    (sto e 2.718281828459045)
    (sto pi 3.141592653589793)
    (sto sqrt (function (x) (** x 0.5)))
    (sto > (function (a b) (< b a)))
)
"""
```

Damit wir diese Funktionen in unseren Programmen auch verwenden können, müssen wir die `library` beim Starten unseres Interpreters laden, also ausführen:
```py
def repl():
    print("Welcome to the g programming language. Enter 'q' to exit.")

    run(library)

    done = False
    while not done:
        ...
```

Wenn wir jetzt noch die Library in eine separate Datei auslagern, können wir vom Syntax-Highlighting unseres Editors profitieren.
```py
from pathlib import Path
library_file = Path(__file__).parent / "library.scm"
library = library_file.read_text()
```

Die Datei mit dem Library-Code heisst `library.scm`:
```scheme
(block
    ; Constants
    (sto pi 3.1415926535897932384626433832795)
    (sto tau (* pi 2))
    (sto e 2.7182818284590452353602874713527)

    ; Cosine
    (sto cos (function (x) 
        (sin (+ x (/ pi 2)))
    ))

    ; Absolute value (Betrag)
    (sto abs (function (x)
        (if (< x 0) (- 0 x) x)
    ))

    ; Factorial (Fakultät): recursive definition
    (sto fact (function (n)
        (if (== n 0)
            1
            (* n (fact (- n 1)))
        )
    ))
)
```
