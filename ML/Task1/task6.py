def check(words_arg, filename=""):
    file = open(filename, "w")
    words = words_arg.lower().split(' ')
    print(words)
    words = dict.fromkeys(set(words), 0)
    print(words)
    words = dict(sorted(words.items(), key=lambda x: x[0]))

    for word in words_arg.lower().split(' '):
        if word in words.keys():
            words[word] += 1
    print(words)
    for word in words:
        file.write(word)
        file.write(" ")
        file.write(str(words[word]))
        file.write("\n")


if __name__ == "__main__":
    check("a aa abC aa ac abc bcd a", "test.txt")

