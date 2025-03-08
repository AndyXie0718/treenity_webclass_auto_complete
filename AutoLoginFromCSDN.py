import selenium
from selenium import webdriver as web
import pandas as pd

chromedriver = r"D:\tools\ChromeDriver\chromedriver.exe" # 这个位置是你自己的下载放置的chromedriver.exe的路径
options = web.ChromeOptions()
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# 创建浏览器
driver = web.Chrome(chromedriver, chrome_options=options)
# 设置窗口大小
driver.set_window_size(1920, 1080)

username = 'xxxxxx'
password = 'xxxxxx'
url = 'xxxxxx'

driver.get(url)
try:
    driver.find_element_by_id("toLogOut")
    print("开始连接学校网络……")
except selenium.common.exceptions.NoSuchElementException:
    # 下面的id信息可以在源码中找到，账户、密码
    username_input = driver.find_element_by_id("username")
    password_input = driver.find_element_by_id("pwd")
    ## 这个地方，有些学校可能不一样，有的就是loginLink，需要仔细查看
    login_button = driver.find_element_by_id("loginLink_div")   
    ## 选择网络服务选项
    select_service = driver.find_element_by_id("selectDisname")
    #  _service_0：校园外网服务(out-campus NET)
    #  _service_1：校园内网服务(in-campus NET)
    #  _service_2：中国移动(CMCC NET)
    services = driver.find_element_by_id("_service_0")
    print("网页加载完毕")
	# 
    username_input.send_keys(username)
    # 密码输入框需单击激活后才可输入↓，id名称上述方法同理
    driver.find_element_by_id("pwd_tip").click()
    # 传入相关参数，密码、账户、
    password_input.send_keys(password)
    select_service.click()
    services.click()
    login_button.click()
    print("连接成功")
    # driver.close()
else:
    f = input("已登录，要退出吗？(Y/N)\n")
    if f.lower() == "y":
        driver.find_element_by_id("toLogOut").click()
        driver.find_element_by_id("sure").click()
        print("已退出登录")
        # driver.close()
    else:
        print("程序结束")
        # driver.close()
