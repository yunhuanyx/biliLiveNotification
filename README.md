# biliLiveNotification
b站直播开播提醒  
需要[winotify](https://github.com/versa-syahptr/winotify)和[retrying](https://github.com/rholder/retrying)模块  
在roomID列表中填入想要提醒的直播间房间号即可运行，可填写多个  
修改wait_time的值可修改监听间隔时间，默认60s监听一次  
监听到开播后会生成win10通知，点击通知可在浏览器中开启直播间  
