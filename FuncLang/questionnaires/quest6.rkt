#lang racket

(define (make-queue) 
	(mcons 'queue '(mcons '() '()))
	()
)

(define (queue? q) 
	(and (mpair? q) (eq? 'queue (mcar q)))
)

(define (empty-queue? q) 
	(and (queue? q) (null? (mcdr q)))
)

(define (insert-queue! q e)
	(if (queue? q) 
		(begin
			(set-mcdr! (mcdr (mcdr q)) (mcons e '()))

		;(set-mcdr! q (mcons (mcdr (mcdr q)) (mcons e '())))
		)
		q
	)
)

(define (delete-stack! s)
(if (and (queue? s) (not (empty-queue? s)))
(set-mcdr! s (mcdr
(mcdr s))) s))

(define (front-queue s) 
	(if (and (queue? s) (not (empty-queue? s)))
		(mcar (mcdr s))
		"empty stack"
	)
)

(define (main)
	(let ((a (make-queue)))
		(insert-queue! a 1)
		(write a)
	)
)

(main)
