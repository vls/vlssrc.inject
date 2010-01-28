# -*- coding: utf-8 -*-
import dolCallEnum
from ctypes import *
import win32con, win32api, win32process, win32event, win32security
import random, math
from dolData import *
from heapq import heappush, heappop
import time
from dolAddr import ADDR
import dolScript
import dolCallCmd
from global_ import *




area = dolCallCmd.TW

changeDelay = 2 # 切换场景类的操作的等待延时

class MemException(Exception):
    pass




def Clean(proc):
    win32api.CloseHandle(proc)


def isSceneChange(proc):
    '''是否场景切换
        return bool
    '''
    return getInt(proc,ADDR.SCENE_CHANGE) != 0         
    

def isBusy(proc):
    '''是否鼠标忙
        return bool
    '''
    return getInt(proc,ADDR.MOUSE_BUSY) != 0

def isOnline(proc):
    '''是否在线
    return bool
    '''
    return getInt(proc, ADDR.PC_STATE) == 1

def isNormal(proc):
    '''是否正常，可执行命令的状态
    == 在线 && !鼠标忙 && !切换场景
    '''
    flag = isOnline(proc)
    print isBusy(proc)
    flag2 = not isBusy(proc)
    flag3 = not isSceneChange(proc)
    print "isNormal %s %s %s" % (flag, flag2, flag3)
    return flag and flag2 and flag3

