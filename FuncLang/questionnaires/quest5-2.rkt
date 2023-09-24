#lang racket

(define (tree-left tree) (vector-ref tree 1))
(define (tree-right tree) (vector-ref tree 2))
(define (empty-tree? t) (equal? t #()))
(define (task-5 tree h)
(call/cc (lambda (cc-exit)
    (let loop ((tree tree) (h h)) 
        (cond 
            ((= h 0) (if (empty-tree? tree) #t (cc-exit #f)))
            ((= h 1) (if (and (not (empty-tree? tree) (empty-tree? (tree-left tree)) (empty-tree? (tree-right tree)))) #t (cc-exit #f)))
            ((> h 1) 
                (cond 
                    ((empty-tree? tree) (cc-exit #f))
                    ((not (loop (tree-left tree) (- h 2))))
                )
            )
        
        )
)

    (cond ((and (empty-tree? tree) (= h 0)) #t)
        ((and (empty-tree? tree) (not (= h 0))) #f)
        (else (and (task-4 (tree-left tree) (- h 2)) (task-4 (tree-right tree) (- h 1))))
  )
)