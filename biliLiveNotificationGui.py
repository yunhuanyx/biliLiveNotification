import tkinter as tk
# import tkinter.ttk as ttk
import ttkbootstrap as ttk
# import tkinter.messagebox as tkmb
import ttkbootstrap.dialogs.dialogs as tkmb
import tkinter.font as tkfont
import webbrowser
from retrying import retry
# from winotify import Notification, audio
from win11toast import notify
import time
import pystray
from pystray import MenuItem, Menu
from PIL import Image, ImageTk
from pic2str import explode
from base64 import b64decode
from io import BytesIO
import threading
import requests
import re
import os


byte_data = b64decode(explode)
image_data = BytesIO(byte_data)
image = Image.open(image_data)
image.save(os.path.dirname(os.path.abspath(__file__)) + '\\imagetmp.png')
toast_icon = {
    'src': os.path.dirname(os.path.abspath(__file__)) + '\\imagetmp.png',
    'placement': 'appLogoOverride'
}
uid_img = []

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}

error_flag = 0

version = "v1.3.1"

listen_button_flag = 0
pause_flag = False
stop_flag = False


def center_window(w, h):
    # 获取屏幕 宽、高
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # 计算 x, y 位置
    x = (ws/2) - (w/2) - 20
    y = (hs/2) - (h/2) - 20
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))


def show_window():
    root.deiconify()


def quit_window():
    os.remove(os.path.dirname(os.path.abspath(__file__)) + '\\imagetmp.png')
    for uid in uid_img:
        os.remove(os.path.dirname(os.path.abspath(__file__)) + '\\' + uid + '_tmp.png')
    root.destroy()


def begin_listen():
    try:
        with open("./BLN.ini", 'r+') as fl:
            fl_text = fl.read()
        roomIdStr = re.search("roomID=(.*)", fl_text).group(1)
        if roomIdStr == "":
            root.after(0, lambda: tkmb.Messagebox.show_error(title="错误", message="房间号为空，请进入设置界面进行设置！"))
            raise RuntimeError("房间号为空")
        roomID = roomIdStr.split(',')
        # print(roomID)
        timeInterval = int(re.search("timeInterval=(.*)", fl_text).group(1))

        stateStr.set("状态：监听中，房间号为" + str(roomID))
        root.withdraw()
        listen.configure(text="暂停监听", bootstyle="warning-outline-toolbutton")
        global listen_button_flag
        listen_button_flag = 1
        try:
            listen_main(roomID, timeInterval)
        except Exception as e:
            listen.configure(text='开始监听', bootstyle="outline-toolbutton")
            listen_button_flag = 0
            stateStr.set("状态：空闲中")
            global stop_flag
            stop_flag = False
            wait_event.clear()
            info_text.config(state=tk.NORMAL)
            info_text.insert(tk.END,
                             time.strftime("%m-%d %H:%M:%S", time.localtime()) + '   '
                             + str(e) + '\n')
            info_text.config(state=tk.DISABLED)
            info_text.see(tk.END)
    except OSError:
        root.after(0, lambda: tkmb.Messagebox.show_error(title="错误", message="未找到配置文件，请进入设置界面进行设置！"))
        raise OSError("未找到文件")


def listen_thread():
    global pause_flag
    global listen_button_flag
    if listen_button_flag == 0:
        stopl.configure(state="normal")
        threading.Thread(target=begin_listen, name="listen", daemon=True).start()
    elif listen_button_flag == 1:
        pause_flag = True
        pause_event.clear()
        wait_event.set()
        listen.configure(text="恢复监听", bootstyle="outline-toolbutton")
        stopl.configure(state="disable")
        """info_text.config(state=tk.NORMAL)
        info_text.insert(tk.END,
                         time.strftime("%m-%d %H:%M:%S", time.localtime()) + '   '
                         + "已暂停监听" + '\n')
        info_text.config(state=tk.DISABLED)
        info_text.see(tk.END)"""
        listen_button_flag = 2
    else:
        pause_flag = False
        pause_event.set()
        listen.configure(text="暂停监听", bootstyle="warning-outline-toolbutton")
        stopl.configure(state="normal")
        info_text.config(state=tk.NORMAL)
        info_text.insert(tk.END,
                         time.strftime("%m-%d %H:%M:%S", time.localtime()) + '   '
                         + "已恢复监听" + '\n')
        info_text.config(state=tk.DISABLED)
        info_text.see(tk.END)
        listen_button_flag = 1


