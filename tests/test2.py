i = 1
j = 1

origin = [0, 0]
for _ in range(248):

    origin[0] = 24 * (j - 1) + 2
    origin[1] = 24 * (i - 1) + 2


    print(origin)

    if j % 22 == 0:
        i += 1
        j = 0

    j += 1