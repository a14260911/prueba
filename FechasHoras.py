#!/usr/bin/env python

from time import localtime, asctime, time
try:
    a = localtime()
    yyear = a.tm_year
    print(f"¡Feliz {yyear}!\n\n{a}")
    print(asctime(localtime()))
    inicio = time()

    for i in range(5000):
        print(f"{i} - ", end="")
        a = i

    print (a);
    final = time()

    print(f"He tardado {round(final - inicio, 1)} segundos.")
    
#     for i in range (5000):
#         print(f"{i}")
except:
     print("An exception occurred")