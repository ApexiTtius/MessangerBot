def getset(filename):
    with open(filename, encoding="UTF-8") as f:
        token = f.readline().strip()
        data = f.readlines()
        for ind, i in enumerate(data):
            data[ind] = i.strip().split()

        return [token, data]



getset("settings.txt")