def writeCmd(proc, cmdList):
    '''
    注意：如果成功，需要使用者自行释放内存
    '''
    size = 1024
    
    assert len(cmdList) == size
    cmd = (c_ubyte * size)()
    
    for i in range(size):
        cmd[i] = cmdList[i]
        
    buf = VirtualAllocEx(proc.handle, None, size, win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
    if(buf == 0):
        raise MemException('VirtualAllocEx Fails')
    
    written = c_long(0) 
    ret = WriteProcessMemory(proc.handle, buf, byref(cmd), size, byref(written))
    
    if(written.value != size):
        ret = VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        if (ret == 0):
            raise MemException("Release memory failed!")
        raise MemException("WriteProcessMemory() does NOT write the complete command!")
    if(ret == 0):
        ret = VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        if (ret == 0):
            raise MemException("Release memory failed!")
        raise MemException('WriteProcessMemory() fails!')
    
    return buf

def writePara(proc, cPara):
    '''
    注意：如果成功，需要使用者自行释放内存
    '''
    size = 24
        
    buf = VirtualAllocEx(proc.handle, None, size, win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
    if(buf == 0):
        raise MemException('VirtualAllocEx Fails')
    
    written = c_long(0) 
      
    ret = WriteProcessMemory(proc.handle, buf, byref(cPara), size, byref(written))
    
    if(written.value != size):
        ret = VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        if (ret == 0):
            raise MemException("Release memory failed!")
        raise MemException("WriteProcessMemory() does NOT write the complete command!")
    if(ret == 0):
        ret = VirtualFreeEx(proc.handle, buf, 0, win32con.MEM_RELEASE)
        if (ret == 0):
            raise MemException("Release memory failed!")
        raise MemException('WriteProcessMemory() fails!')
    
    return buf

def execCmd(proc, cmdBuf, paraBuf):
    tHandle, tid = win32process.CreateRemoteThread(proc.handle, None, 0, cmdBuf, paraBuf, 0)
    print "Success! ThreadHandle, ThreadID = %d,%d" %( tHandle, tid)
    
    
    
    
    win32event.WaitForSingleObject(tHandle, -1)
    ret = win32api.CloseHandle(tHandle)
    if(ret == 0):
        raise MemException("Close handle failed!")
    
    ret = VirtualFreeEx(proc.handle, cmdBuf, 0, win32con.MEM_RELEASE)
    if(ret == 0):
        raise MemException("Release memory failed!")
    
    ret = VirtualFreeEx(proc.handle, paraBuf, 0, win32con.MEM_RELEASE)
    if(ret == 0):
        raise MemException("Release memory failed!")
    
    print "Cleaned"

def walk(proc, x, y):
    x = float(x)
    y = float(y)
    
    nowx, nowy = dolScript.getLandPos(proc)
    
    while(nowx != x and nowy != y):
        cmdBuf = writeCmd(proc, area.walkCmd)
        
        cpara = (c_ubyte * 24)()
    
        fpara = cast(cpara, POINTER(c_float))
        #print "x=%f, y=%f" % (x,y)
        fpara[0] = x
        fpara[1] = y
        
        ipara = cast(cpara, POINTER(c_int))
        for i in range(4):
            ipara[i+2] = getInt(proc, area.walkSeqAddrList[i])
            
        #=======================================================================
        # for i in range(24):
        #    print "para = %x" % (cpara[i])
        #=======================================================================
            
            
        paraBuf = writePara(proc, cpara)
        dowhile(isNormal, [proc])
        execCmd(proc, cmdBuf, paraBuf)
        
        time.sleep(0.2)
        nowx, nowy = dolScript.getLandPos(proc)
        

    
def follow(proc, userid):
    #print len(area.followCmd)
    
    userid = int(userid)
    
    cmdBuf = writeCmd(proc, area.followCmd)
    
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    
    for i in range(len(area.followPara)):
        cpara[i] = area.followPara[i]
        
        
    p = cast(cpara, POINTER(c_int))
    #print cpara
    #print p
    
    p[0] = userid    
    
    #high = random.randrange(0x100,0x1FF) << 16
    #p[5] += high
    #print p[4]
    #for i in range(6):
        #print p[i]
    
    #===========================================================================
    # for i in range(24):
    #    print "pp = %x" % (cpara[i])
    #===========================================================================
        
    paraBuf = writePara(proc, cpara)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
def seafollow(proc, userid):
    '''
    海上跟随
    '''
    userid = int(userid)
    
    cmdBuf = writeCmd(proc, area.seaFollowCmd)  
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    for i in range(len(area.seaFollowPara)):
        cpara[i] = area.seaFollowPara[i]
    
    ip = cast(cpara, POINTER(c_int))
    ip[0] = userid
    
    paraBuf = writePara(proc, cpara)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
def move(proc, moveto):
    '''
    从码头进入城市，或者从城市进入码头
    '''
    
    
    userid = dolScript.getPCID(proc)
    moveto = int(moveto)
        
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    ip = cast(cpara, POINTER(c_int))
    ip[0] = userid
    ip[1] = moveto
    
    ip[2] = random.randrange(0xA40000, 0x0141FFFF)
    ip[3] = random.randrange(0x01410000, 0x01FFFFFF)
    ip[4] = random.randrange(0xA40000, 0x0141FFFF)
    ip[5] = random.randrange(0x01410000, 0x01FFFFFF)
    paraBuf = writePara(proc, cpara)
        
    cmdBuf = writeCmd(proc, area.moveCmd)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    time.sleep(changeDelay)

def moveSea(proc):
    '''
    出航
    '''
    
    userid = dolScript.getPCID(proc)
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    ip = cast(cpara, POINTER(c_int))
    ip[0] = userid
    ip[1] = 0x41d34c
    
    #===========================================================================
    # ip[2] = random.randrange(0xA40000, 0x0141FFFF)
    # ip[3] = random.randrange(0x01410000, 0x01FFFFFF)
    # ip[4] = random.randrange(0xA40000, 0x0141FFFF)
    # ip[5] = random.randrange(0x01410000, 0x01FFFFFF)
    #===========================================================================
    
    paraBuf = writePara(proc, cpara)
        
    cmdBuf = writeCmd(proc, area.moveToSeaCmd)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    time.sleep(changeDelay)
    
def turn(proc, deg):
    '''
    以x轴正方向为0度，逆时针
    '''
    deg = float(deg)
    cos = math.cos(math.radians(deg))
    sin = -math.sin(math.radians(deg))
    
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    fp = cast(cpara, POINTER(c_float))
    fp[0] = cos
    fp[1] = sin
    
    ip = cast(cpara, POINTER(c_int))
    
    #===========================================================================
    # ip[2] = random.randrange(0xa40000, 0xef0000)
    # ip[3] = random.randrange(0xef0000, 0xf0ffff)
    # ip[4] = random.randrange(0xa4e900, 0xa4e9ff)
    # ip[5] = random.randrange(0xef0000, 0xf0ffff)
    #===========================================================================
    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.turnCmd)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)

