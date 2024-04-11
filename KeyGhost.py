# 2023年1月12日23:35:17开始，实现模拟键鼠的操作
# 2023年2月4日21:11:18完工。开始测试和修改
import sys,threading,os,json,datetime,time,random
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox,QFileDialog,QComboBox,QTableWidgetItem
from PyQt5.QtCore import pyqtSignal
import pyautogui as pag
from Ui_KeyGhost import Ui_KeyGhost
 
# 定义全局常量
pag.FAILSAFE = True
ACTIONLIST = ['MoveTo', 'MoveRel', 'MouseDown', 'MouseUp', 'FakeTime', 'KeyDown', 'KeyUp','TypeWrite',
              'ClickLeft', 'ClickRight', 'ClickLeftMulti', 'ClickRightMulti', 'Scroll']
MOVETYPELIST = [pag.easeInQuad,pag.easeOutQuad,pag.easeInOutQuad,pag.easeInCubic,pag.easeOutCubic,pag.easeInOutCubic,
        pag.easeInQuart,pag.easeOutQuart,pag.easeInOutQuart,pag.easeInQuint,pag.easeOutQuint,pag.easeInOutQuint,pag.easeInSine,
        pag.easeOutSine,pag.easeInOutSine,pag.easeInExpo,pag.easeOutExpo,pag.easeInOutExpo,pag.easeInCirc,pag.easeOutCirc,pag.easeInOutCirc,
        pag.easeInElastic,pag.easeOutElastic,pag.easeInOutElastic,pag.easeInBack,pag.easeOutBack,pag.easeInOutBack,pag.easeInBounce,
        pag.easeOutBounce,pag.easeInOutBounce]
ISRUN = 0   # 0是停止  1是运行

# 定义全局函数
# 定义键鼠操作
def fMoveTo( X, Y, XOffset, YOffset, duration, durationOffset):
    X = random.randint( X - XOffset, X + XOffset)
    Y = random.randint( Y - YOffset, Y + YOffset)
    duration = random.uniform( duration - durationOffset, duration + durationOffset)       #duration为移动到目标点的指定耗时
    moveType = random.choice( MOVETYPELIST)      #定义鼠标的移动方式           
    pag.moveTo( X, Y, duration=duration, tween=moveType)
    #返回值，实际移动到的坐标X，Y，实际耗时duration，移动方式moveType
    duration = round( duration, 2)
    return X, Y, duration, moveType

def fMoveRel( X, Y, XOffset, YOffset, duration, durationOffset):
    X = random.randint( X - XOffset, X + XOffset)
    Y = random.randint( Y - YOffset, Y + YOffset)
    duration = random.uniform( duration - durationOffset, duration + durationOffset)       #duration为移动到目标点的指定耗时
    moveType = random.choice( MOVETYPELIST)      #定义鼠标的移动方式           
    pag.moveRel( X, Y, duration=duration, tween=moveType)
    #返回值，实际移动到的坐标X，Y，实际耗时duration，移动方式moveType
    duration = round( duration, 2)
    return X, Y, duration, moveType    

def fClickLeft():
    pag.click( button='left')

def fClickRight():
    pag.click( button='right')

def fClickLeftMulti( clicks, interval, intervalOffset=0.15):      # 参数clicks是点击次数， interval是两次点击的时间间隔， intervalOffset是点击的时间间隔的偏移值，使每两次点击的时间间隔不一样
    for i in range( 0, clicks):
        pag.click( button='left')
        fFakeTime( 's', interval - intervalOffset, interval + intervalOffset)

def fClickRightMulti( clicks, interval, intervalOffset=0.15):     # 参数clicks是点击次数， interval是两次点击的时间间隔， intervalOffset是点击的时间间隔的偏移值，使每两次点击的时间间隔不一样
    for i in range( 0, clicks):
        pag.click( button='right')
        fFakeTime( 's', interval - intervalOffset, interval + intervalOffset)

