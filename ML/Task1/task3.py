def longestCommonPrefix(x):
    first = x[0].strip()
    ret = ""
    for i in range(0, len(first)):
        for j in range(1, len(x)):
            if x[j].strip().find(first[: i + 1]) != 0:
                return ret
        ret = first[: i + 1]
    return ret


if __name__ == "__main__":
    print(longestCommonPrefix(["c", "cc", "ccc"]))
