#lang racket
(define (opposite? x1 y1 z1 x2 y2 z2)
  (if (= -1 (/ (scalarProduct x1 y1 z1 x2 y2 z2) (moduleProduct x1 y1 z1 x2 y2 z2))) #t #f))

(define (scalarProduct x1 y1 z1 x2 y2 z2)
  (+ (* x1 x2) (* y1 y2) (* z1 z2)))

(define (moduleProduct x1 y1 z1 x2 y2 z2)
  (sqrt (* (+ (* x1 x1) (* y1 y1) (* z1 z1)) (+ (* x2 x2) (* y2 y2) (* z2 z2)))))

(opposite? 1 1 1 2 2 2)
(opposite? 2 3 4 1 2 3)
(opposite? 1 0 1 -2 0 -2)
(opposite? 1 1 1 -2 -2 -2)
(opposite? 0 0 345 0 0 -345)
(opposite? 0 -1 87 0 0 -87)
