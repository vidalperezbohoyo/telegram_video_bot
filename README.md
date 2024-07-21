# telegram_video_bot
Simple telegram bot example that uses [telegram-python-api](https://docs.python-telegram-bot.org/en/v21.4/) to send videos over telegram.  
Uses a USB Camera as video input.

## Commands
- **/photo:** sends a photo
- **/video:** sends X seconds of video

# Capabilities
- Access control to multiple users (via telegram user id)
- Logger to see what happened in the bot
- Images / videos with timestamp
- Nothing more, its so simple!

## Install dependencies
```
sudo apt update
sudo apt install pip
pip install python-telegram-bot
```  

Usage:  
```python3 bot.py```

<img src="https://github.com/user-attachments/assets/deb778ba-b4c8-43f3-8d2f-58982ca35811" width="25%">
<img src="https://github.com/user-attachments/assets/ed56420d-66e4-4559-9bdf-f229a8cef153" width="50%">


(Yes..., my ubuntu time is not configured)

## (Advanced) If you want to use telegram bot in Read-Only file systems
(asuming you are in read-only mode and DNS is not working)  
Do:
```
sudo mount -o remount,rw /
```
In ```/etc/resolv.conf``` (with sudo nano or sudo vim) add:  
```
nameserver 8.8.8.8  
nameserver 8.8.4.4
```
Change to ro to store changes and reboot...
```
sudo mount -o remount,ro /
```

Also change VIDEO_PATH and IMAGE_PATH to a path in ```/tmp``` directory, like ```/tmp/output.mp4```