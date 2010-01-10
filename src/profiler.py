# -*- coding: GBK -*-
import time
import timeit
import cProfile
import sys
import getopt

func = None

def usage():
    print "profiler.py <times> <to-test-python-filename> <function>"

def pp(s1, s2):
    print "%s, %s" %(s1,s2)    

def wraper(times, argv):
    for i in range(times):
        func(argv)    

def main(arg=sys.argv):
    global func
    optlist, args = getopt.getopt(arg[1:], "m:t:")
    print optlist
    print args
    
    optdict = dict(optlist)
    times = 100
    if(optdict.has_key('-t')):
        times = int(optdict['-t'])
    
    if(not optdict.has_key('-m')):
        usage()
        return
    
    modName = optdict['-m']
    mod = __import__(modName)
    funcName = args[0]
    func = getattr(mod, funcName)
    string = str(args)
    runstring = "wraper(%s, %s)" % (times,string)
    cProfile.run(runstring)



if __name__ == "__main__":
    main()