# biliLiveNotification
## b站直播开播提醒  
***
### py脚本版  
需要[winotify](https://github.com/versa-syahptr/winotify)和[retrying](https://github.com/rholder/retrying)模块
在roomID列表中填入想要提醒的直播间房间号即可运行，可填写多个  
修改wait_time的值可修改监听间隔时间，默认60s监听一次  
监听到开播后会生成win10通知，点击通知可在浏览器中开启直播间  
***
### Releases版（exe文件）  
可直接运行  
在设置界面填写想要提醒的直播间房间号，多个房间号用“,”隔开  
监听间隔默认60s，有需要可以在设置界面更改，不建议设置间隔太短  
设置完成后点“开始监听”即可进行监听，开播后会生成win10通知，点击通知即可前往直播间  
需要退出程序时点击界面中的“停止 & 退出”按钮，或者右键托盘图标点击菜单中的“退出”，界面中的“X”只能最小化到托盘    