def stop_close():
    ext_yno = tkmb.Messagebox.yesno(title="退出程序", message="确定退出程序吗？", alert=True)
    if ext_yno:
        os.remove(os.path.dirname(os.path.abspath(__file__)) + '\\imagetmp.png')
        for uid in uid_img:
            os.remove(os.path.dirname(os.path.abspath(__file__)) + '\\' + uid + '_tmp.png')
        root.destroy()


def stop_listen():
    global stop_flag
    stop_flag = True
    wait_event.set()
    global listen_button_flag
    listen_button_flag = 0
    stopl.configure(state="disable")


def check_update():
    release_ver = requests.get('https://api.github.com/repos/yunhuanyx/biliLiveNotification/releases/latest').json()['tag_name']
    if version < release_ver:
        update_yon = tkmb.Messagebox.yesno(title="提示",
                                           message="当前版本为" + version
                                                   + ",\n有新版本" + release_ver + "可更新\n是否前往发布页?",
                                           alert=True)
        if update_yon:
            webbrowser.open("https://github.com/yunhuanyx/biliLiveNotification/releases")
    else:
        tkmb.Messagebox.show_info(title="已是最新版本", message="当前已是最新版本", alert=True)


def on_exit():
    root.withdraw()


@retry(stop_max_attempt_number=5)
def get_live_status(roomid):
    url = api + roomid
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    if response.json()['code'] != 0:
        raise RuntimeError(roomid + '直播间不存在')
    live_json = response.json()
    return_dict = {
        'live_status': live_json['data']['live_status'],
        'uid': live_json['data']['uid']
    }
    return return_dict


@retry(stop_max_attempt_number=3)
def get_streamer_info(uid):
    url = "https://api.live.bilibili.com/live_user/v1/Master/info?uid=" + str(uid)
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    streamer_json = response.json()
    return_dict = {
        'uname': streamer_json['data']['info']['uname'],
        'face': streamer_json['data']['info']['face']
    }
    return return_dict


def get_streamer_img(url, uid):
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    uimg = Image.open(BytesIO(response.content))
    uimg_src = os.path.dirname(os.path.abspath(__file__)) + '\\' + uid + '_tmp.png'
    uimg.save(uimg_src)
    return uimg_src


