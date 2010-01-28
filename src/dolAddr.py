# -*- coding: utf-8 -*-
'''
Created on 2009-12-31

@author: vls
'''

OFFSET = 0x1E130 # C5+ 台服与国服的偏移

class ADDR:
    #section 1
    MOUSE_BUSY = 0xB4D6A0 + OFFSET                  #鼠标是否为漏斗状  #B6B7D0
    TAB_OBJTYPE = MOUSE_BUSY + 0x9c - 0x78          #TAB对象类型
    TAB_ID = TAB_OBJTYPE + 0xA0 - 0x9c              #TAB对象ID
    TAB_NUM = 0xB6B848                              #TAB选择框按钮数目
    SCENE_CHANGE = 0xB4e170 + OFFSET                #切换场景
    
    QUICK_KEY = 0xB4E8E8 + OFFSET + 0x1440          #快捷键
    PC_STATE = 0xB6F97C				# 1 =正常, 0 =断线
    
    
    
    
    #section 2
    COMBAT_STATE = 0xB6FA3c             #战斗状态         0=正常 1=主动攻击 2=被攻击 3= 模拟主动攻击 4= 模拟被动攻击

    
    
    HP = 0xB6FAF0                       #行动力
    
    PC_NAME = HP - 0xD8                 #玩家名称
    PC_ID = HP - 0xCC                   #玩家ID
    SHIP_STATE = HP - 0XBC              #船只状态
    
    
    
    HPMAX = HP + 4                      #最大行动力
    MONEY = HP + 8                      #金钱
    #SAILOR = 0xB6FAFC									#当前水手
    FATIGUE = HP + 0x10                 #疲劳 > 300吃，（显示值的10倍）
    FOOD = HP + 0x12                    #食品
    WATER = HP + 0x14                   #水
    BOMB = HP + 0x16                    #炮弹
    WOOD = HP + 0x18                    #木头
    
    SHIP_HP = HP + 0x3A - 0x20          #船耐久
    #SHIP_MAXHP = 0xB6FE60               #船最大耐久
    PC_X = 0xB6FB3C                     #人物X坐标 （陆地和海洋）
    PC_Y = PC_X + 8                     #玩家Y坐标
    
    PC_COS = PC_X + 0x10                #玩家方向COS（陆地和海洋）
    PC_SIN = PC_COS + 8                 #玩家SIN     
    
    #SECTION 3
    LAND_FOLLOW = 0xB51D9C + OFFSET + 4 #陆地跟随
    
    
    
    AUTO_SAIL = 0xB51DC0 + OFFSET + 4   #自动航行
    
    
    SEA_FOLLOW = 0xB6FF40               #海洋跟随
    
    SAIL_STATE = SEA_FOLLOW - 0x6c
    
    TAB_PCBASE = SEA_FOLLOW + 0xCC - 0x68   #TAB 选择人物及NPC对象基址
    
    TAB_STATIC = SEA_FOLLOW + 0xEC - 0x68   #TAB 选择静物对象基址
    
    LOCATION = SEA_FOLLOW + 0xb0c -0xa68    #所在地方名称基址（包括港口，室内，海域）[[ADDR]]
    
    SEASEQ = 0xB7004A                   #海域序号
    LOCTYPE = 0xB7004B                  #所在地方类型
    
    PARTY_BASE = SEA_FOLLOW + 0xb78 - 0xa68    #队伍基址 [[ADDR]+C]
    
    TAB_STATIC2 = TAB_STATIC + 0x690    #静物对象2级
    
    #section 4
    BOOL_CUSTOM = 0xb536c8 + OFFSET + 0x40
    
    
    
    #section 5
    WEATHER = 0xB538D5 + OFFSET + 0x60 #验证 2010/1/1
    SAIL_DAY = WEATHER + 3
    
    @staticmethod
    def getIntList():
        return [ADDR.HP, ADDR.HPMAX, ADDR.MONEY, ADDR.PC_ID,  ADDR.SHIP_HP]
    
    @staticmethod
    def getIntStr():
        return ['HP = %d', 'MaxHP = %d', 'Money = %d', '人物ID = %d', '船只耐久 = %d']
    
    @staticmethod
    def getShortList():
        return [ADDR.FATIGUE, ADDR.FOOD, ADDR.WATER, ADDR.WOOD, ADDR.BOMB]
    
    @staticmethod
    def getShortStr():
        return ['疲劳 = %d', '食物  = %d', '水 = %d', '木 = %d', '炮弹 = %d']
    



    
#SKILL_BASE = 0xBD8388		#ADDR+0x20+0x38 = 技能数目
#  ADDR + 0x20 + 0xC #技能1ID
#ADDR + 0x20 + 0x14 #技能2ID
#ADDR + 0x20 + 0x1C #技能3ID

#