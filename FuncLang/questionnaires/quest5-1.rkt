#lang racket

(define make-tree vector)
(define (tree-data tree) (vector-ref tree 0))
(define (tree-left tree) (vector-ref tree 1))
(define (tree-right tree) (vector-ref tree 2))
(define (empty-tree? t) (equal? t #()))

(define (print-tree-by-level-asc tree)
    (make-tree (
                foldl (lambda (x lst)
                    (if (not (empty-tree? (tree-left x))) (vector-append (tree-left x) ( lst)) (void))
                    ;(if (not (empty-tree? (tree-right x))) (cons (list (tree-right x)) lst) (void))
                )
                '()
                (list tree)
                )
    )
    #|
    (let bfs((queue tree))
        (if (not (null? queue)) (
            (map 
                (lambda (x) (write (tree-data x)))
                (list queue)
            )  
            (bfs (make-tree (
                foldl (lambda (x lst)
                    (if (not (empty-tree? (tree-left x))) (cons x lst) (void))
                    (if (not (empty-tree? (tree-right x))) (cons x lst) (void))
                )
                '()
                (list queue)
                )
            ))  
        )
        (void)
        )
    )
    |#
)

(print-tree-by-level-asc #(10 #(21 #(31 #() #()) #()) #(22 #(33 #() #()) #(34 #() #())))) 