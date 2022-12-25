from math import *

def prime(n):
    s = 0
    for i in range(1, 2**n+1):
        ss = 0
        for j in range(1, i+1):
            ss += floor( cos(pi * (factorial(j-1) + 1)/j)**2 )
        
        T = n / ss
        
        s += floor( T**(1/n) )
    
    return 1 + s

def prime2(n):
    return floor( (factorial(n) % (n+1)) / n ) * (n-1) + 2

for i in range(1,41):
    print(prime(i))
    
