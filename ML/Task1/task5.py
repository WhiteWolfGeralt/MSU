def primes():
    prime_number = 2
    while True:
        yield prime_number
        find_prime = False
        while not find_prime:
            prime_number += 1
            find_prime = True
            for divisor in range(2, prime_number):
                if prime_number % divisor == 0:
                    find_prime = False
                    break
                if divisor ** 2 > prime_number:
                    break


if __name__ == "__main__":
    for i in primes():
        print(i)
        if i == 2:
            break