def listen_main(roomID, wait_time):
    i = 0
    ex = ""
    while True:
        if stop_flag:
            raise RuntimeError("停止监听")
        if pause_flag:
            info_text.config(state=tk.NORMAL)
            info_text.insert(tk.END,
                             time.strftime("%m-%d %H:%M:%S", time.localtime()) + '   '
                             + "已暂停监听" + '\n')
            info_text.config(state=tk.DISABLED)
            info_text.see(tk.END)
            wait_event.clear()
            pause_event.wait()
        if len(roomID) != 0:
            for rid in roomID[::-1]:
                try:
                    live_dict = get_live_status(rid)
                    live_status = live_dict['live_status']
                    uid = live_dict['uid']
                    if live_status == 1:
                        if i == 0:
                            '''toastL = Notification(app_id="bilibili_Live_Notification",
                                                  title="bilibili_Live_Notification",
                                                  msg="开始监听")
                            toastL.set_audio(audio.Default, loop=False)
                            toastL.show()'''

                            notify("bilibili_Live_Notification", "开始监听", icon=toast_icon)

                        '''toastO = Notification(app_id=rid + "开播提醒",
                                             title=rid + "已经开播了",
                                             msg="已经开播了，点击打开直播间！ >>",
                                             launch="https://live.bilibili.com/" + rid)
                        toastO.set_audio(audio.Default, loop=False)
                        toastO.show()'''

                        uinfo_dict = get_streamer_info(uid)
                        uname = uinfo_dict['uname']
                        face = uinfo_dict['face']
                        uimg_url = get_streamer_img(face, str(uid))
                        notify(uname + "(" + rid + ")" + "开播提醒",
                               uname + "(" + rid + ")" + "已经开播了",
                               icon=uimg_url,
                               button={'activationType': 'protocol',
                                       'arguments': "https://live.bilibili.com/" + rid,
                                       'content': '打开直播间'})
                        info_text.config(state=tk.NORMAL)
                        info_text.insert(tk.END,
                                         time.strftime("%m-%d %H:%M", time.localtime()) + '   '
                                         + uname + "(" + rid + ")" + "已开播" + '\n')
                        info_text.config(state=tk.DISABLED)
                        info_text.see(tk.END)
                        if str(uid) not in uid_img:
                            uid_img.append(str(uid))
                        roomID.remove(rid)
                        stateStr.set("状态：监听中，房间号为" + str(roomID))
                        i += 1
                    else:
                        if i == 0:
                            notify("bilibili_Live_Notification", "开始监听", icon=toast_icon)
                        i += 1
                except Exception as e:
                    ex = e
                    info_text.config(state=tk.NORMAL)
                    info_text.insert(tk.END, str(e) + '\n')
                    info_text.config(state=tk.DISABLED)
                    info_text.see(tk.END)
                    # print(e)

            if stop_flag:
                raise RuntimeError("停止监听")
            if ex != "":
                ex = ""
                wait_event.wait(5)
                continue
            if len(roomID) != 0:
                wait_event.wait(wait_time)
            else:
                raise RuntimeError("监听结束")
        else:
            raise RuntimeError("监听结束")


class SettingWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title('设置')
        self.resizable(False, False)
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        w = 400
        h = 200
        x = (ws / 2) - (w / 2) - 20
        y = (hs / 2) - (h / 2) - 20
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        with open("./BLN.ini", 'r+') as fw:
            fw_text = fw.read()

        if re.search("roomID=(.*)", fw_text) == "":
            self.idStr = ""
        else:
            self.idStr = re.search("roomID=(.*)", fw_text).group(1)

        # print(self.idStr)
        self.timeInt = tk.StringVar(value=re.search("timeInterval=(.*)", fw_text).group(1))
        # print(self.timeInt.get())

        self.idText = tk.Text(self, width=50, height=3, relief=tk.SUNKEN)
        self.setUI()

    def setUI(self):

        self.idText.insert('0.0', self.idStr)
        self.idText.place(x=20, y=35)

        ttk.Label(self, text="房间号——用\",\"隔开（例：213,77386）").place(x=20, y=10)

        timeEntry = ttk.Entry(self, width=7, justify=tk.CENTER, textvariable=self.timeInt)
        timeEntry.place(x=150, y=105)
        ttk.Label(self, text="监听间隔（单位：秒）").place(x=20, y=108)
        saveSetting = ttk.Button(self, text='保存', command=self.save_setting)
        saveSetting.place(x=90, y=150)
        cancelSet = ttk.Button(self, text='取消并关闭', command=self.cancel_setting)
        cancelSet.place(x=210, y=150)

    def save_setting(self):
        idStr = self.idText.get('0.0', tk.END).replace('，', ',').replace('\n', '')
        # print(idStr)
        timeIntStr = self.timeInt.get()

        with open("./BLN.ini", "r") as f1s, open("./BLN.tmp", "w") as f2s:
            strTmp = re.sub("roomID=(.*)", "roomID=" + idStr, f1s.read())
            f2s.write(re.sub("timeInterval=(.*)", "timeInterval=" + timeIntStr, strTmp))
        os.remove("./BLN.ini")
        os.rename("./BLN.tmp", "BLN.ini")

        self.destroy()

    def cancel_setting(self):
        self.destroy()


