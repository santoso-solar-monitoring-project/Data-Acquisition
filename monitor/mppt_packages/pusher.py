import pusher
import time, random

pusher_client = pusher.Pusher(app_id=u'651114', key=u'9dfb7224d7fd60cc9c5f', secret=u'958b9a4ad341c43ade27', cluster=u'us2')

def push_data(data):
    for datum in data:
        print("Pushing %f %f" % (datum.voltage, datum.current))
    response = pusher_client.trigger_batch([
                                            {u'channel': u'ch0', u'name': u'eventName', u'data' : {u'voltage': data[0].voltage, u'current': data[0].current}},
                                            {u'channel': u'ch1', u'name': u'eventName', u'data' : {u'voltage': data[1].voltage, u'current': data[1].current}},
                                            {u'channel': u'ch2', u'name': u'eventName', u'data' : {u'voltage': data[2].voltage, u'current': data[2].current}}
                                            ])
    if not response: #Response will be an empty dictionary if it succeeds
        return True
    else:
        return False
