#lang racket
(define (list-fib-squares-a n)
    (map (lambda (x) (* x x)) 
        (let loop ((i n) (fib-n-1 1) (fib-n-2 1) (result '()))
            (if (= i 0) (reverse result)
                ;else
                (loop (- i 1) (+ fib-n-1 fib-n-2) fib-n-1 (cons fib-n-2 result)))
        )
    )    
)

(define (list-fib-squares-b n) 
    (reverse (foldl (lambda (x lst) (cons (* x x) lst)) '()
        (let loop ((i n) (fib-n-1 1) (fib-n-2 1) (result '()))
            (if (= i 0) (reverse result)
                ;else
                (loop (- i 1) (+ fib-n-1 fib-n-2) fib-n-1 (cons fib-n-2 result)))
        )
    ))
)

(define (process lst)
    (let loop (
        (val (foldl * 1 (car lst))) 
        (inner-lst (cdr lst))
        (result '())
        )
        ;body
        (if (null? inner-lst) (reverse result)
            ;else
            (loop
                val 
                (cdr inner-lst)
                (if (> (foldl + 0 (car inner-lst)) val) (cons (car inner-lst) result)
                    ;else
                    result
                )
            )
        )
    )
)

(list-fib-squares-a 10)
(list-fib-squares-b 10)
(process '((5) (16) (1 -1) (1 2) () (3 4) (2 3) (2 3 4) (2 4 3)))