root = tk.Tk()

root.title('B站开播提醒'+version)
center_window(395, 200)
root.resizable(False, False)
root.protocol('WM_DELETE_WINDOW', root.iconify)
ico_img = ImageTk.PhotoImage(data=byte_data)
root.iconphoto(True, ico_img)
listen = ttk.Button(root, text='开始监听', width=8, command=listen_thread, bootstyle="outline-toolbutton")
listen.place(x=10, y=10)
stopl = ttk.Button(root, text='停止监听', width=7, command=stop_listen, state="disable", bootstyle="danger-outline-toolbutton")
stopl.place(x=95, y=10)
config = ttk.Button(root, text='设置', width=6, command=SettingWindow, bootstyle="info-outline-toolbutton")
config.place(x=172, y=10)
update = ttk.Button(root, text='检查更新', width=7, command=check_update, bootstyle="outline-toolbutton")
update.place(x=242, y=10)
ext = ttk.Button(root, text='退出', width=6, command=stop_close, bootstyle="danger-outline-toolbutton")
ext.place(x=319, y=10)
ttk.Separator(root, orient=tk.HORIZONTAL).place(x=5, y=45, relwidth=0.97)
stateStr = tk.StringVar(value="状态：空闲中")
state = ttk.Label(root, textvariable=stateStr, wraplength=410).place(x=10, y=46)

info_scr = ttk.Scrollbar(root, bootstyle="round")
info_text = tk.Text(root, width=44, height=5, bd=1,
                    font=tkfont.Font(family="Microsoft YaHei", size=10),
                    yscrollcommand=info_scr.set, state=tk.DISABLED)
info_scr.config(command=info_text.yview)
info_scr.place(x=380, y=84, height=111)
info_text.place(x=9, y=85)

menu = (MenuItem('显示', show_window, default=True), Menu.SEPARATOR, MenuItem('退出', quit_window))
icon = pystray.Icon("name", image, "开播提醒", menu)

root.protocol('WM_DELETE_WINDOW', on_exit)
threading.Thread(target=icon.run, name="stray", daemon=True).start()

pause_event = threading.Event()
wait_event = threading.Event()


try:
    with open("./BLN.ini", 'r+') as fp:
        lst = fp.read()
    matchObj = re.match("api=(.*)", lst)
    st1 = re.search("roomID=(.*)", lst)
    st2 = re.search("timeInterval=(.*)", lst)
    if st1 is None or st2 is None:
        raise AttributeError
    api = matchObj.group(1)
    if api == "":
        with open("./BLN.ini", "r") as f1, open("./BLN.tmp", "w") as f2:
            f2.write(re.sub("api=(.*)", "api=https://api.live.bilibili.com/room/v1/Room/room_init?id=", f1.read()))
        os.remove("./BLN.ini")
        os.rename("./BLN.tmp", "BLN.ini")
        api = "https://api.live.bilibili.com/room/v1/Room/room_init?id="
except FileNotFoundError:
    with open("./BLN.ini", 'w') as fp:
        fp.write("api=https://api.live.bilibili.com/room/v1/Room/room_init?id=" + "\n"
                 + "roomID=" + "\n" + "timeInterval=60")
    api = "https://api.live.bilibili.com/room/v1/Room/room_init?id="
except AttributeError:
    with open("./BLN.ini", "w") as f1, open("./BLNback.txt", "w") as f2:
        f2.write(lst)
        f1.write("api=https://api.live.bilibili.com/room/v1/Room/room_init?id=" + "\n"
                 + "roomID=" + "\n" + "timeInterval=60")
    api = "https://api.live.bilibili.com/room/v1/Room/room_init?id="
    error_flag = 1

if error_flag == 1:
    tkmb.Messagebox.show_warning(title="警告", message="配置文件有误，已生成新配置文件，原配置内容可在同目录\"BLNback.txt\"中找到")


root.mainloop()
