from selenium import webdriver
 
# 初始化 WebDriver 并打开一个谷歌浏览器窗口
driver = webdriver.Chrome()
 
# 打开一个网页
driver.get('https://www.baidu.com')
 
# 打印页面标题
print(driver.title)
 
# 关闭浏览器
driver.quit()