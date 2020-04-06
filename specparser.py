def number_set(numberspec):
    numberset = set()

    for part in numberspec.split(","):
        part = part.strip()

        split_part = part.split("-")

        if len(split_part) == 1: # 1 number with no -, its a single port
            numberset.add(int(part))
        elif len(split_part) == 2: # 2 numbers with - inbetween, its a range
            a = int(split_part[0])
            b = int(split_part[1])

            for num in range(a, b + 1):
                numberset.add(num)

    return numberset
