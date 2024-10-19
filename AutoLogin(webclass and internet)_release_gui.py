import time
import os
import tkinter as tk
#from tkinter import filedialog
import ctypes
import requests
#import queue
import threading
import cv2
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def make_cache_file(cache_dir = './WebClassLoginCache', cache_file_name = 'cache', root_path = ""):
    cache_path = os.path.join(root_path, cache_dir, cache_file_name + '.txt')
    cache_dir = os.path.join(root_path, cache_dir)
    if not os.path.exists(cache_path):
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(cache_path, 'w', encoding='utf-8') as file:
            file.write("")  # 创建空文件

def read_the_last_line_of_cache(cache_dir = './WebClassLoginCache', cache_file_name = 'cache'):
    """
    检查是否存在 ./WebClassLoginCache/cache.txt 文件，并读取最后一行内容。
    如果文件不存在，则创建文件并返回空字符串。
    
    :return: 文件的最后一行内容（如果存在），否则返回空字符串
    """
    cache_path = cache_dir + '/' + cache_file_name + '.txt'
    make_cache_file(cache_dir, cache_file_name)

    with open(cache_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    for line in reversed(lines):
        if line.find("今日规律学习目标完成!") != -1 or line.find("发生错误") != -1 or line.find("sudo") != -1:
            return line.strip()  # 返回最后一行内容并去除换行符
    console_log("Cache Not Found, Start From DeFault _1.1")
    return "[Warning] Cache Not Found, Start From DeFault _1.1"

def write_to_cache(message, cache_dir = './WebClassLoginCache', cache_file_name = 'cache'):
    """
    在 cache.txt 文件中追加当前时间和给定的消息，并在每条消息前换行。
    
    :param message: 要追加的消息字符串
    """
    cache_path = cache_dir + '/' + cache_file_name + '.txt'
    make_cache_file(cache_dir, cache_file_name)

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{current_time}: {message}\n"
    
    #print(log_message)
    console_log(log_message.strip())
    with open(cache_path, 'a', encoding='utf-8') as file:
        file.write(log_message)

def check_config(config_dict, root_path='C:/WebClassAutoLogin', cache_dir = './WebClassLoginCache', cache_file_name = 'user_config'):
    cache_path = os.path.join(root_path, cache_dir, cache_file_name + '.txt')
    make_cache_file(cache_dir, cache_file_name, root_path)

    with open(cache_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        if not line:  # 跳过空行
            continue
        type = ""
        for i, char in enumerate(line.strip()):
            if char == ':':
                data = line.strip()[i+1:]
                config_dict[type] = data
                break
            type += char
    if 'None' in config_dict.values(): 
        write_to_cache("[Warning] Missing config info!\n警告: 用户信息不完整")
        # for key in config_dict:
        #     if config_dict[key] == 'None':
        #         config_dict[key] = input("请输入缺失信息{}: ".format(key))
        #         write_config(key, config_dict[key])
        show_settings_popup(config_dict)

def write_config_dos(key, config_message, root_path='C:/WebClassAutoLogin', cache_dir = './WebClassLoginCache', cache_file_name = 'user_config'):
    cache_path = os.path.join(root_path, cache_dir, cache_file_name + '.txt')
    make_cache_file(cache_dir, cache_file_name, root_path)

    with open(cache_path, 'a', encoding='utf-8') as file:
        file.write("{}:{}\n".format(key, config_message))

def write_config_gui(config_dict, root_path='C:/WebClassAutoLogin', cache_dir = './WebClassLoginCache', cache_file_name = 'user_config'):
    cache_path = os.path.join(root_path, cache_dir, cache_file_name + '.txt')
    make_cache_file(cache_dir, cache_file_name, root_path)

    with open(cache_path, 'w', encoding='utf-8') as file:
        for key, value in config_dict.items():
            file.write("{}:{}\n".format(key, value))

def login_wisdom_tree(driver, config_dict):
    # # 切换到以“学校+学号”登录的方式(可直接访问https://passport.zhihuishu.com/login#studentID)
    # change_login_method_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/div[2]/div[1]/a[2]"))
    # )
    # change_login_method_button.click()

    # 依次填写学校、学号、密码
    school_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[1]/div/input[2]"))
    )
    school_name_input.send_keys(config_dict['school_name'])
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[1]/div/div/div/div[1]/ul/li[2]"))
    )
    login_button.click()

    student_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[2]/input"))
    )
    student_name_input.send_keys(config_dict['student_id'])

    pwd_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[3]/input"))
    )
    pwd_input.send_keys(config_dict['login_pwd'])

    # 找到登录按钮
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/span"))
    )
    login_button.click()

