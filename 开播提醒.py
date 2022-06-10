import requests
from retrying import retry
import time
from winotify import Notification, audio


roomID = ["213"]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 YaBrowser/19.7.0.1635 Yowser/2.5 Safari/537.36"}


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
                time.sleep(60)
            else:
                break
        else:
            break


if __name__ == "__main__":
    main()