def fScroll( min, max):     # 参数1是最小值，参数2是最大值  pyautogui的滚动一次到位，要改成循环步进
    if min > max:
        pag.alert(text='Scroll 参数1 > 参数2', title='错误')
        return 0
    fakeScrollNum = random.randint( min, max)
    fakeCountAbs = abs(fakeScrollNum // 30)
    if fakeScrollNum >= 0:
        for i in range( 0, fakeCountAbs):
            pag.scroll(30)
            fFakeTime( 's', 0.1, 0.3)
    else:
        for i in range( 0, fakeCountAbs):
            pag.scroll( -30)
            fFakeTime( 's', 0.1, 0.3)
    return fakeScrollNum

def fMouseDown():
    pag.mouseDown()

def fMouseUp():
    pag.mouseUp()

def fTypeWrite( strParam):
    for i in strParam:
        pag.keyDown( i)
        # fFakeTime( 's', 0.05, 0.1)
        pag.keyUp( i)
        fFakeTime( 's', 0.1, 0.5)
    return strParam

def fKeyDown( strParam):
    pag.keyDown( strParam)
    return strParam

def fKeyUp( strParam):
    pag.keyUp( strParam)
    return strParam

# 定义时间操作
# timeType是时间类型字符串，s是秒，m是分，h是小时。min是最短的s/m/h。 max是最大的s/m/h
# twActions表格中的操作参数1是min， 操作参数2是max
def fFakeTime(timeType, min=1.0, max=10.0):  
    fakeTimeNum = random.uniform( min, max)
    if timeType == 's':
        time.sleep( fakeTimeNum)
    elif timeType == 'm':
        time.sleep( fakeTimeNum*60)
    elif timeType == 'h':
        time.sleep( fakeTimeNum*3600)
    else:
        pag.alert( title='错误', text='FakeTime操作参数1  时间单位应该是秒s，分m，小时h')
    fakeTimeNum = round( fakeTimeNum, 2)
    return fakeTimeNum



class KeyGhost( QMainWindow, Ui_KeyGhost): 
    #定义一个信号，用于子线程给主线程发信号
    signalCrossThread = pyqtSignal(str, str)     #两个str参数，第一个接收信号类型，第二个接收信号内容

    def __init__(self,parent =None):
        super( KeyGhost,self).__init__(parent)
        self.setupUi(self)

        # 初始化保存操作信息的表格
        tempHeaderText = ['操作类型', 'X', 'Y', 'X偏移', 'Y偏移', '时长', '时长偏移', '操作参数1', '操作参数2', '操作参数3', '备注']
        self.twActions.setColumnCount( len(tempHeaderText))
        self.twActions.setHorizontalHeaderLabels( tempHeaderText)
        self.twActions.setColumnWidth( 0, 150)
        for i in range(1,6):
            self.twActions.setColumnWidth( i, 60)

        #打开配置文件，初始化界面数据
        if os.path.exists( "./KeyGhost.ini"):
            try:
                iniFileDir = os.getcwd() + "\\"+ "KeyGhost.ini"
                with open( iniFileDir, 'r', encoding="utf-8") as iniFile:
                    iniDict = json.loads( iniFile.read())
                if iniDict:
                    if os.path.exists( iniDict['kgDir']):   # 如果脚本文件位置信息存在，则用mfRefresh()初始化界面
                        self.labelDir.setText( iniDict['kgDir'])
                        self.sbCount.setValue( iniDict['count'])
                        self.sbInterval.setValue( iniDict['interval'])

                        self.mfRefresh( iniDict['kgDir'])    
                    else:
                        QMessageBox.about( self, '提示', '配置文件KeyGhost.ini中的kgDir脚本文件位置错误或文件不存在')
            except:
                QMessageBox.about( self, "提示", "打开初始化文件KeyGhost.ini异常, 软件关闭时会自动重新创建KeyGhost.ini文件")

        # 绑定槽函数
        self.btnOpen.clicked.connect( self.mfOpen)
        self.btnSave.clicked.connect( self.mfSave)
        self.btnAdd.clicked.connect( self.mfAdd)
        self.btnDelete.clicked.connect( self.mfDelete)
        self.btnClearActions.clicked.connect( self.mfClearActions)
        self.btnQuit.clicked.connect( self.mfQuit)
        self.btnStart.clicked.connect( self.mfStart)
        self.btnStop.clicked.connect( self.mfStop)
        self.btnHelp.clicked.connect( self.mfHelp)
        self.btnClearLog.clicked.connect( self.mfClearLog)


        self.signalCrossThread.connect( self.mfSignal)       # 处理子线程给主线程发的信号

    # 槽函数定义
    # 点击使用帮助
    def mfHelp( self):
        QMessageBox.about( self, '使用帮助', 
        '1.点击退出按钮会保存操作表格中的数据，点击右上角叉号退出不会保存表格数据。  \
         \n2.FakeTime是随机时间, 操作参数1是时间类型 s是秒, m是分钟, h是小时。 操作参数2是最短时间值, 操作参数3是最长时间值 \
         \n3.ClickLeftMulti是多次点击左键，操作参数1是点击次数，操作参数2是点击时间间隔，单位秒s。参数3是间隔的时间偏移 \
         \n4.Scroll滚轮滚动(游戏慎用) 操作参数1是滚动最小值， 操作参数2是滚动最大值，正数向上滚动，负数向下滚动，只接收一个整数。 \
         \n5.尽量不要用Click，用MouseDown，MouseUp代替 \
         \n6.操作列表中数据不能为空，没有数据的要填上0，否则保存时会出现异常 \
         '
         )


    # 处理子线程给主线程发的信号, 信号signalType是字符串'QMessageBox' 'Display' 
    def mfSignal( self, signalType, content):
        if signalType == 'QMessageBox':
            QMessageBox.about( self, "提示", content)

        elif signalType == 'Display':
            self.teLog.append( content)


    # 定义 传入脚本文件位置，打开脚本文件，刷新软件界面
    def mfRefresh( self, paramDir):
        global ACTIONLIST
        # self.twActions.clearContents()    这个只清空数据，会留下空白的行. 这里需要清空所有行
        for i in range( 0, self.twActions.rowCount()):
            self.twActions.removeRow(0)

        with open( paramDir, 'r', encoding="utf-8") as kgFile:
            kgDict = json.loads( kgFile.read())
            if kgDict:
                i = 0 
                for key in kgDict:
                    self.twActions.insertRow( self.twActions.rowCount())
                    tempComboBox =  QComboBox()
                    tempComboBox.addItems( ACTIONLIST)
                    self.twActions.setCellWidget( i, 0, tempComboBox)
                    tempComboBox.setCurrentText( kgDict[key]['type'])
                    self.twActions.setItem( i, 1, QTableWidgetItem( str(kgDict[key]['X'])))
                    self.twActions.setItem( i, 2, QTableWidgetItem( str(kgDict[key]['Y'])))
                    self.twActions.setItem( i, 3, QTableWidgetItem( str(kgDict[key]['XOffset'])))
                    self.twActions.setItem( i, 4, QTableWidgetItem( str(kgDict[key]['YOffset'])))
                    self.twActions.setItem( i, 5, QTableWidgetItem( str(kgDict[key]['duration'])))
                    self.twActions.setItem( i, 6, QTableWidgetItem( str(kgDict[key]['durationOffset'])))
                    self.twActions.setItem( i, 7, QTableWidgetItem( str(kgDict[key]['actionParam1'])))
                    self.twActions.setItem( i, 8, QTableWidgetItem( str(kgDict[key]['actionParam2'])))
                    self.twActions.setItem( i, 9, QTableWidgetItem( str(kgDict[key]['actionParam3'])))
                    self.twActions.setItem( i, 10, QTableWidgetItem( str(kgDict[key]['actionNote'])))

                    i = i + 1


    # 定义 打开(脚本文件.kg), 获得文件位置，并传递文件位置给mfRefresh()，用来刷新界面
    def mfOpen( self):
        try:
            tempDir, uselessFilt = QFileDialog.getOpenFileName( self, '选择脚本文件', os.getcwd(), '脚本文件(*.kg)', '脚本文件(*.kg)')
            if tempDir != '':
                self.labelDir.setText( tempDir)
                self.mfRefresh( tempDir)
            else:
                QMessageBox.about( self, "提示", "请选择后缀名为 .kg 的脚本文件。")
        except:
            QMessageBox.about( self, "提示", "打开脚本文件失败，请重新选择。")


    #定义 保存界面上的数据
    def mfSave(self):
        saveDict = {}
        for i in range( 0, self.twActions.rowCount()):
            saveKey = 'action' + str(i+1)
            tempDict = {}
            tempDict['type'] = self.twActions.cellWidget( i, 0).currentText()
            tempDict['X'] = self.twActions.item( i, 1).text()
            tempDict['Y'] = self.twActions.item( i, 2).text()
            tempDict['XOffset'] = self.twActions.item( i, 3).text()
            tempDict['YOffset'] = self.twActions.item( i, 4).text()
            tempDict['duration'] = self.twActions.item( i, 5).text()
            tempDict['durationOffset'] = self.twActions.item( i, 6).text()
            tempDict['actionParam1'] = self.twActions.item( i, 7).text()
            tempDict['actionParam2'] = self.twActions.item( i, 8).text()
            tempDict['actionParam3'] = self.twActions.item( i, 9).text()
            tempDict['actionNote'] = self.twActions.item( i, 10).text()

            saveDict[saveKey] = tempDict
        
        saveJson = json.dumps( saveDict, indent=4)
        try:
            with open( self.labelDir.text(), 'w', encoding="utf-8") as saveFile:
                saveFile.write( saveJson)
        except:
            QMessageBox.about( self, "提示", "保存脚本文件失败")

    #给twActions表格添加一个空的行，用来添加新的操作
    def mfAdd( self):
        global ACTIONLIST
        self.twActions.insertRow( self.twActions.rowCount())
        tempComboBox =  QComboBox()
        tempComboBox.addItems(ACTIONLIST)
        self.twActions.setCellWidget( self.twActions.rowCount()-1, 0, tempComboBox)
        tempComboBox.setCurrentText( 'Click')
        self.twActions.setItem( self.twActions.rowCount()-1, 1, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 2, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 3, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 4, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 5, QTableWidgetItem('1.5'))
        self.twActions.setItem( self.twActions.rowCount()-1, 6, QTableWidgetItem('0.4'))
        self.twActions.setItem( self.twActions.rowCount()-1, 7, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 8, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 9, QTableWidgetItem('0'))
        self.twActions.setItem( self.twActions.rowCount()-1, 10, QTableWidgetItem('备注'))

        self.twActions.scrollToBottom()     # twActions滚动到最后一行

    # 删除twActions当前所选的行
    def mfDelete( self):
        self.twActions.removeRow( self.twActions.currentRow())

    # 清空twActions中的所有内容
    def mfClearActions( self):
        for i in range( 0, self.twActions.rowCount()):
            self.twActions.removeRow(0)

    # 清空日志
    def mfClearLog( self):
        self.teLog.clear()

    # 退出程序
    def mfQuit( self):
        self.mfSave()
        app = QApplication.instance()
        app.quit()
        
    # 点击执行，运行脚本
    def mfStart( self):
        global ISRUN
        ISRUN = 1
        # 创建一个新线程
        inRunThreading = threading.Thread( target= self.mfRun)
        inRunThreading.start()
        self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  开始执行脚本 in mfStart()')

    # 点击停止，停止脚本运行
    def mfStop( self):
        global ISRUN
        ISRUN = 0
        self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  当前操作完成后，停止脚本')

    # 运行脚本， 核心代码**************************************************
    def mfRun( self):
        global ISRUN
        self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  开始 in mfRun()')
        for i in range( 0, self.sbCount.value()):
            for j in range( 0, self.twActions.rowCount()):
                tempDict = {}
                tempDict['type'] = self.twActions.cellWidget( j, 0).currentText()
                tempDict['X'] = self.twActions.item( j, 1).text()
                tempDict['Y'] = self.twActions.item( j, 2).text()
                tempDict['XOffset'] = self.twActions.item( j, 3).text()
                tempDict['YOffset'] = self.twActions.item( j, 4).text()
                tempDict['duration'] = self.twActions.item( j, 5).text()
                tempDict['durationOffset'] = self.twActions.item( j, 6).text()
                tempDict['actionParam1'] = self.twActions.item( j, 7).text()
                tempDict['actionParam2'] = self.twActions.item( j, 8).text()
                tempDict['actionPamra3'] = self.twActions.item( j, 9).text()
                tempDict['actionNote'] = self.twActions.item( j, 10).text()

                if tempDict['type'] == 'MoveTo':
                    moveToX, moveToY, moveToDuration, MoveToMoveType = fMoveTo( int(tempDict['X']), int(tempDict['Y']), int(tempDict['XOffset']), int(tempDict['YOffset']), float(tempDict['duration']), float(tempDict['durationOffset']))
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 MoveTo (' + str(moveToX) + ',' + str(moveToY) + ')  耗时 ' + str(moveToDuration) + '秒  移动方式 ' + str(MoveToMoveType ))
                    if ISRUN == 0:
                        return

                elif tempDict['type'] == 'MoveRel':
                    moveRelX, moveRelY, moveRelDuration, moveRelMoveType = fMoveRel( int(tempDict['X']), int(tempDict['Y']), int(tempDict['XOffset']), int(tempDict['YOffset']), float(tempDict['duration']), float(tempDict['durationOffset']))
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 MoveRel (' + str(moveRelX) + ',' + str(moveRelY) + ')  耗时 ' + str(moveRelDuration) + '秒  移动方式 ' + str(moveRelMoveType ))
                    if ISRUN == 0:
                        return

                elif tempDict['type'] == 'FakeTime':
                    # 操作参数1 是 时间类型s是秒, m是分钟, h是小时。 操作参数2是最短时间值， 操作参数3是最长时间值
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 FakeTime 等待时间开始，区间[' + tempDict['actionParam2'] + ',' + tempDict['actionPamra3'] + ']  单位' + tempDict['actionParam1'])
                    fakeTimeNum = fFakeTime( tempDict['actionParam1'], float(tempDict['actionParam2']), float(tempDict['actionPamra3']))
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 FakeTime 等待时间' + str(fakeTimeNum) + tempDict['actionParam1'] + '结束')
                    if ISRUN == 0:
                        return

                elif tempDict['type'] == 'ClickLeft':
                    fClickLeft()
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 ClickLeft' )
                    if ISRUN == 0:
                        return     

                elif tempDict['type'] == 'ClickRight':
                    fClickRight()
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 ClickRight' )
                    if ISRUN == 0:
                        return     

                elif tempDict['type'] == 'ClickLeftMulti':
                    # 操作参数1是点击的次数， 操作参数2是点击的时间间隔 单位是秒s, 操作参数3是时间间隔的偏移值
                    fClickLeftMulti( int(tempDict['actionParam1']), float(tempDict['actionParam2']), float( tempDict['actionPamra3']))
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 ClickLeftMulti  点击左键 ' + tempDict['actionParam1'] + '次  每次间隔 ' + tempDict['actionParam2'] + '秒  偏移 ' + tempDict['actionPamra3'] + '秒' )
                    if ISRUN == 0:
                        return     

                elif tempDict['type'] == 'ClickRightMulti':
                    # 操作参数1是点击的次数， 操作参数2是点击的时间间隔 单位是秒s, 操作参数3是时间间隔的偏移值
                    fClickRightMulti( int(tempDict['actionParam1']), float(tempDict['actionParam2']), float( tempDict['actionPamra3']))
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 ClickRightMulti  点击右键 ' + tempDict['actionParam1'] + '次  每次间隔 ' + tempDict['actionParam2'] + '秒  偏移 ' + tempDict['actionPamra3'] + '秒' )
                    if ISRUN == 0:
                        return  

                elif tempDict['type'] == 'Scroll':
                    # 操作参数1是滚动最小值， 操作参数2是滚动最大值，正数向上滚动，负数向下滚动，只接收一个整数。
                    fakeScrollNum = fScroll( int(tempDict['actionParam1']), int(tempDict['actionParam2']))
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 Scroll  鼠标滚动了 '+ str(fakeScrollNum) +'格' )
                    if ISRUN == 0:
                        return  

                elif tempDict['type'] == 'MouseDown':
                    fMouseDown()
                    fFakeTime( 's', 0.1, 0.5)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 MouseDown  鼠标按下' )
                    if ISRUN == 0:
                        return 

                elif tempDict['type'] == 'MouseUp':
                    fMouseUp()
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 MouseUp  鼠标松开' )
                    if ISRUN == 0:
                        return
                
                elif tempDict['type'] == 'TypeWrite':
                    # 操作参数1 是需要输入的字符串
                    strParam = fTypeWrite( tempDict['actionParam1'])
                    fFakeTime( 's', 0.2, 1.2)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 TypeWrite  输入 ' + strParam )
                    if ISRUN == 0:
                        return

                elif tempDict['type'] == 'KeyDown':
                    # 操作参数1 是需要输入的字符串
                    strParam = fKeyDown( tempDict['actionParam1'])
                    fFakeTime( 's', 0.1, 0.5)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 KeyDown 按下 ' + strParam )
                    if ISRUN == 0:
                        return

                elif tempDict['type'] == 'KeyUp':
                    # 操作参数1 是需要输入的字符串
                    strParam = fKeyUp( tempDict['actionParam1'])
                    fFakeTime( 's', 0.2, 0.9)
                    self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(j+1) + '行 KeyUp 松开 ' + strParam )
                    if ISRUN == 0:
                        return

            
            # 脚本执行一遍后 向日志窗口发送消息，并暂停时间 
            time.sleep( self.sbInterval.value())        
            self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  第' + str(i+1) + '次循环完成')
            # 再加一个随机时间
            fFakeTime( 's', 1, 10)

        self.signalCrossThread.emit( 'Display', datetime.datetime.now().strftime('%H:%M:%S') + '  全部执行完毕')


#主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = KeyGhost()
    myWin.show()

    appExit = app.exec_()
    #退出程序之前，保存界面上的设置
    tempDict = { 'kgDir':myWin.labelDir.text(), 'count':myWin.sbCount.value(), 'interval':myWin.sbInterval.value() }
    saveIniJson = json.dumps( tempDict, indent=4)
    try:
        saveIniFile = open( "./KeyGhost.ini", "w",  encoding="utf-8")
        saveIniFile.write( saveIniJson)
        saveIniFile.close()
    except:
        QMessageBox.about( myWin, "提示", "保存配置文件KeyGhost.ini失败")

    # 这一句特别重要, 程序是两个线程在运行, 关闭窗口只能结束主线程, 子线程还在运行. 
    # 创建子线程的标志ISRUN 一定要改成0, 子线程在检测ISRUN==0之后,就不再用Timer创建新的线程了
    ISRUN = 0

    sys.exit( appExit)
# sys.exit(app.exec_())  