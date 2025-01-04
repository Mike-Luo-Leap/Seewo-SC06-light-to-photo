import pyautogui as pag
import pygetwindow as pgw
import time
import PIL.Image
import sys
import pystray
import threading

# 加载图标
image = PIL.Image.open("icon.png")

stop_all = threading.Event()

def tray_icon_thread():
    def on_clicked():
        stop_all.set()
        icon.stop()
        sys.exit(0)

    icon = pystray.Icon("Seewo Light to Photo Helper", image, menu=pystray.Menu(pystray.MenuItem('Quit', on_clicked)))
    icon.run()

def monitoring_thread():
    while not stop_all.is_set():
        if "希沃视频展台" == pgw.getActiveWindowTitle():
            time.sleep(3)
            photoPosX, photoPosY = pag.locateCenterOnScreen("photo.png", confidence=0.8)
            while True:
                time.sleep(1)
                try:
                    lightPosX, lightPosY = pag.locateCenterOnScreen("lighted.png", confidence=0.8)
                    pag.leftClick(photoPosX, photoPosY)
                    pag.leftClick(lightPosX, lightPosY)
                except:
                    pass

tray_thread = threading.Thread(target=tray_icon_thread)
monitoring_thread = threading.Thread(target=monitoring_thread)

tray_thread.start()
monitoring_thread.start()

tray_thread.join()
monitoring_thread.join()