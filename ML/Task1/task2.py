def is_palindrome(x):
    tmp = x
    reversed_x = 0
    while x > 0:
        reversed_x *= 10
        reversed_x += x % 10
        x //= 10
    if tmp == reversed_x:
        return "YES"
    else:
        return "NO"


if __name__ == "__main__":
    print(is_palindrome(0))
