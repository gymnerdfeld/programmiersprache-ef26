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
