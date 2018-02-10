
import time

def millis():
    return int(1000 * time.time())

class Progress:
    def __init__(me, threshold):
        me.value = None
        me.timestamp = 0
        me.changed = False
        me.threshold = threshold

    def update(me, v):
        now = millis()
        if v != me.value:
            me.changed = True
            me.value = v
        if me.changed and now - me.timestamp > me.threshold:
            print(str(me.value))
            me.changed = False
            me.timestamp = now
