# 匯入套件
import os
import numpy as np
import datetime
import time
import pandas as pd
from talib import abstract


def ConvertKBar(date, data, n):
    # 定義初始時間及K棒頻率
    StartTime = datetime.datetime.strptime(
        date + ' 09000000000', '%Y%m%d %H%M%S%f')
    space = datetime.timedelta(0, 60*n)
    Bar = []
    for i in data:
        # 時間
        time = datetime.datetime.strptime(date + ' ' + i[0], '%Y%m%d %H%M%S%f')
        # 價格
        price = float(i[2])
        # 成交量
        volume = int(i[3])
        if time < StartTime:
            # 時 開 高 低 收 量
            # 最高價判斷
            Bar[-1][2] = max(price, Bar[-1][2])
            # 最低價判斷
            Bar[-1][3] = min(price, Bar[-1][3])
            # 收盤價更換
            Bar[-1][4] = price
            # 累計成交量
            Bar[-1][5] += volume
        # 新增K棒
        else:
            while time >= StartTime:
                # 起始時間 + 週期
                StartTime += space
            # 新增一根新的K棒
            Bar.append([str(StartTime), price, price, price, price, volume])
    return Bar


def getKbar(file):
    Bar = open(file).readlines()
    Bar = [i.strip('\n').split(',') for i in Bar]
    # 存成dict 格式
    KBar = {}
    # 取出時 開 高 低 收 量
    KBar['time'] = np.array([i[0] for i in Bar])
    KBar['open'] = np.array([float(i[1]) for i in Bar])
    KBar['high'] = np.array([float(i[2]) for i in Bar])
    KBar['low'] = np.array([float(i[3]) for i in Bar])
    KBar['close'] = np.array([float(i[4]) for i in Bar])
    KBar['volume'] = np.array([float(i[5]) for i in Bar])
    return KBar


def run(stock, KbarsMinutes, KbarsNewHigh, StopLoss):
    path = '../StockData/'   # 資料路徑
    NameList = os.listdir(path)     # 取資料夾內所有檔名
    Record = open('Record.csv', 'w')  # 交易紀錄
    Position = 0                    # 手中持有股票的張數
    Prod = stock                   # 股票標的
    QTY = '1'                       # 交易的張數
    Cycle = KbarsMinutes                      # K棒的頻率

    target_file = 'KBar_'+Prod+'_'+str(Cycle)+'.txt'

    if os.path.exists(target_file) == False:
        Output = []
        # 逐日回測
        for name in NameList:
            # 日期
            Date = name[:8]
            # 讀檔並整理資料
            data = open(path + name).readlines()
            data = [i.strip('\n').split(',') for i in data if i[13:17] == Prod]
            Output += ConvertKBar(Date, data, Cycle)

        Output = '\n'.join([','.join([str(j) for j in i]) for i in Output])
        file = open(target_file, 'w')
        file.write(Output)
        file.close()

    # 取K棒
    KBar = getKbar(target_file)

    # 要用np.array格式
    KBar['k'], KBar['d'] = abstract.STOCH(KBar['high'],
                                          KBar['low'],
                                          KBar['close'],
                                          fastk_period=9,
                                          slowk_period=3,
                                          slowk_matype=0,
                                          slowd_period=3,
                                          slowd_matype=0)

    HighPrice = 0
    StopLoss = 1-(StopLoss/100)

    # 進出場判斷
    for i in range(12, len(KBar['time'])):
        Date = KBar['time'][i][:10].replace('-', '')
        Time = KBar['time'][i][11:].replace(':', '') + '000000'
        ThisHigh = KBar['high'][i]
        ThisClose = KBar['close'][i]
        ThisK = float(KBar['k'][i])
        ThisD = float(KBar['d'][i])
        LastK = float(KBar['k'][i-1])
        LastD = float(KBar['d'][i-1])
        ThisVolume = KBar['volume'][i]
        start = i-(KbarsNewHigh-1)
        MaxVolume = max(KBar['volume'][start:i+1])

        # K值 由下往上穿越 D值 且 當根K棒成交量為近五根最高
        if Position < 18 and LastK <= LastD and ThisK > ThisD and ThisVolume == MaxVolume:
            Record.write(
                ','.join([Prod, 'B', Date, Time, str(ThisClose), QTY+'\n']))
            print('進場', Prod, 'B', Date, Time, ThisClose, QTY)
            Position += 1
            HighPrice = max(HighPrice, ThisClose)  # 進場後最高價

        # 持有多單
        elif Position > 0:
            # 停損 (移動停損法 5%) #可調整
            HighPrice = max(HighPrice, ThisHigh)
            # StopLoss 0.95
            if ThisClose <= HighPrice * StopLoss:
                for i in range(Position):
                    Record.write(
                        ','.join([Prod, 'S', Date, Time, str(ThisClose), QTY+'\n']))
                print('停損', Prod, 'S', Date, Time, ThisClose, Position)
                Position = 0
                HighPrice = 0

    # 回測時間結束強制平倉
    if Position > 0:
        for i in range(Position):
            Record.write(
                ','.join([Prod, 'S', Date, Time, str(ThisClose), QTY+'\n']))
        print('結束', Prod, 'S', Date, Time, ThisClose, Position)

    Record.close()


if __name__ == "__main__":
    run('2330', 60, 2, 4.5)
