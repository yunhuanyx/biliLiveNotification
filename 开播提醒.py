import requests
import time
from winotify import Notification, audio
import json


roomID = ["213"]


def main():
    print("监听中……")
    i = 0
    url = "https://api.live.bilibili.com/room/v1/Room/room_init?id="
    while True:
        if len(roomID) != 0:
            for rid in roomID[::-1]:
                if json.loads(requests.get(url+rid).text)['data']['live_status'] == 1:
                    if i == 0:
                        print("正常运行")
                    toast = Notification(app_id=rid+"开播提醒",
                                         title=rid+"已经开播了",
                                         msg="已经开播了，点击打开直播间！ >>",
                                         launch="https://live.bilibili.com/" + rid)
                    toast.set_audio(audio.Default, loop=False)
                    toast.show()
                    roomID.remove(rid)
                    # print(len(roomID))
                    i += 1
                else:
                    if i == 0:
                        print("正常运行")
                    i += 1

            if len(roomID) != 0:
                time.sleep(60)
            else:
                break
        else:
            break


if __name__ == "__main__":
    main()