def custom(proc, num):
    '''
    使用自订栏
    '''
    num = int(num)
    if( num < 1 or num > 8):
        print 'Invalid num'
        return

    num -= 1
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    ip = cast(cpara, POINTER(c_int))
    ip[0] = num
    ip[1] = 0x41e868
    
    #===========================================================================
    # ip[2] = random.randrange(0x3f0000, 0x018effff)
    # ip[3] = random.randrange(0x3f0000, 0x018effff)
    # ip[4] = random.randrange(0x3f0000, 0x0199ffff)
    # ip[5] = random.randrange(0x3f0000, 0x018effff)
    #===========================================================================
    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.customCmd)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
def enterD(proc):
    '''
    进港, 进门, 出门
    '''
    addr = getInt(proc, 0xB6FFC4)
    print "addr = %x" % (addr)
    
    tarx = getFloat(proc, 0xb6fb3c)
    tary = getFloat(proc, 0xb6fb44)
    
    
    
    heap = []
    for i in range(10):
        value = getInt(proc, addr)
        while(value == 0):
            addr += 4
            value = getInt(proc, addr)
            print "value = %x, addr = %x" % (value, addr)
        addr += 4
    
        
        addr_2 = value
        prevalue = getInt(proc, addr_2)
        value = getInt(proc, addr_2+4)
        print "prevalue = %x, value = %x, addr_2 = %x" %(prevalue, value, addr_2)
        while(value != 0):
            addr_2 += 4
            prevalue = value
            value = getInt(proc, addr_2+4)
            print "prevalue = %x, value = %x, addr_2 = %x" %(prevalue, value, addr_2)
            
        
        cityid = getInt(proc, prevalue + 4)
        
        if(cityid == 0):
            break
        
        x = getFloat(proc, prevalue + 0x10)
        y = getFloat(proc, prevalue + 0x18)
        p = Pos(cityid, tarx, tary, x, y)
        
        if(x != 0 and y != 0):
            heappush(heap, p)
        
        print "%x %.4f %.4f dis = %d" % ( cityid, x, y, p.dis)
    near = heappop(heap)
    print "x = %.4f, y= %.4f" % (tarx,tary)
    print "the nearest door is %x %d" % (near.id, near.dis)
     
    
    enterDoor(proc, near.id)

def enterDoor(proc, did):
    '''
    '''
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    ip = cast(cpara, POINTER(c_int))
    ip[0] = did
    ip[1] = 0x41d34c
    

    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.enterDCmd)
    
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    time.sleep(changeDelay)


