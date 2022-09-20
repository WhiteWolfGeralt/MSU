#lang racket
(define (iter-odd-fib-list n)
    (let loop ((i n) (prev 0) (curr 1) (result '()))
        (if (<= i 0) 
            (reverse result)
        ;else
        (loop
            (if (odd? curr) (- i 1) i)
            curr
            (+ prev curr)
            (if (odd? curr) (cons curr result) result)
        ))
    )
)

(define (rec-odd-fib-list n)
    (let loop ((i n) (prev 0) (curr 1) (result '()))
        (if (<= i 0) 
            (reverse result) 
        ;else 
        (if (odd? curr)
            (cons curr (loop (- i 1) curr (+ prev curr) result))
        ;else
        (loop i curr (+ prev curr) result))
    ))
)

(iter-odd-fib-list 100)
(rec-odd-fib-list 100)
