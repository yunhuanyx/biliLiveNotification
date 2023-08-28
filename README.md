# biliLiveNotification
## b站直播开播提醒  
***
### py文件版  
* 需要[win11toast](https://github.com/GitHub30/win11toast)和[retrying](https://github.com/rholder/retrying)模块
* 在roomID列表中填入想要提醒的直播间房间号即可运行，可填写多个  
* 修改wait_time的值可修改监听间隔时间，默认60s监听一次  
* 监听到开播后会生成通知，点击通知中的按钮可在浏览器中开启直播间  
***
### Releases版（exe文件）  
* 可直接运行  
* 在设置界面填写想要提醒的直播间房间号，多个房间号用“,”隔开  
* 监听间隔默认60s，有需要可以在设置界面更改，不建议设置间隔太短  
* 设置完成后点“开始监听”即可进行监听，开播后会生成通知，点击通知中的按钮即可前往直播间  
* 界面中的“X”会最小化到托盘  
* 需要退出程序时请点击界面中的“停止 & 退出”按钮，或者右键托盘图标点击菜单中的“退出”  
## 通知效果如图所示
![Snipaste_2023-08-28_19-48-01](https://github.com/yunhuanyx/biliLiveNotification/assets/95404593/bf7359ac-069b-459a-9b9c-4eec6325e1fb) 
所用API均来自[bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)
