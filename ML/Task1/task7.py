process = lambda l: [sorted({x * x for x in sum(l, [])})][::-1]
