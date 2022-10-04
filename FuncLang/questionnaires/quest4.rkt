#lang racket

(define (tree-left tree) (vector-ref tree 1))
(define (tree-right tree) (vector-ref tree 2))
(define (empty-tree? t) (equal? t #()))
(define (task-4 tree h)
    (cond 
        ((and (empty-tree? tree) (= h 0)) #t)
        ((and (empty-tree? tree) (not (= h 0))) #f)
        ((and (empty-tree? (tree-left tree)) (empty-tree? (tree-right tree)) (= h 1)) #t)
        (else (and (task-4 (tree-left tree) (- h 2)) (task-4 (tree-right tree) (- h 1))))
    )
)
