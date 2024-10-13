# 说明：依赖库selenium, opencv, requests
# 安装指令: 
# pip install selenium -i https://mirrors.aliyun.com/pypi/simple/
# pip install opencv-python -i https://mirrors.aliyun.com/pypi/simple/
# pip install requests -i https://mirrors.aliyun.com/pypi/simple/
import time
import os
import requests
import cv2
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置 Chrome 选项
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
#chrome_options.add_argument('--ignore-cache')   # 无视缓存
#chrome_options.add_argument("--incognito") # 无痕模式

# 启动浏览器实例
service = Service(executable_path=r"D:\tools\ChromeDriver\chromedriver.exe")  # 指定 chromedriver 的路径
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    print("没有正确安装chrome或者chromedriver, 错误信息如下:\n{}".format(e))
    print("正在尝试为您启动edge")
    driver = webdriver.Edge()

def login_wisdom_tree():
    # # 切换到以“学校+学号”登录的方式(可直接访问https://passport.zhihuishu.com/login#studentID)
    # change_login_method_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/div[2]/div[1]/a[2]"))
    # )
    # change_login_method_button.click()

    # 依次填写学校、学号、密码
    school_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[1]/div/input[2]"))
    )
    school_name_input.send_keys("湖南大学")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[1]/div/div/div/div[1]/ul/li[2]"))
    )
    login_button.click()

    student_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[2]/input"))
    )
    student_name_input.send_keys("")    # 在这里输入学号

    pwd_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/ul[2]/li[3]/input"))
    )
    pwd_input.send_keys("")             # 在这里输入密码

    # 找到登录按钮
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/form/div[1]/span"))
    )
    login_button.click()

def save_image():
    url_s = None
    url_b = None
    while(url_s is None or url_b is None):
        print(url_s, url_b)
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
def move(distance):
    # 获取滑块元素
    #loc = 'div[class="yidun_slider  yidun_slider--hover "]'
    #ele = driver.find_element('css selector', loc)
    ele = driver.find_element(By.XPATH, "/html/body/div[33]/div[2]/div/div/div[2]/div/div[2]/div[2]")
    # 实例化对象
    action = ActionChains(driver)
    # 拖动滑块

    action.drag_and_drop_by_offset(ele, xoffset=distance, yoffset=0).perform()

    # # 定位到验证成功
    # #这里 如果写time.sleep(2)会匹配失败，具体原因不知道
    # time.sleep(1)
    # loc = '.yidun_tips__text.yidun-fallback__tip'
    # text = driver.find_element('css selector',loc).text

    # if text == "验证成功":
    #     print("验证成功")
    # else:
    #     print("验证失败")

def play_video():
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
    time.sleep(10)
    actions = ActionChains(driver)
    ActionChains(driver).reset_actions()  # https://blog.csdn.net/weixin_45080737/article/details/134436893   move_by_offset()所执行的鼠标移动不是绝对坐标, 而是相对坐标
    actions.move_by_offset(430, 250).click().perform()  
    #actions.move_by_offset(215, 125).click().perform()  # 可以播放, 但是不知道位置点到哪里了
    print("点击播放按钮成功")

# def check_task():
#     close_button = WebDriverWait(driver, 15*60).until(
#        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/span/div"))
#     )
#     return close_button
def check_task():
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/span/div")
        return True
    except NoSuchElementException:
        return False

def complete_task():
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

def completely_close_task():
    if(check_task() == True):
        complete_task()
        # 选择正确选项机制待完善
        close_task_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/span/div")
        close_task_button.click()
        time.sleep(1)
        play_video()

def present_video_title():
    return driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[1]/div[1]/span[2]").text

def if_node_match(cache_node):
    present_chapter = present_video_title()
    present_node = present_chapter[:3]
    if present_node == cache_node:
        return True
    else:
        return False

def select_new_video():
    present_chapter = present_video_title()
    present_node = present_chapter[:3]
    print("当前学习章节: {}, 章节编号: {}, 正在跳转...".format(present_chapter, present_node))
    actions = ActionChains(driver)
    ActionChains(driver).reset_actions()
    actions.move_by_offset(457, 596).perform() 
    control_bar = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]")
    next = control_bar.find_element(By.CLASS_NAME, "nextButton")
    actions.move_to_element(next).click().perform()  
    print("点击下一章节按钮成功")
    time.sleep(10)

# 注意：以下两个查看时间的指令一定要保证没有弹窗！(可忽略, 后面已经封装completely_close_task函数保证安全性)
def cur_time():
    completely_close_task()
    actions = ActionChains(driver)
    ActionChains(driver).reset_actions()
    actions.move_by_offset(457, 596).perform()
    #print("当前播放进度: {}".format())
    return driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]/div[4]/span[1]").text
    #return n_play_time_div.find_element(By.CSS_SELECTOR, ".currentTime").text

def duration():
    completely_close_task()
    actions = ActionChains(driver)
    ActionChains(driver).reset_actions()
    actions.move_by_offset(457, 596).perform()
    return driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]/div[4]/span[2]").text
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

def check_if_over():
    cur = cur_time()
    dur = duration()
    #print("当前播放进度: {}/{}".format(cur, dur))
    if cur == dur:
        print("当前视频: {} 已经播放结束".format(present_video_title()))
        return True
    else:
        return False

