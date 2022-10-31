; заготовка "Доктора". Сентябрь 2022
#lang scheme/base
(require racket/vector)

; В учебных целях используется базовая версия Scheme

; основная функция, запускающая "Доктора"
; параметр name -- имя пациента
(define (visit-doctor name)
  (printf "Hello, ~a!\n" name)
  (print '(what seems to be the trouble?))
  (doctor-driver-loop-v2 name #())
)

(define (visit-doctor-v2 stop-word max-patients)
  (let loop ((name (ask-patient-name)) (count 1))
    (if (or (equal? name stop-word)) (println '(time to go home))
      (begin
        (visit-doctor name)
        (if (= count max-patients) (println '(time to go home))
          (loop (ask-patient-name) (+ count 1))
        )
      )
    ) 
  )
)

(define (ask-patient-name)
  (begin
    (println '(next!))
    (println '(who are you?))
    (print '**)
    (car (read))
  ) 
)

; цикл диалога Доктора с пациентом
; параметр name -- имя пациента
(define (doctor-driver-loop name)
  (newline)
  (print '**) ; доктор ждёт ввода реплики пациента, приглашением к которому является **
  (let ((user-response (read)))
    (cond 
      ((equal? user-response '(goodbye)) ; реплика '(goodbye) служит для выхода из цикла
        (printf "Goodbye, ~a!\n" name)
        (println '(see you next week))
      )
      (else 
        (print (reply user-response)) ; иначе Доктор генерирует ответ, печатает его и продолжает цикл
        (doctor-driver-loop name)
      )
    )
  )
)

; генерация ответной реплики по user-response -- реплике от пользователя 
(define (reply user-response history)
  (case (random (if (< 0 (vector-length history)) 0 1) (if (has-keyword user-response) 4 3)) ; с равной вероятностью выбирается один из трёх способов построения ответа
    ((0) (history-answer history))
    ((1) (hedge-answer))
    ((2) (qualifier-answer user-response))
    ((3) (keyword-answer user-response))
  )
)

(define (history-answer history)
  (append 
    '(earlier you said that) 
    (change-person (vector-ref history (random 0 (vector-length history))))
  )
)

; 1й способ генерации ответной реплики -- случайный выбор одной из заготовленных фраз, не связанных с репликой пользователя
(define (hedge-answer)
  (pick-random-vector 
    '#(
        (please go on)
        (many people have the same sorts of feelings)
        (many of my patients have told me the same thing)
        (please continue)
        (tell me more about this problem)
        (this is very important for some people)
        (please give me a minute... go on)
      )
    )
)

; случайный выбор одного из элементов непустого вектора
(define (pick-random-vector vctr)
  (vector-ref vctr (random 0 (vector-length vctr)))
)

; 2й способ генерации ответной реплики -- замена лица в реплике пользователя и приписывание к результату случайно выбранного нового начала
(define (qualifier-answer user-response)
  (append (pick-random-vector 
    '#(
        (you seem to think that)
        (you feel that)
        (why do you believe that)
        (why do you say that)
        (what you think about)
        (i think it very important that)
        (dont worry about)
      )
    )
    (change-person user-response)
  )
)

; замена лица во фразе
(define (change-person phrase)
  (many-replace-v3
  '((am are) (are am) (i you) (me you) (mine yours) (my your) (myself yourself) (you i)
    (your my) (yours mine) (yourself myself) (we you) (us you) (our your) (ours yours)
    (ourselves yourselves) (yourselves ourselves) (shall will))
  phrase)
 )

; осуществление всех замен в списке lst по ассоциативному списку replacement-pairs
(define (many-replace replacement-pairs lst)
  (cond ((null? lst) lst)
    (else (let ((pat-rep (assoc (car lst) replacement-pairs))) ; Доктор ищет первый элемент списка в ассоциативном списке замен
      (cons 
        (if pat-rep (cadr pat-rep) ; если поиск был удачен, то в начало ответа Доктор пишет замену
          (car lst) ; иначе в начале ответа помещается начало списка без изменений
        )
        (many-replace replacement-pairs (cdr lst)) ; рекурсивно производятся замены в хвосте списка
        )
      )
    )
  )
)

(define (many-replace-v2 map lst)
  (let loop ((remains lst) (result '()))
    (if (null? remains) (reverse result)
      (let ((pat-rep (assoc (car remains) map)))
        (loop 
          (cdr remains) 
          (if pat-rep (cons (cadr pat-rep) result)
            (cons (car remains) result) 
          )
        )    
      )
    )
  )  
)

(define (many-replace-v3 pairs lst)
  (map 
    (lambda (x)  
      (let ((pat-rep (assoc x pairs)))
        (if pat-rep (cadr pat-rep) x)   
      )
    )
    lst
  )  
)

; в Racket нет vector-foldl, реализуем для случая с одним вектором (vect-foldl f init vctr)
; у f три параметра i -- индекс текущего элемента, result -- текущий результат свёртки, elem -- текущий элемент вектора
(define (vector-foldl f init vctr)
  (let ((length (vector-length vctr)))
    (let loop ((i 0) (result init))
      (if (= i length) result
        (loop (add1 i) (f i result (vector-ref vctr i)))
      )
    )
  )  
)
	
; аналогично от конца вектора к началу
(define (vector-foldr f init vctr)
  (let ((length (vector-length vctr)))
    (let loop ((i (sub1 length)) (result init))
      (if (= i -1) result
        (loop (sub1 i) (f i result (vector-ref vctr i)))
      )
    )
  )
)

(define keywords-structure 
  '#(
    #( ; начало данных 1й группы
      #(depressed suicide exams university) ; список ключевых слов 1й группы
      #( ; список шаблонов для составления ответных реплик 1й группы 
        (when you feel depressed, go out for ice cream)
        (depression is a disease that can be treated)
        (i reccomending you watch TV for relax)
        (you must think less about *)
      )
    ) ; завершение данных 1й группы
    #( ; начало данных 2й группы ...
      #(mother father parents brother sister uncle aunt grandma grandpa)
      #(
        (tell me more about your * , i want to know all about your *)
        (why do you feel that way about your * ?)
        (your family is important. * is loving you)
        ()
      )
    )
    #(
      #(university scheme lections)
      #(
        (your education is important)
        (how much time do you spend on your studies ?)
        ()
        ()
      )
    )
    #(
      #(python ML DL torch)
      #(
        (this is really disgusting)
        (i hate machine learning and deep learning!!!!!)
        (compiliers are better than neural networks)
      )
    )
    #(
      #(MSU CMC VMK university education MechMath)
      #(
        (while the Moscow river will flow VMK will be better than MechMath)
        (i like OKi on VMK!!!)
        (do you like eat pizza on VMK?)
      )
    )
  )
)

