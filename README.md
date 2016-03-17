# python-android-notify
update android service notification from python using plyer/jnius

### Build & Run
use buildozer from the project root to build and run:
```
 buildozer android debug deploy run logcat
```

### About

This is an example android application using Python kivy/plyer/pyjnius. A background service is created, which creates a permanent Notification. Two text boxes allow for modifying the display text of the notification. This notification can have up to three buttons. The code demonstrates how to update the notification text and react to a button press.

### Current Problems:

1. Callback for reacting to a notification button press is not correctly implemented. The logs show the follow message. In service/main.py, the Intent is not being registered correctly, and there is no receiver registered to receive the event.

  ```
  03-17 09:29:07.612  5703  5703 D StatusBar: Clicked on button 0 for 0|org.test.notiexample|1|null|10101
  ```
2. Display Icon in notification button. It is unclear what the dimensions of the icon should be.