def save_image(driver):
    url_s = None
    url_b = None
    while(url_s is None or url_b is None):
        #print(url_s, url_b)
        time.sleep(1)
        # 小图片
        url_s = driver.find_element(By.CLASS_NAME, 'yidun_jigsaw').get_attribute('src')
        # 大图片
        url_b = driver.find_element(By.CLASS_NAME, 'yidun_bg-img').get_attribute('src')

    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

    # 发送请求，获取验证码图片
    response_s = requests.get(url_s, headers=header).content
    response_b = requests.get(url_b, headers=header).content

    # 判断文件夹是否存在不存在则创建'
    os.makedirs('./image/', exist_ok=True)
    # 保存图片
    with open('./image/slider_s.png', 'wb') as f:
        f.write(response_s)

    with open('./image/slider_b.png', 'wb') as f:
        f.write(response_b)

# 将两张图片先进行灰度处理，再对图像进行高斯处理，最后进行边缘检测
def handel_img(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)  # 转灰度图
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # 高斯模糊
    imgCanny = cv2.Canny(imgBlur, 60, 60)  # Canny算子边缘检测
    return imgCanny

# 将JPG图像转变为4通道（RGBA）
def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """
    r_channel, g_channel, b_channel = cv2.split(img)  # 剥离jpg图像通道
    # 创建Alpha通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
    # 融合通道
    img_new = cv2.merge((r_channel, g_channel, b_channel, alpha_channel))
    return img_new

# 读取图像
def match(img_s_path, img_b_path):
    # 读取图像
    img_jpg = cv2.imread(img_s_path, cv2.IMREAD_UNCHANGED)
    img_png = cv2.imread(img_b_path, cv2.IMREAD_UNCHANGED)
    # 判断jpg图像是否已经为4通道
    if img_jpg.shape[2] == 3:
        img_jpg = add_alpha_channel(img_jpg)
    img = handel_img(img_jpg)
    small_img = handel_img(img_png)
    res_TM_CCOEFF_NORMED = cv2.matchTemplate(img, small_img, 3)
    value = cv2.minMaxLoc(res_TM_CCOEFF_NORMED)
    value = value[3][0]  # 获取到移动距离
    return value

# 移动
def move(driver, distance):
    # 获取滑块元素
    #loc = 'div[class="yidun_slider  yidun_slider--hover "]'
    #ele = driver.find_element('css selector', loc)
    ele = driver.find_element(By.XPATH, "/html/body/div[33]/div[2]/div/div/div[2]/div/div[2]/div[2]")
    # 实例化对象
    action = ActionChains(driver)
    # 拖动滑块

    action.drag_and_drop_by_offset(ele, xoffset=distance, yoffset=0).perform()

def check_if_redirected(driver, initial_url, timeout, interval):
    init_time = 0
    while init_time < timeout:
        if driver.current_url != initial_url:
            write_to_cache("登录成功！正在跳转至学习网址...")
            return True

        time.sleep(interval)
        init_time += interval
    return False

def play_video(driver):
    # 旧思路: 根据Xpath找到元素并点击, 无法实现
    # 失败原因: 无法定位元素位置
    # # 找到并点击播放按钮
    # play_button = WebDriverWait(driver, 10).until(
    #    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]/div[2]")) # 播放按钮
    #    # EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[8]'))       # 播放页面
    # )
    #play_button.click()
    #driver.execute_script("arguments[0].scrollIntoView(true);", play_button)
    # script = '''
    # var event = new MouseEvent('mouseover', {
    # 'view': window,
    # 'bubbles': true,
    # 'cancelable': true
    # });
    # arguments[0].dispatchEvent(event);
    # '''
    # driver.execute_script(script, play_button)
    # #driver.execute_async_script(script)
    # ActionChains(driver).move_to_element(close_message_button).click().perform()

    # 新思路：直接hover到特定位置执行点击任务
    # 新思路2：先hover到父元素control_bar, 通过Xpath定位父元素, 通过css_selector从父元素定位子元素
    completely_close_task(driver)
    #time.sleep(10)
    time.sleep(3)
    actions = ActionChains(driver)
    actions.reset_actions()  # https://blog.csdn.net/weixin_45080737/article/details/134436893   move_by_offset()所执行的鼠标移动不是绝对坐标, 而是相对坐标
    actions.move_by_offset(430, 250).click().perform()  
    #actions.move_by_offset(215, 125).click().perform()  # 可以播放, 但是不知道位置点到哪里了
    console_log("点击播放按钮成功")

def check_task(driver):
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/span/div")
        return True
    except NoSuchElementException:
        return False

def complete_task(driver):
    # 先选一个选项A, 查看是否是正确答案
    # 不能用Xpath, 会找不到???

    # css元素新语法
    first_topic_item = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".topic-list .topic-item:first-child"))
    )
    # 点击第一个 topic-item
    #first_topic_item.click()   # 该方法不安全, 如果已经点击会报错
    actions = ActionChains(driver)
    actions.move_to_element(first_topic_item).click().perform()

def completely_close_task(driver):
    if(check_task(driver) == True):
        complete_task(driver)
        # 选择正确选项机制待完善
        close_task_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/span/div")
        close_task_button.click()
        time.sleep(1)
        play_video(driver)

def present_video_title(driver):
    return driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[1]/div[1]/span[2]").text

def get_video_node(title):
    temp = ""
    for i in range(len(title)):
        if title[i] == '.' or title[i].isdigit():
            temp += title[i]
        else:
            break
    return temp

def if_node_match(driver, cache_node):
    present_chapter = present_video_title(driver)
    present_node = get_video_node(present_chapter)
    if present_node == cache_node:
        return True
    else:
        return False

def select_new_video(driver):
    present_chapter = present_video_title(driver)
    present_node = get_video_node(present_chapter)
    console_log("当前学习章节: {}, 章节编号: {}, 正在跳转...".format(present_chapter, present_node))
    actions = ActionChains(driver)
    actions.reset_actions()
    actions.move_by_offset(457, 596).perform() 
    control_bar = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]")
    next = control_bar.find_element(By.CLASS_NAME, "nextButton")
    actions.move_to_element(next).click().perform()
    console_log("点击下一章节按钮成功")
    time.sleep(10)

# 注意：以下两个查看时间的指令一定要保证没有弹窗！(可忽略, 后面已经封装completely_close_task函数保证安全性)
def cur_time(driver):
    completely_close_task(driver)
    actions = ActionChains(driver)
    actions.reset_actions()
    actions.move_by_offset(457, 596).perform()
    #console_log("当前播放进度: {}".format())
    cur_time_info = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]/div[4]/span[1]"))
    )
    return cur_time_info.text
    #return n_play_time_div.find_element(By.CSS_SELECTOR, ".currentTime").text

def duration(driver):
    completely_close_task(driver)
    actions = ActionChains(driver)
    actions.reset_actions()
    actions.move_by_offset(457, 596).perform()
    video_duration_info = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]/div[4]/span[2]"))
    )

    return video_duration_info.text
    #return n_play_time_div.find_element(By.CSS_SELECTOR, ".duration").text

def time_cal(time1, time2):
    # 接受两个形如 "00:13:33"(hour:minute:second) 的时间字符串, 计算它们之间的差值, 并将结果转换为分钟数
    # 解析时间字符串
    def parse_time(time_str):
        hours, minutes, seconds = map(int, time_str.split(':'))
        total_minutes = hours * 60 + minutes + seconds / 60
        return total_minutes
    
    # 转换为分钟数
    minutes1 = parse_time(time1)
    minutes2 = parse_time(time2)
    
    # 计算差值
    diff_minutes = abs(minutes1 - minutes2)
    
    return diff_minutes


def check_if_over(driver, cur, dur):
    # 使用time库检测
    if time_cal(cur, dur) < 2 / 60:
        console_log("当前视频: {} 已经播放结束".format(present_video_title(driver)))
        return True
    else:
        return False

def check_if_bar_refreshed(driver):
    if duration(driver) is None or duration(driver) == "00:00:00":
        return False
    return True

def check_if_title_refreshed(driver, title_temp):
    if present_video_title(driver) == title_temp:
        return False
    return True

# def check_if_paused(last, cur):
#     if last != cur:
#         return False
#     else:
#         time.sleep(10)
#         cur = cur_time()
#         if last != cur:
#             return False
#         return True

def find_node(message):
    head = -1
    for i in range(len(message)):
        if message[i] == '_':
            head = i
        elif not (message[i].isdigit() or message[i] == '.') and head != -1:
            tail = i
            return message[head+1:tail]

def activate(config_dict):
    os.chdir(config_dict['install_path'])  # 一定加上这一句, 否则文件都存到系统默认用户目录了
    #os.chdir(r'D:\Project\Python_lib\WebTest')  # 一定加上这一句, 否则文件都存到系统默认用户目录了

    check_config(config_dict, config_dict['install_path'])
    cache = read_the_last_line_of_cache()
    cur_node = find_node(cache)
    write_to_cache("上次学习进度: {}".format(cur_node))
    pattern = "已经播放"    # 发生错误时返回的播放时间
    is_last_crash = cache.find(pattern)
    #print(str(datetime.now())[:10], cache[:10]) 
    if is_last_crash != -1 and str(datetime.now())[:10] == cache[:10]:
        last_crash_play_time = cache[is_last_crash+len(pattern):]
        last_crash_play_time = float(last_crash_play_time[:-2])
        write_to_cache("已读取到上次学习时间: {}分钟".format(last_crash_play_time))
    else:
        last_crash_play_time = 0
        write_to_cache("未读取到上次学习时间或上次学习时间在一天前")

    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--log-level=3")  # 设置日志级别，3 表示只显示严重错误
    #chrome_options.add_argument('--ignore-cache')   # 无视缓存
    #chrome_options.add_argument("--incognito") # 无痕模式

    # 启动浏览器实例
    driver_path = config_dict['driver_path']
    service = Service(executable_path=driver_path)  # 指定 chromedriver 的路径
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        console_log("没有正确安装chrome或者chromedriver, 错误信息如下:\n{}".format(e))
        console_log("正在尝试为您启动edge")
        driver = webdriver.Edge()

    
    # 登录智慧树官网
    login_treenity_url = config_dict['login_treenity_url']
    driver.get(login_treenity_url)
    try:
        login_wisdom_tree(driver, config_dict)
        # 将滑块验证图片下载到本地通过opencv进行缺口位置分析
        check_if_login = False
        login_attempt_left = 3      
        while(not check_if_login):
            save_image(driver)
            # 对比两张图片，计算滑动距离
            small_img_path = './image/slider_s.png'  # 滑块图（小图片）
            big_img_path = './image/slider_b.png'   # 背景图（大图片）
            distance = match(small_img_path, big_img_path)
            #distance = distance / 320 * 300 + 22 # 先根据图片尺寸进行处理，然后加上调整参数20
            distance = distance / 320 * 310 + 14# 先根据图片尺寸进行处理，然后加上调整参数20
            # 移动
            move(driver, distance)
            check_if_login = check_if_redirected(driver, login_treenity_url, 20, 1)
            login_attempt_left -= 1
            if login_attempt_left == 0:
                raise Exception("multiple login attempts timeout, please check your account name and password\n多次登录超时, 请检查账号或密码!")
        # 输出登录成功信息
    except Exception as e:
        write_to_cache("[Warning]: {}".format(e))

    webclass_url = config_dict['webclass_url']
    driver.get(webclass_url)
    try:
        # 找到关闭学习提示按钮
        # 无法直接用class或xpath定义，属于伪元素，参考https://blog.csdn.net/Z_shoushow/article/details/89499866
        # 复制父节点的selector路径
        close_message_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div > div:nth-child(6) > div.dialog-read > div.el-dialog__header > i"))
        )
        #ActionChains(driver).move_to_element(close_message_button).click().perform()
        try: 
            close_message_button.click()
        except Exception as e:
            write_to_cache("请先手动登录学习页面, 将最外层提示永久关闭!\n[Warning]{}".format(e))
        write_to_cache("关闭学习提示按钮成功")
        time.sleep(2)
        present_title_temp = present_video_title(driver)
        while(not if_node_match(driver, cur_node)):
            select_new_video(driver)
            present_title_temp = present_video_title(driver)
            #play_video()

        while(not check_if_bar_refreshed(driver)):
            time.sleep(1)

        present_title_temp = present_video_title(driver)
        write_to_cache("已成功跳转至昨日进度! 当前进度_{}".format(present_title_temp))
        #TotalTime = 0  # cannot handle multiple crashes
        TotalTime = last_crash_play_time
        #max_play_time = 25
        max_play_time = int(config_dict['max_play_time'])

        time.sleep(5)
        while(TotalTime <= max_play_time):
            # 对于网速不好的时候, 需要增加等待时间, 以免CurTimePoint读取到未初始化的进度条时间(00:00:00)
            while(not check_if_bar_refreshed(driver)):
                console_log("正在等待进度条加载...")
                time.sleep(1)
            # 在新视频播放开头初始化计时器
            CurTimePoint = cur_time(driver)
            LastTimePoint = CurTimePoint
            dur = duration(driver)
            play_video(driver)
            #print()
            #is_the_video_over = False 
            while(not check_if_over(driver, CurTimePoint, dur) and TotalTime <= max_play_time):
                #completely_close_task()
                LastTimePoint = CurTimePoint
                CurTimePoint = cur_time(driver)
                TotalTime += time_cal(LastTimePoint, CurTimePoint)
                console_log("已经播放{}分钟".format(TotalTime))
                time.sleep(10) # put into check_if_paused
                if LastTimePoint == CurTimePoint:
                    console_log("检测到视频已经暂停, 正在尝试继续播放")
                    #play_video()
                
            if(TotalTime >= max_play_time):
                break
            present_title_temp = present_video_title(driver)
            write_to_cache("正在跳转至下一视频, 当前进度_{}, 当前学习时间{}分钟".format(present_title_temp, TotalTime))
            select_new_video(driver)
            present_title_temp = present_video_title(driver)
        
        write_to_cache("今日规律学习目标完成! 当前进度_{}".format(present_title_temp))        
        #time.sleep(60*60)
    except Exception as e:
        write_to_cache("{}\n{}: 发生错误! 当前进度_{}, 已经播放{}分钟".format(e, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), present_title_temp, TotalTime))

    # 关闭浏览器实例
    driver.quit()


# ### class for user gui

def show_settings_popup(config_dict, sub_width = 600, sub_height = 300):
    '''
    create a subwindow for users to change user configuration

    :param: `config_dict`: a standard dictionary object containing the user config

        `subwidth`: the width of the subwindow

        `sub_height`: the height of the subwindow

    '''
    temp_dict = config_dict.copy()
    kx = main_width/sub_width
    ky = main_height/sub_height

    popup = tk.Toplevel(root)
    popup.title("设置")
    popup.geometry(f"{sub_width}x{sub_height}")  # 宽度x高度

    def make_setting_statement(node, text, default_message, entry_temp, adjust_coef = 2):
        # 创建一个标签
        label = tk.Label(popup, text=text)
        label.place(relx=0.01*kx, rely=0.03*ky*node*adjust_coef)

        # 创建一个输入框
        message = default_message
        entry = tk.Entry(popup, width=50)
        entry.place(relx=0.22*kx, rely=0.03*ky*node*adjust_coef)
        entry.insert(0, default_message)
        
        entry_temp.append(entry)
# config_dict = {'student_id': 'None', 'login_pwd': 'None', 'school_name': 'None', 'default_browser': 'Chrome',
#                    'driver_path':'D:/tools/ChromeDriver/chromedriver.exe', 'login_treenity_url': 'https://passport.zhihuishu.com/login#studentID',
#                    'webclass_url': 'https://studyvideoh5.zhihuishu.com/stuStudy?recruitAndCourseId=485f5d5c455f4859454a5859584d5c4258', 
#                    'max_play_time': '25', 'auto_play': 'False', 'install_path': 'C:/WebClassAutoLogin'}
    reference = ["学生学号", "登录密码", "学校名称", "浏览器名称", "浏览器驱动路径", "登录地址", "学习地址", "单日最大播放时间", "意外暂停自动播放"]
    key = list(temp_dict.keys())
    value = list(temp_dict.values())
    entry_temp = []
    for i in range(len(reference)):
        make_setting_statement(i, reference[i], value[i], entry_temp)

    def submit_settings():
        '''
        submit the settings changed by user, called when pressing the submit button
        '''
        for i in range(len(reference)):
            temp_dict[key[i]] = entry_temp[i].get()
        config_dict.update(temp_dict)
        new_install_root_path = config_dict['install_path']
        write_config_gui(config_dict, new_install_root_path)
    
    # 创建一个提交按钮
    submit_button = tk.Button(popup, text="确定", command=lambda: [submit_settings(), console_log("用户信息设置成功"), popup.destroy()])
    submit_button.place(relx=0.45*kx, rely=0.85)

    # 弹出窗口设置
    popup.transient(root)  # 使弹出窗口依赖于主窗口
    popup.grab_set()  # 使弹出窗口获得焦点，并阻止用户与主窗口交互
    #popup.focus_force()  # 强制弹出窗口获得焦点
    popup.wait_window()  # 等待弹出窗口关闭

def set_install_session(config_dict):
    '''
    set the install_path of the exe, shown in mainwindow and is never closed
    '''
    # 创建一个标签
    label = tk.Label(root, text="请选择安装路径:")
    label.place(relx=0.01, rely=0.03)

    # 创建一个输入框
    install_path = 'C:/WebClassAutoLogin'
    entry = tk.Entry(root, width=50)
    entry.place(relx=0.22, rely=0.035)
    entry.insert(0, install_path)

    # 创建一个选择目录按钮，并绑定处理函数
    choose_button = tk.Button(root, text="选择目录", command=lambda: choose_directory(entry))
    choose_button.place(relx=0.05, rely=0.1)

    # 创建一个提交按钮
    def update_install_path():
        config_dict['install_path'] = entry.get()
    submit_button = tk.Button(root, text="确定", command=lambda: [console_log("安装路径'{}'设置成功".format(entry.get())), update_install_path()])
    submit_button.place(relx=0.25, rely=0.1)
 

def console_log(text):
    '''
    append text to the textbox in the mainwindow
    '''
    textbox.config(state=tk.NORMAL)
    textbox.insert(tk.END, text + "\n")
    textbox.see(tk.END)
    textbox.config(state=tk.DISABLED)
    # message_queue.put(text)

# def check_queue():
#     while not message_queue.empty():
#         message = message_queue.get()
#         textbox.config(state=tk.NORMAL)
#         textbox.insert(tk.END, message + "\n")
#         textbox.see(tk.END)
#         textbox.config(state=tk.DISABLED)
#     root.after(100, check_queue)

# 定义一个函数来处理按钮点击事件
def choose_directory(entry, install_path='C:/WebClassAutoLogin'):
    '''
    handle the submit action of the install path selection
    '''
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    directory = tk.filedialog.askdirectory(initialdir=install_path)
    if directory:
        entry.delete(0, tk.END)  # 清空输入框
        entry.insert(0, directory)  # 插入选择的目录路径


config_dict = {'student_id': 'None', 'login_pwd': 'None', 'school_name': 'None', 'default_browser': 'Chrome',
                   'driver_path':'D:/tools/ChromeDriver/chromedriver.exe', 'login_treenity_url': 'https://passport.zhihuishu.com/login#studentID',
                   'webclass_url': 'https://studyvideoh5.zhihuishu.com/stuStudy?recruitAndCourseId=485f5d5c455f4859454a5859584d5c4258', 
                   'max_play_time': '25', 'auto_play': 'False', 'install_path': 'C:/WebClassAutoLogin'}
# 设置 DPI 意识
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# 创建主窗口
root = tk.Tk()
root.title("AutoLogin_release1.4.0")
# message_queue = queue.Queue()
# check_queue()

# 设置窗口大小
main_width = 600
main_height = 450
# sub_width = 600
# sub_height = 100
root.geometry(f"{main_width}x{main_height}")  # 宽度x高度

settings_button = tk.Button(root, text="其他设置", command=lambda: [check_config(config_dict, config_dict['install_path']), show_settings_popup(config_dict)])
settings_button.place(relx=0.4, rely=0.1)

#settings_button = tk.Button(root, text="关于", command=lambda: print(config_dict))
settings_button = tk.Button(root, text="关于", command=lambda: console_log("作者: AndyXie\ngithub项目地址: https://github.com/AndyXie0718/treenity_webclass_auto_complete\n2024/10/19"))
settings_button.place(relx=0.6, rely=0.1)

def start_activation():
    # 创建一个新的线程来运行 activate 函数
    activation_thread = threading.Thread(target=lambda: activate(config_dict))
    activation_thread.start()
#settings_button = tk.Button(root, text="启动", command=lambda: activate(config_dict))
settings_button = tk.Button(root, text="启动", command=lambda: start_activation())
settings_button.place(relx=0.8, rely=0.1)

# 创建一个文本框来显示安装信息，并设置 state 为 DISABLED
textbox = tk.Text(root, height=20, width=65, state=tk.DISABLED)
textbox.place(relx=0.01, rely=0.2)

# 显示弹出式窗口
set_install_session(config_dict)

# 进入消息循环
root.mainloop()