def read_the_last_line_of_cache():
    """
    检查是否存在 ./WebClassLoginCache/cache.txt 文件，并读取最后一行内容。
    如果文件不存在，则创建文件并返回空字符串。
    
    :return: 文件的最后一行内容（如果存在），否则返回空字符串
    """
    cache_path = './WebClassLoginCache/cache.txt'
    
    if not os.path.exists('./WebClassLoginCache'):
        os.makedirs('./WebClassLoginCache')
    
    if not os.path.exists(cache_path):
        with open(cache_path, 'w', encoding='utf-8') as file:
            file.write("")  # 创建空文件
    
    with open(cache_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    for line in reversed(lines):
        if line.find("今日规律学习目标完成!") != -1 or line.find("发生错误") != -1 or line.find("sudo"):
            return line.strip()  # 返回最后一行内容并去除换行符
    print("Cache Not Found, Start From DeFault _1.1")
    return "[Warning] Cache Not Found, Start From DeFault _1.1"


def write_to_cache(message):
    """
    在 cache.txt 文件中追加当前时间和给定的消息，并在每条消息前换行。
    
    :param message: 要追加的消息字符串
    """
    cache_path = './WebClassLoginCache/cache.txt'
    
    if not os.path.exists('./WebClassLoginCache'):
        os.makedirs('./WebClassLoginCache')
    
    if not os.path.exists(cache_path):
        with open(cache_path, 'w', encoding='utf-8') as file:
            file.write("")  # 创建空文件
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{current_time}: {message}\n"
    
    print(log_message)
    with open(cache_path, 'a', encoding='utf-8') as file:
        file.write(log_message)

def find_node(message):
    for i in range(len(message)):
        if message[i] == '_':
            return message[i+1:i+4]

#def timer():

# 登录联通校园网

# driver.get("http://58.20.19.47/0.htm")
# try:
#     # 找到登录按钮
#     login_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[2]/form[1]/div[2]/input[1]"))
#     )

#     # 点击登录按钮
#     login_button.click()

#     # 输出登录成功信息
#     print(f"登录成功")
# except Exception as e:
#     print(f"自动登录联通校园网时发生错误: {e}")

# 这里输入文件目录
os.chdir(r'')  # 一定加上这一句, 否则文件都存到系统默认用户目录了
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

# 登录智慧树官网
driver.get("https://passport.zhihuishu.com/login#studentID")
try:
    login_wisdom_tree()

    # 将滑块验证图片下载到本地通过opencv进行缺口位置分析
    save_image()
    # 对比两张图片，计算滑动距离
    small_img_path = './image/slider_s.png'  # 滑块图（小图片）
    big_img_path = './image/slider_b.png'   # 背景图（大图片）
    distance = match(small_img_path, big_img_path)
    #distance = distance / 320 * 300 + 22 # 先根据图片尺寸进行处理，然后加上调整参数20
    distance = distance / 320 * 310 + 14# 先根据图片尺寸进行处理，然后加上调整参数20
    # 移动
    move(distance)
    
    # 输出登录成功信息
except Exception as e:
    print(f"自动登录智慧树时发生错误: {e}")

# 等待页面跳转并进入学习界面
print("正在跳转至学习界面")
time.sleep(10)
driver.get("https://studyvideoh5.zhihuishu.com/stuStudy?recruitAndCourseId=485f5d5c455f4859454a5859584d5c4258")
try:
    # 找到关闭学习提示按钮
    # 无法直接用class或xpath定义，属于伪元素，参考https://blog.csdn.net/Z_shoushow/article/details/89499866
    # 复制父节点的selector路径
    close_message_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div > div:nth-child(6) > div.dialog-read > div.el-dialog__header > i"))
    )
    #ActionChains(driver).move_to_element(close_message_button).click().perform()
    close_message_button.click()
    #driver.execute_script("")
    write_to_cache("关闭学习提示按钮成功")

    time.sleep(2)
    while(not if_node_match(cur_node)):
        select_new_video()
        #play_video()

    present_title_temp = present_video_title()
    write_to_cache("已成功跳转至昨日进度! 当前进度_{}".format(present_title_temp))
    TotalTime = 0
    # 对于网速不好的时候, 需要增加等待时间, 以免CurTimePoint读取到未初始化的进度条时间(00:00:00)
    print("正在等待进度条加载...")
    time.sleep(5)
    while(TotalTime <= 28-last_crash_play_time):
        # 在新视频播放开头初始化计时器
        CurTimePoint = cur_time()
        play_video()
        print() 
        while(not check_if_over() and TotalTime <= 28-last_crash_play_time):
            #completely_close_task()
            LastTimePoint = CurTimePoint
            CurTimePoint = cur_time()
            TotalTime += time_cal(LastTimePoint, CurTimePoint)
            print("已经播放{}分钟".format(TotalTime))
            time.sleep(10)
        if(TotalTime >= 28-last_crash_play_time):
            break
        present_title_temp = present_video_title
        write_to_cache("正在跳转至下一视频, 当前进度_{}, 当前学习时间{}分钟".format(present_title_temp, TotalTime))
        select_new_video()
    
    write_to_cache("今日规律学习目标完成! 当前进度_{}".format(present_video_title()))        
    #time.sleep(60*60)
except Exception as e:
    #print(f"发生错误: {e}")
    write_to_cache("{}\n发生错误! 当前进度_{}, 已经播放{}分钟".format(e, present_title_temp, TotalTime))

# 关闭浏览器实例
driver.quit()