(define (keyword-answer user-response)
  (let ((key (pick-random-word user-response)))
    (many-replace-v3 (list (list '* key)) (pick-random-vector (unioin-answers key)))
  )
)

(define (has-keyword user-response)
  (call/cc
    (lambda (cc-exit)    
      (let loop-user ((user-lst user-response))
        (if (null? user-lst) #f
          (begin
            (vector-foldl
              (lambda (i result el)
                (if (equal? (car user-lst)  el) (cc-exit #t) (void))
              )
              #()
              get-all-keywords
            )
            (loop-user (cdr user-lst))
          )
        )
      )     
    )
  )
)

(define (unioin-answers key)
  (vector-foldl
    (lambda (i res el)
      (if (vector-member key (vector-ref el 0)) 
        (vector-append res (vector-ref el 1))
        res
      )
    )
    #()
    keywords-structure
  )
)

(define (pick-random-word user-response)
  (let ((all-word (get-all-keywords-in-response user-response)))
    (vector-ref all-word (random 0 (vector-length all-word)))
  )
)

(define (get-all-keywords-in-response user-response)
  (let loop-user ((user-lst user-response) (res #()))
    (if (null? user-lst) res
      (loop-user
        (cdr user-lst) 
        (vector-append res
          (vector-foldl
            (lambda (i result el)
              (if (equal? (car user-lst) el) 
                (vector-append result (vector el))
                result
              )
            )
            #()
            get-all-keywords
          )
        )
      )
    )
  )
)

(define get-all-keywords
  (vector-foldl
    (lambda (i res el) (vector-append res (vector-ref el 0)))
    #()
    keywords-structure
  )
)

(define strategy-storage
  (vector 
    (vector 
      (lambda (_1 history) (if (< 0 (vector-length history)) #t #f))
      1
      (lambda (_1 history) (history-answer history))
    )
    (vector
      (lambda (_1 _2) #t)
      3
      (lambda (_1 _2) (hedge-answer))
    )
    (vector
      (lambda (_1 _2) #t)
      5
      (lambda (user-response _2) (qualifier-answer user-response))
    )
    (vector
      (lambda (user-response _2) (if (has-keyword user-response) #t #f))
      10
      (lambda (user-response _2) (keyword-answer user-response))
    )
  )
)

(define (get-strategy user-response history)
  (vector-filter
    (lambda (el) ((vector-ref el 0) user-response history))
    strategy-storage
  )
)

(define (count-sum all-strategies)
  (vector-foldl
    (lambda (i res el)
      (+ res (vector-ref el 1))
    )
    1
    all-strategies
  )
)

(define (pick-strategy user-response history)
  (let ((all-strategies (get-strategy user-response history)))
    (let ((number (random 1 (count-sum all-strategies))))
      (call/cc
        (lambda (cc-exit)
          (vector-foldl
            (lambda (i total-sum el)
              (if (or (<= number (+ (vector-ref el 1) total-sum)))
                (cc-exit (vector-ref el 2))
                (+ total-sum (vector-ref el 1))
              )
            )
            (vector-ref (vector-ref all-strategies 0) 1)
            all-strategies
          )
        )
      )
    )
  )
)

(define (reply-2 user-response history)
  ((pick-strategy user-response history) user-response history)
)

(define (doctor-driver-loop-v2 name history)
  (newline)
  (print '**) ; доктор ждёт ввода реплики пациента, приглашением к которому является **
  (let ((user-response (read)))
    (cond 
      ((equal? user-response '(goodbye)) ; реплика '(goodbye) служит для выхода из цикла
        (printf "Goodbye, ~a!\n" name)
        (println '(see you next week))
      )
      (else 
        (print (reply-2 user-response history)) ; иначе Доктор генерирует ответ, печатает его и продолжает цикл
        (doctor-driver-loop-v2 name (vector-append history (vector user-response)))
      )
    )
  )
)

;(visit-doctor-v2 'stop 4)