import requests
from retrying import retry
import time
from win11toast import notify
# from win10toast_click import ToastNotifier
# from winotify import Notification, audio
# import webbrowser
# import json


# roomId = "213"
roomID = ["213", "45104"]
wait_time = 60
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}


@retry(stop_max_attempt_number=5)
def get_live_status(roomid):
    url = "https://api.live.bilibili.com/room/v1/Room/room_init?id=" + roomid
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    return response.json()['data']['live_status']


def main():
    print("监听中……")
    i = 0
    ex = ""
    while True:
        if len(roomID) != 0:
            for rid in roomID[::-1]:
                try:
                    live_status = get_live_status(rid)
                    if live_status == 1:
                        if i == 0:
                            print("正常运行")
                        notify(rid + "开播提醒",
                               rid + "已经开播了",
                               button={'activationType': 'protocol',
                                       'arguments': "https://live.bilibili.com/" + rid,
                                       'content': '打开直播间'})
                        roomID.remove(rid)
                        i += 1
                    else:
                        if i == 0:
                            print("正常运行")
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
                break
        else:
            break


if __name__ == "__main__":
    main()


'''
def go():
    webbrowser.open_new_tab("https://live.bilibili.com/"+roomId)



def main():
    print("监听中……")
    url = "https://api.live.bilibili.com/room/v1/Room/room_init?id="+roomId
    i = 0
    toast = Notification(app_id="开播提醒",
                         title="已经开播了",
                         msg="已经开播了，点击打开直播间! >>",
                         launch="https://live.bilibili.com/" + roomId)
    toast.set_audio(audio.Default, loop=False)
    while True:
        if json.loads(requests.get(url).text)['data']['live_status'] == 1:
            # ToastNotifier().show_toast("开播提醒", "已经开播了", threaded=True, callback_on_click=go)
            toast.show()

            break
        else:
            if i == 0:
                print("当前未开播，继续监听……")
            i += 1
            time.sleep(60)


'''