import pyautogui as pag
import pygetwindow as pgw
import time
import PIL.Image
import sys
import pystray
import threading
import numpy as np
import cv2
import traceback
import logging  # 新增导入

# 加载图标
image = PIL.Image.open("icon.png")

stop_all = threading.Event()
monitoring_running = True  # 将默认状态置为 True

# 配置日志记录
logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def captureScreen(region = None):
    return cv2.cvtColor(np.array(pag.screenshot(region=region)), cv2.COLOR_RGB2BGR)

def detectClarity(image):
    return cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), cv2.CV_64F).var()

# 新增 safe_locate 函数：包装 locateCenterOnScreen，找不到图片时返回 None
def safe_locate(image_path, confidence=0.8):
    try:
        return pag.locateCenterOnScreen(image_path, confidence=confidence)
    except pag.ImageNotFoundException:
        return None
    except Exception:
        return None

def tray_icon_thread():
    def on_start(icon, item):
        global monitoring_running
        monitoring_running = True

    def on_stop(icon, item):
        global monitoring_running
        monitoring_running = False

    def on_quit(icon, item):
        stop_all.set()
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem('开始', on_start),
        pystray.MenuItem('停止', on_stop),
        pystray.MenuItem('退出', on_quit)
    )
    icon = pystray.Icon("Seewo Light to Photo Helper", image, menu=menu)
    icon.run()

def monitoring_thread():
    while not stop_all.is_set():
        try:
            try:
                active_title = pgw.getActiveWindowTitle()
            except Exception:
                active_title = ""
            if monitoring_running:
                if active_title == "希沃视频展台":
                    time.sleep(3)
                    photoPos = safe_locate("photo.png", confidence=0.8)
                    if photoPos is None:
                        time.sleep(1)
                        continue
                    while monitoring_running and not stop_all.is_set():
                        time.sleep(1)
                        lightPos = safe_locate("lighted.png", confidence=0.8)
                        if lightPos is None:
                            continue
                        if detectClarity(captureScreen((760, 340, 400, 400))):
                            pag.leftClick(photoPos)
                            pag.leftClick(lightPos)
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
        except Exception:
            logging.error(traceback.format_exc())
            # 忽略错误继续执行

tray_thread = threading.Thread(target=tray_icon_thread)
monitoring_thread = threading.Thread(target=monitoring_thread)

tray_thread.start()
monitoring_thread.start()

tray_thread.join()
monitoring_thread.join()
