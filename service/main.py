"""

Kivy/Android Background Service.

an OSC handler is regiserted which accepts 2 text fields. The text fields
are used to update the text in an Android Notification.

This also supports adding up to three buttons to the notification.
This feature is not yet fully working as the callback to handle the
button press is not working.

This code is largely based on these two examples:

https://github.com/kivy/plyer/tree/master/examples/notification
http://cheparev.com/kivy-recipe-service-customization/

"""


from kivy.lib import osc
from kivy.logger import Logger

from plyer import notification
from plyer.utils import platform
from plyer.compat import PY2

if platform == 'android':
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.broadcast import BroadcastReceiver
import time

# Todo pull these alues from a file common to main application and service
hostname = '127.0.0.1'
serviceport = 15123
activityport = 15124

def update_notification(message, *args):
    '''callback handler from osc update event
    this function is called whenever the user presses the update button
    in the main app,
    '''
    Logger.info("service: recieved request: %s",message)

    if platform == "android":
        update_service(*message[2:])

def update_service(ptext, pmessage):
    """
    http://cheparev.com/kivy-recipe-service-customization/

    this post demonstrates how it could be possible to update the
    default android foreground service notification.
    """

    # create wrapper objects for Java Classes
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    AndroidString = autoclass('java.lang.String')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    #registerReceiver = autoclass('android.content.registerReceiver')
    # Action is added in api 19. Action.Builder is added in 20
    # the current api used below was deprectated in 23.
    Action = autoclass('android.app.Notification$Action')
    PythonActivity = autoclass('org.renpy.android.PythonActivity')
    PythonService = autoclass('org.renpy.android.PythonService')

    service = PythonService.mService
    Drawable = autoclass("{}.R$drawable".format(service.getPackageName()))

    # convert input text into a java string
    text = AndroidString(ptext.encode('utf-8'))
    message = AndroidString(pmessage.encode('utf-8'))

    # kivy doesnt have a tray icon by default
    #small_icon = getattr(Drawable, 'tray_small')
    # kivy creates this icon by default
    large_icon_bitmap = get_scaled_icon('icon')

    intent = Intent(service, service.getClass())
    contentIntent = PendingIntent.getActivity(service, 0, intent, 0)
    notification_builder = NotificationBuilder(service)
    notification_builder.setContentTitle(text)
    notification_builder.setContentText(message)
    Logger.info("service: set small icon")
    notification_builder.setSmallIcon(Drawable.icon)
    Logger.info("service: set large icon")
    notification_builder.setLargeIcon(large_icon_bitmap)
    Logger.info("service: set intent")
    notification_builder.setContentIntent(contentIntent)

    # Intent Action, as Java String
    # (this is probably no the correct action to use)
    actiontext = AndroidString("ACTION_GET_CONTENT".encode('utf-8'))

    # ########################################################################
    # update the first button

    # text to display on buttons (doesnt work, because icon is too big)
    act1msg = AndroidString("Act1".encode('utf-8'))
    intentAct1 = Intent(service, service.getClass())
    intentAct1.setAction(actiontext)
    # must use intentAct1.setClass()  ???
    # what are the correct arguments/ttypes for setClass?
    # 12345 is an arbitrary number (unclear what the field is for)
    contentIntent = PendingIntent.getBroadcast(service, 12345, intentAct1, PendingIntent.FLAG_UPDATE_CURRENT )
    notification_builder.addAction(Drawable.icon,act1msg,contentIntent)

    # ########################################################################
    # update the second button
    act2msg = AndroidString("Act2".encode('utf-8'))
    intentAct2 = Intent(service, service.getClass())
    intentAct2.setAction(actiontext)
    contentIntent = PendingIntent.getBroadcast(service, 12345, intentAct2, PendingIntent.FLAG_UPDATE_CURRENT )
    notification_builder.addAction(Drawable.icon,act2msg,contentIntent)

    # ########################################################################
    # update the third button
    act3msg = AndroidString("Act3".encode('utf-8'))
    intentAct3 = Intent(service, service.getClass())
    intentAct3.setAction(actiontext)
    contentIntent = PendingIntent.getBroadcast(service, 12345, intentAct3, PendingIntent.FLAG_UPDATE_CURRENT )
    notification_builder.addAction(Drawable.icon,act3msg,contentIntent)


    # ########################################################################
    # build and update notification

    notification = notification_builder.getNotification()
    notification_service = service.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_service.notify(1, notification)

def get_scaled_icon(icon):
    """
    icon : name of icon file (png) without extension

    this function assumes that a 'Drawable' was regiseted, (see original post)
    it should be possible to create a bitmap dynamically, using a bitmap
    factory.

    Bitmap bm = BitmapFactory.decodeResource(getResources(), R.drawable.image);
    """
    Dimen = autoclass("android.R$dimen")
    Bitmap = autoclass("android.graphics.Bitmap")
    PythonService = autoclass('org.renpy.android.PythonService')
    service = PythonService.mService
    Drawable = autoclass("{}.R$drawable".format(service.getPackageName()))

    scaled_icon = getattr(Drawable, icon)
    scaled_icon = cast("android.graphics.drawable.BitmapDrawable",
                       service.getResources().getDrawable(scaled_icon))
    scaled_icon = scaled_icon.getBitmap()

    res = service.getResources()
    height = res.getDimension(Dimen.notification_large_icon_height)
    width = res.getDimension(Dimen.notification_large_icon_width)
    return Bitmap.createScaledBitmap(scaled_icon, width, height, False)

def intent_callback(context, intent, *args):
    ''' Notification Button Callback
    If everything was working correctly, this function would be called
    when the user press a notification button.
    '''
    # context, intent
    Logger.warning("captured intent")
    Logger.warning("%s"%context)
    Logger.warning("%s"%intent)
    Logger.warning("%s"%args)

def main():

    oscid = osc.listen(ipAddr=hostname, port=serviceport)
    osc.init()

    osc.bind(oscid, update_notification, '/update')

    br = BroadcastReceiver(intent_callback,["GET_CONTENT",]) # no prefix ACTION_ required
    br.start()

    while True:
        osc.readQueue(oscid)
        time.sleep( .1 )

if __name__ == '__main__':
    main()