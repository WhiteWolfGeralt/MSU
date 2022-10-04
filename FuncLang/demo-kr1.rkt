#lang racket

(define (taskI lst)
    (let loop ((cur-min +inf.0) (counter 0) (lst lst) (result '()))
        (cond 
            ((null? lst) result) ;return value
            ((< (car lst) cur-min) (loop (car lst) (+ counter 1) (cdr lst) (list counter))) ;if find new minimum
            ((= (car lst) cur-min) (loop cur-min (+ counter 1) (cdr lst) (cons counter result))) ;if current number equals to minimum
            (else (loop cur-min (+ counter 1) (cdr lst) result)) ;if current number greater than minimum
        )
    )
)
#|
(taskI (list -1 0 -2 3 -2 -1 0 -3 -2 -3 -1)) ;correct: (9 7)
(taskI (list -1 0 1 -1 0 1 -1))
(taskI (list 832183))
(taskI '())
|#

(define (taskII t s)
    (foldl 
        (lambda (x val) 
            (if (number? x) (+ (* x (/ s 4)) val)
                (+ val (taskII x (/ s 4)))
            )
        )
        0
        (vector->list t)
    )
)
;(taskII #(1 0 0 #(1 1 1 0)) 16)


(define (taskIII t)
    (call/cc (lambda (cc-exit)
        (let loop ((t t) (cost 4) (total 0))
            (cond 
                ((> total 4) (cc-exit #t))
                (loop t total)
            )
        )
    ))
)

;(taskIII #(1 1 0 #(1 1 1 0))) ;#t
;(taskIII #(0 0 0 #(1 0 1 1))) ;#f

(define taskV (lambda args 
    (lambda (input)
        (let loop ((lst (reverse args)) (res input))
            (if (null? lst) res
                (loop (cdr lst) ((car lst) res))
            )
        )
    )
))

((taskV (lambda (x) (* 2 x)) (lambda (x) (+ 1 x)) (lambda (x) (* 3 x))) 10)


(define a (list (list 1 2) (cons (cons 3 4) 5)))
(define b (list (cdr a) (car a) 1))
(define c (cons (cdr b) b))
(writeln a)
(writeln b)
(writeln c)