def sail(proc, state):
    '''
    升降帆
    '''
    state = int(state)
    assert state >= 0 and state <= 4
    
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    ip = cast(cpara, POINTER(c_int))
    ip[0] = state
    ip[1] = 0x41fd08
    
    #===========================================================================
    # ip[2] = random.randrange(0x026bFFFF, 0x02830000)
    # ip[3] = random.randrange(0x027d0000, 0x0283FFFF)
    # ip[4] = random.randrange(0x026bFFFF, 0x02830000)
    # ip[5] = random.randrange(0x027d0000, 0x0283FFFF)
    #===========================================================================
    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.sailCmd)
    
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
def getNPC(proc):
    addr = getInt(proc, 0xb6ffa4)
    
    addr_2 = getInt(proc, addr)
    while(addr_2 == 0):
        addr += 4
        addr_2 = getInt(proc, addr)
    for i in range(1000):
        #print "----------------------Round %d -------------------------" % (i)
        #print "addr_2 before = %x" % (addr_2)
        id = getInt(proc, addr_2)
        
        if(id == 0):
            break
        
        namebase = getInt(proc, addr_2 + 4)
        addr_2 = getInt(proc, addr_2 + 8)
        #print "addr_2 after = %x" % (addr_2)
        #print "%x" %( namebase)
        namebase_2 = getInt(proc, namebase + 0x3c)
        #print "%x" % ( namebase_2)
        name = getStringW(proc, namebase_2, 40)
        #name2 = getString(proc, namebase_2, 40)
        #print name2
        #print unicode(name2).encode('gbk')
        #print name.encode('utf-8')
        #print name
        x = getFloat(proc, namebase + 0x3c + 0xe0)
        y = getFloat(proc, namebase + 0x3c + 0xe0 + 0x8)
        unknown = getFloat(proc, namebase + 0x3c + 0xe0 + 0x4)
        if(x != 0):
            print "id = %8x, name = %s, x = %.3f, y = %.3f" % (id, name,x, y)
        
        
        while(addr_2 == 0):
            addr += 4
            addr_2 = getInt(proc, addr)
            #print "addr_2 Adjust = %x" % (addr_2)




def __isOpened(proc):
    '''
    开了对话框？
    (存疑)
    '''
    addr = getInt(proc, 0xbd8388)
    addr = getInt(proc, addr)
    addr = getInt(proc, addr + 8)
    value = getInt(proc, addr + 0xC)
    return value != 0

def __getSellPara(proc):
    '''
    获取卖船的某个参数
    '''
    addr = getInt(proc, 0xbd805c)
    print "addr = %x" % (addr)
    print "after adjust = %x" %(addr + 0x5e8)
    addr = getInt(proc, addr + 0x5e8)
    
    print "addr = %x" % (addr)
    print "after adjust = %x" %(addr + 0xe8)
    value2 = getInt(proc, addr + 0xe8)
    print "value2 = %x" % (value2)
    return value2

def sellShip(proc, bossid):
    '''
    卖船
    '''
    
    bossid = int(bossid)
     
    
    if(not __isOpened(proc)):
        paraSize = 24
        cpara = (c_ubyte * paraSize)()

        
        ip = cast(cpara, POINTER(c_int))
        ip[0] = bossid
        ip[1] = 0
        ip[2] = 0x53
        
        paraBuf = writePara(proc, cpara)
        cmdBuf = writeCmd(proc, area.openSellShipCmd)
        
        dowhile(isNormal, [proc])
        execCmd(proc, cmdBuf, paraBuf)
    
        while(True):
            if(__isOpened(proc)):
                print "Open finished!"
                break      
            print "Wait..."      
            time.sleep(0.2)
    
    para2 = __getSellPara(proc)
    
    paraSize = 24
    cpara = (c_ubyte * paraSize)()
    ip = cast(cpara, POINTER(c_int))
    ip[0] = bossid
    ip[1] = para2
    ip[2] = 0x53
    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.sellShipCmd)
    
    time.sleep(4)
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
def talk(proc, tarid):
    '''
    与npc对话
    '''
    tarid = int(tarid)
    
    paraSize = 24
    cpara = (c_ubyte * paraSize)()

    
    ip = cast(cpara, POINTER(c_int))
    ip[0] = tarid
    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.talkCmd)
    
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
def buildShip(proc, shipid, woodid, storage, bossid):
    '''
    买船
    '''
    shipid = int(shipid)
    woodid = int(woodid)
    storage = int(storage)
    bossid = int(bossid)
    
    paraSize = 24
    cpara = (c_ubyte * paraSize)()

    
    ip = cast(cpara, POINTER(c_int))
    ip[0] = shipid
    ip[1] = woodid
    ip[2] = storage
    ip[3] = bossid
    ip[4] = 0x0206
    
    paraBuf = writePara(proc, cpara)
    cmdBuf = writeCmd(proc, area.buildShipCmd)
    
    dowhile(isNormal, [proc])
    execCmd(proc, cmdBuf, paraBuf)
    
    
