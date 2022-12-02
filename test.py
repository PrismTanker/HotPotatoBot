from hotloader import Hotloader

default_users = Hotloader('defaults.txt', 3600, lambda x: 
        {int(pair[0]): int(pair[1]) for pair in [s.split() for s in x]}
        )
while True:
    print(default_users.get())