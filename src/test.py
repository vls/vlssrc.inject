import ctypes

memcpy = ctypes.cdll.msvcrt.memcpy
memmove = ctypes.memmove

def main():
    size = 20
    arr = []
    for i in range(size):
        arr.append(i)
    
    print arr
    
    buf = (ctypes.c_ubyte * size)()
    #print ctypes.addressof(arr)
    print id(arr)
    print buf
    for i in range(size):
        print "buf[%d] = %x" % (i, buf[i]) 
    
    #memcpy(ctypes.byref(buf), id(arr), size)
    memmove(ctypes.byref(buf), arr, size)
    
    for i in range(size):
        print "buf[%d] = %x" % (i, buf[i])
    
if __name__ == "__main__":
    main()