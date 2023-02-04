
def run():
    data = open('Record.csv').readlines()
    data = [i.strip('\n').split(',') for i in data]

    Position = {}    # 部位狀態
    Record = []      # 進出場的交易紀錄
    BackData = {
        '買進日期': [],
        '買進時間': [],
        '買進價格': [],
        '售出日期': [],
        '售出時間': [],
        '售出價格': [],
        '數量': [],
        '獲利': [],
        '累積獲利': []
    }

    # 整理交易紀錄
    for d in data:
        # 商品代碼、多空方向、日期、時間、價格、張數
        Prod, BS, Date, Time, Price, QTY = d
        for i in range(int(QTY)):
            # 該商品沒有部位
            if Prod not in Position.keys() or Position[Prod] == []:
                Position[Prod] = [[Prod, BS, Date, Time, Price]]
            # 該商品已有部位
            else:
                # 同方向
                if BS == Position[Prod][0][1]:
                    Position[Prod].append([Prod, BS, Date, Time, Price])
                # 反方向
                else:
                    # 商品代碼、多空方向、進場日期、進場時間、進場價格、出場日期、出場時間、出場價格
                    Record.append(Position[Prod][0] + [Date, Time, Price])
                    del Position[Prod][0]

    # 回測結束，檢查是否仍持有部位
    Check = [p for p in Position.keys() if Position[p] != []]
    if Check != []:
        print('請將全數股票部位平倉，未平倉股票代碼:', Check)

    # 判斷是否超額交易
    Over_5_Millions = False
    Capital = 5000000
    temp = []
    for i in Record:
        # 新倉or平倉、商品代碼、價格
        temp.append(['Order', i[0], float(i[4])])
        temp.append(['Cover', i[0], float(i[7])])
    temp = sorted(temp, key=lambda k: k[1])
    for i in temp:
        Prod = int(i[1])
        Price = i[2] * 1000
        fee = Price * 0.001425
        # 股票
        if 1000 < Prod < 9999:
            tax = Price * 0.003
        # ETF
        else:
            tax = Price * 0.001
        # 進場
        if i[0] == 'Order':
            Capital = Capital - Price - fee
        # 出場
        elif i[0] == 'Cover':
            Capital = Capital + Price - fee - tax
        # 判斷資金部位
        if Capital < 0:
            Over_5_Millions = True
            break
    if Over_5_Millions == True:
        print('有超額交易')
        Over_5_Millions = '是'
    else:
        print('無超額交易')
        Over_5_Millions = '否'

    # 記錄每筆損益
    Profit = []
    Return_Rate = []
    for i in Record:
        Prod = int(i[0])
        OrderPrice = float(i[4]) * 1000
        CoverPrice = float(i[7]) * 1000
        fee = round(OrderPrice * 0.001425) + round(CoverPrice * 0.001425)
        # 股票
        if 1000 < Prod < 9999:
            tax = round(CoverPrice * 0.003)
        # ETF
        else:
            tax = round(CoverPrice * 0.001)
        # 多單
        if i[1] == 'B':
            P = CoverPrice-OrderPrice-fee-tax
            Profit.append(P)
            Return_Rate.append(P/OrderPrice)
            BackData['買進日期'].append(i[2][:4]+"/"+i[2][4:6]+"/"+i[2][6:8])
            BackData['買進時間'].append(i[3][0:2]+":"+i[3][2:4])
            BackData['買進價格'].append(i[4])
            BackData['數量'].append("1")
            BackData['售出日期'].append(i[5][:4]+"/"+i[2][4:6]+"/"+i[2][6:8])
            BackData['售出時間'].append(i[6][0:2]+":"+i[6][2:4])
            BackData['售出價格'].append(i[7])
            BackData['獲利'].append(P)
            BackData['累積獲利'].append(sum(BackData['獲利']))
        # 空單
        elif i[1] == 'S':
            P = OrderPrice-CoverPrice-fee-tax
            Profit.append(P)
            Return_Rate.append(P/OrderPrice)
            BackData['買進日期'].append(i[2][:4]+"/"+i[2][4:6]+"/"+i[2][6:8])
            BackData['買進時間'].append(i[3][0:2]+":"+i[3][2:4])
            BackData['買進價格'].append(i[4])
            BackData['數量'].append("1")
            BackData['售出日期'].append(i[5][:4]+"/"+i[2][4:6]+"/"+i[2][6:8])
            BackData['售出時間'].append(i[6][0:2]+":"+i[6][2:4])
            BackData['售出價格'].append(i[7])
            BackData['獲利'].append(P)
            BackData['累積獲利'].append(sum(BackData['獲利']))

    # 獲利及虧損的資料
    Win = [i for i in Profit if i > 0]
    Loss = [i for i in Profit if i < 0]

    # 總損益
    Total_Profit = sum(Profit)
    # 總交易次數
    Total_Trade = len(Profit)
    # 平均損益
    Avg_Profit = Total_Profit / Total_Trade
    # 勝率
    Win_Rate = len(Win) / Total_Trade
    # 獲利因子及賺賠比
    if len(Loss) == 0:
        Profit_Factor = 'NA'
        Win_Loss_Rate = 'NA'
    else:
        Profit_Factor = sum(Win) / -sum(Loss)
        Win_Loss_Rate = (sum(Win)/len(Win)) / (-sum(Loss)/len(Loss))
    # 最大資金回落
    MDD, Capital, MaxCapital = 0, 0, 0
    for p in Profit:
        Capital += p
        MaxCapital = max(MaxCapital, Capital)
        DD = MaxCapital - Capital
        MDD = max(MDD, DD)
    # 夏普比率 (忽略無風險利率)
    import numpy as np
    Return_Rate = np.array(Return_Rate)
    Sharpe_Ratio = np.mean(Return_Rate) / np.std(Return_Rate)

    # 將績效指標匯出
    file = open('KPI.csv', 'w')
    file.write(','.join(['總損益', '總交易次數', '平均損益', '勝率',
               '獲利因子', '賺賠比', '最大資金回落', '夏普比率', '是否超額交易', '\n']))
    file.write(','.join([str(Total_Profit), str(Total_Trade), str(Avg_Profit), str(Win_Rate), str(
        Profit_Factor), str(Win_Loss_Rate), str(MDD), str(Sharpe_Ratio), Over_5_Millions]))
    file.close()

    # print(BackData)
    # print('總損益', str(Total_Profit), '\n總交易次數', str(Total_Trade), '\n平均損益', str(Avg_Profit), '\n勝率', str(Win_Rate), '\n獲利因子', str(
    #    Profit_Factor), '\n賺賠比', str(Win_Loss_Rate), '\n最大資金回落', str(MDD), '\n夏普比率', str(Sharpe_Ratio), '\n是否超額交易', Over_5_Millions)
    KPI_dict = {'交易次數': Total_Trade,
                '總損益': Total_Profit,
                '平均損益': Avg_Profit,
                '勝率': Win_Rate,
                '獲利因子': Profit_Factor,
                '賺賠比': Win_Loss_Rate,
                '最大資金回落': MDD,
                '夏普比率': Sharpe_Ratio,
                '是否超額交易': Over_5_Millions,
                'data': BackData
                }
    return KPI_dict


if __name__ == "__main__":
    run()
