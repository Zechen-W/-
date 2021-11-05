import multiprocessing.connection
import threading
from multiprocessing import Pipe
import numpy as np
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

n_max_threads = 4
loops = 2


def watchVideo(browser: webdriver.Chrome,
               video: webdriver.remote.webelement.WebElement,
               io_sender: multiprocessing.connection.Connection,
               io_receiver: multiprocessing.connection.Connection,
               token_sender: multiprocessing.connection.Connection,
               token_receiver: multiprocessing.connection.Connection):
    print('this is in a thread')
    print(browser, video, io_sender, token_sender, sep='\n')
    io_receiver.recv()
    token_receiver.recv()
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
        # time.sleep(0.1)
        speed2 = browser.find_element_by_xpath(
            '//*[@id="video-box"]/div/xt-wrap/xt-controls/xt-inner/xt-speedbutton/xt-speedlist/ul/li[1]')
        action.move_to_element(speed2).perform()
        time.sleep(3)
        speed2.click()
        time.sleep(3)
        end_time = browser.find_element_by_xpath(
            '//*[@id="video-box"]/div/xt-wrap/xt-controls/xt-inner/xt-time/span[2]')
        begin_time = browser.find_element_by_xpath('//*[@id="video-box"]/div/xt-wrap/xt-controls/xt-inner/xt-time'
                                                   '/span[1]')
        begin_time, end_time = begin_time.text.split(':'), end_time.text.split(':')
        sleep_time = [int(i) for i in (begin_time + end_time)]
        sleep_time = np.dot(sleep_time, [-3600, -60, -1, 3600, 60, 1]) / 2
        browser.switch_to.window(browser.window_handles[0])
        token_sender.send('token line')
        print('sleep time:', sleep_time, sep='\n')
        print('gonna sleep')
        time.sleep(sleep_time)
    except:
        print('exception occurred')
        browser.switch_to.window(browser.window_handles[0])
        token_sender.send('token line')

    token_receiver.recv()
    browser.switch_to.window(this_window)
    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    time.sleep(1)
    token_sender.send('token line')
    io_sender.send('io line')


def main():
    options = webdriver.ChromeOptions()
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

    browser = webdriver.Chrome('./chromedriver.exe', options=options)
    browser.get('https://bupt.yuketang.cn/pro/lms/84hxA9Q7Bn5/7899241/studycontent')
    time.sleep(3)
    browser.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div[3]/div/div[1]/div/div/div[2]/button/span').click()
    time.sleep(20)

    browser.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/div[3]/div/ul/li[4]').click()
    time.sleep(10)
    videos = browser.find_elements_by_class_name('unit-name-hover')[:123]
    texts = [i.text for i in browser.find_elements_by_class_name('concrete-tr')][:123]

    fifo_receiver, fifo_sender = Pipe(False)
    token_receiver, token_sender = Pipe(False)
    for i in range(n_max_threads):
        fifo_sender.send('a line')
    token_sender.send('token line')
    threads = []
    print('videos:', videos, sep='\n')
    for loop in range(loops):
        for video, text in zip(videos, texts):
            if '单元作业' in text or '已完成' in text:
                continue

            thread = threading.Thread(target=watchVideo, args=(browser, video, fifo_sender, fifo_receiver,
                                                               token_sender, token_receiver))
            thread.start()
            print('a new thread started')
            threads.append(thread)
            print('threads:', threads, sep='\n')
        for thread in threads:
            thread.join(60 * 60)
        browser.refresh()
        time.sleep(10)


if __name__ == '__main__':
    main()
