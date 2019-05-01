import pusher

pusher_client = pusher.Pusher(app_id=u'773740', key=u'2f5b9c6ca3ae47929ed1', secret=u'10d53ef80206b52ca5b8', cluster=u'us2')

def push_data(data):
    #for datum in data:
    #    print("Pushing %f %f" % (datum.voltage, datum.current))
    response = pusher_client.trigger_batch([
                                            {u'channel': u'ch0', u'name': u'new-data', u'data' : {u'payload': [[data[0].time, data[0].voltage]]}}, #MPPT voltage
                                            {u'channel': u'ch1', u'name': u'new-data', u'data' : {u'payload': [[data[0].time, data[0].current]]}}, #MPPT current
                                            {u'channel': u'ch2', u'name': u'new-data', u'data' : {u'payload': [[data[1].time, data[1].voltage]]}}, #Single load voltage
                                            {u'channel': u'ch3', u'name': u'new-data', u'data' : {u'payload': [[data[1].time, data[1].current]]}}, #Single load current
					                        {u'channel': u'ch4', u'name': u'new-data', u'data' : {u'payload': [[data[2].time, data[2].voltage]]}}  #Open circuit voltage
                                            ])
    if not response: #Response will be an empty dictionary if it succeeds
        return True
    else:
        return False
