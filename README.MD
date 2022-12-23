# Make a headless window out of every window! Perfect for undetected chromedriver (Selenium) to pass bot detection in headless mode.

**_From https://github.com/ultrafunkamsterdam/undetected-chromedriver_**
"just to mention it another time, since some people have hard time reading: headless is still WIP. Raising issues is needless_"

It is of course not the same as Chromes built-in headless mode [that's why I called it PoorMansHeadless :)]
but it allows you to run several automation processes on your pc without getting disturbed all the time.

```python
pip install PoorMansHeadless
```

```python
# A simple way to get the hwnd for your window:
from PoorMansHeadless import FakeHeadless
hand = FakeHeadless.get_all_windows_with_handle()
hwnd = 2231030
self = FakeHeadless(hwnd)
```

```python
# The window will be hidden almost completely (99,99999%) . Because of the 0.00001, 
# its execution is still a priority for the operating system. 
# This little part is a one-pixel-line above the Windows taskbar.
# Too small to see/interact/interfere, but big enough
# to avoid standby mode/rescource saving. 
```

```python
# if you pass None as width and height, the window won't be resized, just moved. 
# The upper part will be placed one pixel above the taskbar (distance_from_taskbar)
self.start_headless_mode(width=None, height=None, distance_from_taskbar=1) 
```

```python
# To check if everything is going well in your headless window you can either start a video stream:
self.start_video_stream()

# or save screenshots to the HDD:
self.start_saving_screenshots(
    folder="c:\\pictest4", frequency=1
)  # if the folder doesn't exist, it will be created. Frequency=1 means one screenshot every second
```

```python
# if you have seen enough, you can stop the video/screenshot stream by calling:
self.disable_save_screenshots()
self.disable_video_stream()

# if you want to quit the headless mode, use:
self.quit_headless_mode()
```

```python
# By the way, if you are stuck in topmost mode (window on top of everything) after quitting the headless mode, use 
self.activate() 
# to set the hierachy back to normal. It happens sometimes when you use your mouse or keyboard, 
# while quitting the headless mode. 
```

```python
# The module contains some additional methods (resizing, invisibility, color substitution ... )
# Most of them are used as "helper methods" for the principal
# purpose of this package. But they also can be used on their own.
```
