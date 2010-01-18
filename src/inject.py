# -*- coding: GBK -*-
from ctypes import *
import sys
import win32process
import win32api
import win32con
import os
import win32security
import pywintypes
import random
import win32event
import getopt
import dolCall

kernel32 = windll.kernel32
VirtualAllocEx = kernel32.VirtualAllocEx
VirtualFreeEx = kernel32.VirtualFreeEx
LoadLibraryA = kernel32.LoadLibraryA
WriteProcessMemory = kernel32.WriteProcessMemory









def query():
    hToken = win32security.OpenProcessToken (win32api.GetCurrentProcess (), win32security.TOKEN_QUERY)
    #print "------------------------------------------"
    for luid, flags in win32security.GetTokenInformation (hToken, win32security.TokenPrivileges):
        privilege_name = win32security.LookupPrivilegeName (None, luid)
        print privilege_name, "is enabled" if flags & win32security.SE_PRIVILEGE_ENABLED else "is not enabled"

def raiseP():
    #query()
    priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    hToken = win32security.OpenProcessToken (
      win32api.GetCurrentProcess (), 
      priv_flags
    )
    privilege_id = win32security.LookupPrivilegeValue (
      None, 
      win32security.SE_DEBUG_NAME
    )
    #print "privilege_id = %d" % (privilege_id)
    old_privs = win32security.AdjustTokenPrivileges (hToken, 0, [(privilege_id, win32security.SE_PRIVILEGE_ENABLED | win32security.SE_PRIVILEGE_USED_FOR_ACCESS )])
    #print "old_priv = %s" %( old_privs)
    #query()
    print "raise privilege error code = %d" %  (win32api.GetLastError())

def getProcByName(procName):
    
    pidList = win32process.EnumProcesses()
    #print pidList

    raiseP()
    
    for pid in pidList:
        try:
            #print pid
            win32api.SetLastError(0)
            hProcess = win32api.OpenProcess(
                                            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ
                                             | win32con.PROCESS_CREATE_THREAD | win32con.PROCESS_VM_OPERATION 
                                             | win32con.PROCESS_VM_WRITE
                                            , False, pid)
            #print "error code = %d" %  (win32api.GetLastError())
            #print "open process pid = %d" % (pid)
            hProcessFirstModule = win32process.EnumProcessModules(hProcess)[0]
            fullname = os.path.split(win32process.GetModuleFileNameEx(hProcess, hProcessFirstModule))
            #print fullname
            processName = os.path.splitext(fullname[1])[0]
            #print processName
            
            if(not procName.isalpha()):
                #print unicode(procName.decode("gbk"))
                #print processName
                procName = unicode(procName.decode("gbk"))
                
                #print unicode(processName)
                processName = unicode(processName)
                
                if(procName == processName):
                    return hProcess
            else:
                #print processName 
                if( procName.lower() == processName.lower()):
                    return hProcess
            win32api.CloseHandle(hProcess)
        except pywintypes.error as e:
            #print "fail to open process pid = %d" % (pid)

            #print e
            pass
    return None

def Clean(proc):
    win32api.CloseHandle(proc)



def inject(proc, dllName):
    size = len(dllName) + 1
    buf = VirtualAllocEx(proc.handle, None, size, win32con.MEM_COMMIT, win32con.PAGE_READWRITE)

    if(buf == 0):
        Clean(proc)
        print "VirtualAllocEx Fails"
        return
    
    written = c_long(0)    
    ret = WriteProcessMemory(proc.handle, buf, dllName, size, byref(written))
    
    if(written.value != size or ret == 0):
        VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        Clean(proc)
        print "WriteProcessMemory Fails"
        return
    
    module = win32api.GetModuleHandle("kernel32")
    if(module == 0):
        VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        Clean(proc)
        print "GetModuleHandle Fails"
        return
    
    addr = win32api.GetProcAddress(module, "LoadLibraryA")
    if(addr == 0):
        VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        Clean(proc)
        print "GetProcAddress Fails"
        return
    
    tHandle, tid = win32process.CreateRemoteThread(proc.handle, None, 0, addr, buf, 0)
    print "Success! ThreadHandle, ThreadID = %d,%d" %( tHandle, tid)
    
    print "wait for single object return = %d" % (win32event.WaitForSingleObject(tHandle, win32event.INFINITE))
    
    print "return code = %d" % (win32process.GetExitCodeThread(tHandle))
    print "error code = %d, %s" %  (win32api.GetLastError(), win32api.FormatMessage(win32api.GetLastError()))
    
    
    
    ret = VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
    if(ret == 0):
        print "Free fails"
    win32api.CloseHandle(tHandle)
    print "Cleaned"
    


def usage():
    print "inject -p <process> <dll>"
    


def main(argv=sys.argv):
#    if(len(sys.argv) != 4):
#        usage()
#        return
    #print kernel32.LoadLibraryA("TraceAPI.dll")
    
    optlist, args = getopt.getopt(argv[1:], 'cp:f:wh:i:')
    
    optdict = dict(optlist)
    print optdict
    print args
    if(optdict.has_key('-c')):
        dolCall.area = dolCall.CN
        
    if(optdict.has_key('-h')):
        dllName = optdict['-h']
        print "LoadLibrary %s = %d" %(dllName, kernel32.LoadLibraryA(dllName))
        
    if(optdict.has_key('-p')):
        procName = optdict['-p']
        hProc = getProcByName(procName)
        if(hProc == None):
            print "Can't find the process named %s" % (procName)
            return
    
    try:
        if(optdict.has_key('-i')):
            dllName = optdict['-i']
            inject(hProc, dllName)
        elif(optdict.has_key('-f')):
            funcName = optdict['-f']
            mod = __import__('dolCall')
            func = getattr(mod, funcName)
            func(hProc, *args)
            #dolCall.follow(hProc, id)
        else:
            usage()
    finally:
        win32api.CloseHandle(hProc)



if __name__ == "__main__":
    main()
