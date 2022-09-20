#lang racket
(define (task-03 lst)
    (sqrt
        (foldl + 0 
            (map 
                (lambda (z) (* z z))
                    (map
                        (lambda (x) (/ (foldl + 0 x) (length x)))
                        lst
                    )
            )
        )
    )
)

(task-03 (list (list 2 4 0) (list 2 2) (list 1 1 1 1 1 1 1)))