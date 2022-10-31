#lang racket

(define (stream-scale s f)
  (stream-map (lambda (x) (* x f)) s)
)

(define (powers x)
  (stream-cons 1 (stream-scale (powers x) x))
)

(define (interleave str1 str2)
  (stream-cons (stream-first str1)
    (interleave str2 (stream-rest str1))
  )
)

(define (power-streams s1 s2)
  (if (< (stream-first s1) (stream-first s2))
    (stream-cons (stream-first s1) (power-streams (stream-rest s1) s2))
    (stream-cons (stream-first s2) (power-streams s1 (stream-rest s2)))
  )
)

(define power-stream
  (power-streams (stream-rest (powers 2)) (powers 3))
)

(define (print-stream s num)
  (let loop ((i 0))
    (if (< i num)
      (begin
        (writeln (stream-ref s i))
        (loop (+ i 1))
      )
      (void)
    )
  )
)

(print-stream power-stream 5)