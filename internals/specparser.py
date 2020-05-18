import socket

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

def address_set(addresses, addressfiles):
    addresses = addresses or []
    addressfiles = addressfiles or []

    for addr_filename in addressfiles:
        try:
            addr_file = open(addr_filename)
            new_addr = [ line.strip() for line in addr_file if len(line.strip()) > 0 ]
            addresses.extend(new_addr)
        except FileNotFoundError:
            print('No such file: "' + addr_filename + '"')

    addr_set = set(addresses)

    bad_addr = []

    for addr in addr_set:
        try:
            socket.inet_aton(addr)
        except socket.error:
            print('Bad IP address: "' + addr + '"')
            bad_addr.append(addr)

    for addr in bad_addr:
        addr_set.remove(addr)

    return addr_set
