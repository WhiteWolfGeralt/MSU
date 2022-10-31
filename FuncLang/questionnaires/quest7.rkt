;Это невозможно реализовать функцией, поскольку аргументы функции вычисляются при вызове функции и в 
;функции будут изменяться локальные переменные. Поэтому возможна реализация только макросом.

#lang racket

(define-syntax swap
  (syntax-rules ()
    ((swap a b)
      (let ((c b))
        (set! b a)
        (set! a c)
      )
    )
  )
)

(define-syntax left-rot!
  (syntax-rules ()
    ((left-rot!) (void))
    ((left-rot! m1) m1)
    ((left-rot! m1 m2) (swap m1 m2))
    ((left-rot! m1 m2 m3 ...)
      (begin
        (swap m1 m2)
        (left-rot! m2 m3 ...)
      )
    )
  )
) 

(let ( (a 3) (b 2) (c 1)) 
  (begin
    (left-rot! a b c ) 
    (/ a b c)
  )
)
