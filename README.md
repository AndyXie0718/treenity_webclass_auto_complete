# treenity_webclass_auto_complete
# develop 1.2.1
fixed few bugs when facing exceptions

# develop 1.2.2
fixed bugs when reading cache

# develop 1.2.3
fixed fatal bugs while reading last crash message and getting the playtime from it

bugs unfixed: 
- unexpected bug:
```
2024-10-14 13:01:34: Message: no such element: Unable to locate element: {"method":"xpath","selector":"/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[10]/div[4]/span[1]"}
```
- can't auto detect whether the video is playing or not, which print the same time-progress message at the console while the video is accidentally paused

- if the control bar was dragged, cannot auto detect the present_time

- the total length of the video can have errors, but only in about 1s, so we can jump to next video in advance

# develop 1.2.4
fixed few bugs

# log_241015
待新增新函数crash_report_export,用于导出crash数据,
def crash_report_add(message):
	with open ...
		file.write(message\n)

def crash_report_export(crash_report_path = ...):
	with open ...(加上日期)
		file.copy()

播放中出现的问题：
已经播放2.333333333333334分钟
检测到视频已经暂停, 正在尝试继续播放
已经播放2.5000000000000004分钟
已经播放2.8333333333333335分钟
点击播放按钮成功
已经播放2.9333333333333336分钟
已经播放3.1000000000000005分钟
已经播放3.266666666666667分钟
2024-10-15 13:25:24: invalid literal for int() with base 10: ''

初步猜测：获取播放进度字符串时刚好打断了正常获取进度的流程，导致获取到空字符串

解决方案：提高cur_time()调用的健壮性，使他能够返回一个正确格式的字符串(设置最大尝试次数，超出就继续抛出空字符串)

# release 1.3.02
fixed crash error when facing a newly popped out window after the course ends
the function wasn't tested, be aware and revert if necessary

## 环境配置(requirements)
```bash
python 3 # 可以是运行在anaconda环境里也可以是python原生环境, 不要windows版
nuitka, numpy, opencv-python, selenium, requests
```

## 编译指南
首先需要安装指定的C++编译器(在C++上还挺好用的, 是gcc13.2+llvm): [链接](https://github.com/brechtsanders/winlibs_mingw/releases/download/13.2.0-16.0.6-11.0.1-msvcrt-r1/winlibs-x86_64-posix-seh-gcc-13.2.0-llvm-16.0.6-mingw-w64msvcrt-11.0.1-r1.zip)
**- IDM 下载-选项-连接-最大连接个数从默认8改为4: 跳过github多线程检查**
下载完之后必须安装到指定目录(Nuitka安装路径的子目录)：(C:\Users\19528\AppData\Local\Nuitka\Nuitka\Cache\DOWNLO~1\gcc\x86_64\13.2.0-16.0.6-11.0.1-msvcrt-r1)
顺便**加到系统的环境变量目录**

```bash
# 提示: 先通过anaconda_prompt 进入py3.7虚拟环境
conda activate SmartCar_3_7
cd D:\Project\Python_lib\WebTest
(SmartCar_3_7) PS D:\Project\Python_lib\WebTest> python -m nuitka --onefile --windows-console-mode=disable --mingw64 --enable-plugin=tk-inter "AutoLogin(webclass and internet)_release_gui.py"
...
Nuitka will make use of Dependency Walker (https://dependencywalker.com) tool
to analyze the dependencies of Python extension modules.

Is it OK to download and put it in 'C:\Users\19528\AppData\Local\Nuitka\Nuitka\Cache\DOWNLO~1\depends\x86_64'.

Fully automatic, cached. Proceed and download? [Yes]/No : yes
Nuitka: Downloading 'https://dependencywalker.com/depends22_x64.zip'.
Nuitka: Extracting to 'C:\Users\19528\AppData\Local\Nuitka\Nuitka\Cache\DOWNLO~1\depends\x86_64\depends.exe'
...
Nuitka-Onefile: Keeping onefile build directory 'AutoLoginwebclass and internet_release_gui.onefile-build'.
Nuitka: Keeping dist folder 'AutoLoginwebclass and internet_release_gui.dist' for inspection, no need to use it.
Nuitka: Keeping build directory 'AutoLoginwebclass and internet_release_gui.build'.
Nuitka: Successfully created 'AutoLoginwebclass and internet_release_gui.exe'.
```
最终编译出的文件：
```bash
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        2024/10/21      0:23                AutoLoginwebclass and internet_release_gui.build
d-----        2024/10/21      0:23                AutoLoginwebclass and internet_release_gui.dist
d-----        2024/10/21      0:23                AutoLoginwebclass and internet_release_gui.onefile-build
-a----        2024/10/20      1:50          30200 AutoLogin(webclass and internet)_release_gui.py
-a----        2024/10/21      0:25       36881920 AutoLoginwebclass and internet_release_gui.exe
```
可见大小缩小为`36mb`, 差强人意

