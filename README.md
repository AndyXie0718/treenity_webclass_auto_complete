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
