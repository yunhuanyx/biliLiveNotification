import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmb
from retrying import retry
from winotify import Notification, audio
import time
import pystray
from pystray import MenuItem, Menu
from PIL import Image, ImageTk
from pic2str import explode
from base64 import b64decode
from io import BytesIO
import threading
import requests


byte_data = b64decode(explode)
image_data = BytesIO(byte_data)
image = Image.open(image_data)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}


def center_window(w, h):
    # 获取屏幕 宽、高
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # 计算 x, y 位置
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))


def show_window():
    root.deiconify()


def quit_window():
    root.destroy()


def begin_listen():
    try:
        with open("./BLN.ini", 'r+') as fp:
            lst = fp.readlines()
        if lst[0] == "roomID=\n":
            tkmb.showerror(title="错误", message="房间号为空，请进入设置界面进行设置！")
            raise RuntimeError("房间号为空")
        roomIdStr = lst[0].split("=")[1].replace('\n', '')
        timeInterval = int(lst[1].split("=")[1])

        roomID = roomIdStr.split(',')

        stateStr.set("状态：监听中")
        root.withdraw()
        listen.config(state=tk.DISABLED)
        try:
            listen_main(roomID, timeInterval)
        except:
            listen.config(state=tk.NORMAL)
            stateStr.set("状态：空闲中")
            raise RuntimeError("监听结束")
    except OSError:
        tkmb.showerror(title="错误", message="未找到配置文件，请进入设置界面进行设置！")
        raise OSError("未找到文件")


def listen_thread():
    threading.Thread(target=begin_listen, name="listen", daemon=True).start()


def stop_close():
    root.destroy()


def on_exit():
    root.withdraw()


@retry(stop_max_attempt_number=5)
def get_live_status(roomid):
    url = "https://api.live.bilibili.com/room/v1/Room/room_init?id=" + roomid
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    return response.json()['data']['live_status']


def listen_main(roomID, wait_time):
    i = 0
    ex = ""
    while True:
        if len(roomID) != 0:
            for rid in roomID[::-1]:
                try:
                    live_status = get_live_status(rid)
                    if live_status == 1:
                        if i == 0:
                            toastL = Notification(app_id=" ",
                                                  title="bilibili_Live_Notification",
                                                  msg="开始监听")
                            toastL.set_audio(audio.Default, loop=False)
                            toastL.show()
                        toast = Notification(app_id=rid + "开播提醒",
                                             title=rid + "已经开播了",
                                             msg="已经开播了，点击打开直播间！ >>",
                                             launch="https://live.bilibili.com/" + rid)
                        toast.set_audio(audio.Default, loop=False)
                        toast.show()
                        roomID.remove(rid)
                        i += 1
                    else:
                        if i == 0:
                            toastL = Notification(app_id=" ",
                                                  title="bilibili_Live_Notification",
                                                  msg="开始监听")
                            toastL.set_audio(audio.Default, loop=False)
                            toastL.show()
                        i += 1
                except Exception as e:
                    ex = e
                    print(e)

            if ex != "":
                ex = ""
                time.sleep(5)
                continue
            if len(roomID) != 0:
                time.sleep(wait_time)
            else:
                raise RuntimeError("监听结束")
        else:
            raise RuntimeError("监听结束")


class settingWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title('设置')
        self.resizable(False, False)
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        w = 400
        h = 200
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        try:
            with open("./BLN.ini", 'r+') as fp:
                lst = fp.readlines()
            self.idStr = lst[0].split("=")[1].replace('\n', '')
            # print(self.idStr)
            self.timeInt = tk.StringVar(value=lst[1].split("=")[1])
            # print(self.timeInt.get())
        except:
            with open("./BLN.ini", 'w') as fp:
                fp.write("roomID=" + "\n" + "timeInterval=60")
            self.idStr = ""
            self.timeInt = tk.StringVar(value="60")

        self.idText = tk.Text(self, width=50, height=3, relief=tk.SUNKEN)
        self.setUI()

    def setUI(self):

        self.idText.insert('0.0', self.idStr)
        self.idText.place(x=20, y=35)

        ttk.Label(self, text="房间号——用\",\"隔开（例：213,77386）").place(x=20, y=10)

        timeEntry = tk.Entry(self, width=7, justify=tk.CENTER, textvariable=self.timeInt)
        timeEntry.place(x=150, y=100)
        ttk.Label(self, text="监听间隔（单位：秒）").place(x=20, y=100)
        saveSetting = ttk.Button(self, text='保存', command=self.save_setting)
        saveSetting.place(x=90, y=150)
        cancelSet = ttk.Button(self, text='取消并关闭', command=self.cancel_setting)
        cancelSet.place(x=210, y=150)

    def save_setting(self):
        idStr = self.idText.get('0.0', tk.END).replace('，', ',')
        timeIntStr = self.timeInt.get()
        with open("./BLN.ini", 'w') as fp:
            fp.write("roomID="+idStr+"timeInterval="+timeIntStr)
        self.destroy()

    def cancel_setting(self):
        self.destroy()


root = tk.Tk()
root.title('B站开播提醒')
center_window(285, 65)
root.resizable(False, False)
root.protocol('WM_DELETE_WINDOW', root.iconify)
ico_img = ImageTk.PhotoImage(data=byte_data)
root.iconphoto(True, ico_img)
listen = ttk.Button(root, text='开始监听', command=listen_thread)
listen.place(x=15, y=10)
config = ttk.Button(root, text='设置', width=7, command=settingWindow)
config.place(x=115, y=10)
ext = ttk.Button(root, text='停止 & 退出', command=stop_close)
ext.place(x=185, y=10)
ttk.Separator(root, orient=tk.HORIZONTAL).place(x=5, y=45, relwidth=0.97)
stateStr = tk.StringVar(value="状态：空闲中")
state = ttk.Label(root, textvariable=stateStr).place(x=10, y=46)

menu = (MenuItem('显示', show_window, default=True), Menu.SEPARATOR, MenuItem('退出', quit_window))
icon = pystray.Icon("name", image, "开播提醒", menu)

root.protocol('WM_DELETE_WINDOW', on_exit)
threading.Thread(target=icon.run, name="stray", daemon=True).start()

root.mainloop()

