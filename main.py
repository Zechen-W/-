import multiprocessing.connection
import threading
from multiprocessing import Queue
import numpy as np
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

n_max_threads = 4
loops = 2
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"


def watchVideo(browser: webdriver.Chrome,
               video: webdriver.remote.webelement.WebElement,
               io: multiprocessing.Queue,
               token: multiprocessing.Queue):
    print('this is in a thread')
    print(browser, video, io, token, sep='\n')
    io.get()
    token.get()
    video.click()
    time.sleep(10)
    this_window = browser.window_handles[-1]
    browser.switch_to.window(this_window)
    try:
        video_zone = browser.find_element_by_class_name('cf')
        action = ActionChains(browser)
        action.move_to_element(video_zone).perform()
        speed = browser.find_element_by_class_name('xt_video_player_common_value')
        action.move_to_element(speed).perform()
        speed2 = browser.find_element_by_xpath(
            '//*[@id="video-box"]/div/xt-wrap/xt-controls/xt-inner/xt-speedbutton/xt-speedlist/ul/li[1]')
        action.move_to_element(speed2).perform()
        time.sleep(3)
        speed2.click()
        time.sleep(3)
        action.move_to_element(video_zone).perform()
        end_time = browser.find_element_by_xpath(
            '//*[@id="video-box"]/div/xt-wrap/xt-controls/xt-inner/xt-time/span[2]')
        begin_time = browser.find_element_by_xpath('//*[@id="video-box"]/div/xt-wrap/xt-controls/xt-inner/xt-time'
                                                   '/span[1]')
        begin_time, end_time = begin_time.text.split(':'), end_time.text.split(':')
        sleep_time = [int(i) for i in (begin_time + end_time)]
        sleep_time = np.dot(sleep_time, [-3600, -60, -1, 3600, 60, 1]) / 2
        browser.switch_to.window(browser.window_handles[0])
        token.put('token line')
        print('sleep time:', sleep_time, sep='\n')
        print('gonna sleep')
        time.sleep(sleep_time)
    except:
        print('exception occurred')
        browser.switch_to.window(browser.window_handles[0])
        token.put('token line')

    token.get()
    browser.switch_to.window(this_window)
    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    time.sleep(1)
    token.put('token line')
    io.put('io line')


def main():
    # config
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path

    browser = webdriver.Chrome('./chromedriver.exe', options=options)
    browser.get('https://bupt.yuketang.cn/pro/lms/84hxA9Q7Bn5/7899241/studycontent')
    time.sleep(3)
    # login. you have 20 seconds to scan the QR code with your phone to login.
    # you can also fine-tune the code to add or decrease the time.
    browser.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div[3]/div/div[1]/div/div/div[2]/button/span').click()
    time.sleep(20)

    browser.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/div[3]/div/ul/li[4]').click()
    time.sleep(10)

    fifo = Queue()
    token = Queue()
    for i in range(n_max_threads):
        fifo.put('a line')

    token.put('token')

    for loop in range(loops):
        threads = []
        videos = browser.find_elements_by_class_name('unit-name-hover')[:123]
        texts = [i.text for i in browser.find_elements_by_class_name('concrete-tr')][:123]
        print('videos:', videos, sep='\n')
        for video, text in zip(videos, texts):
            if '单元作业' in text or '已完成' in text:
                continue

            thread = threading.Thread(target=watchVideo, args=(browser, video, fifo, token))
            thread.start()
            print('a new thread started')
            threads.append(thread)
            print('threads:', threads, sep='\n')
        # set time out in seconds. the parameter should be greater than length of any video to watch.
        for thread in threads:
            thread.join(60 * 60)
        browser.refresh()
        time.sleep(30)


if __name__ == '__main__':
    main()
