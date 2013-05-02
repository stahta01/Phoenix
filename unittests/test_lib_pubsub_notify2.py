"""

:copyright: Copyright 2006-2009 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.


"""

import imp_unittest, unittest

import wtc



#---------------------------------------------------------------------------


class lib_pubsub_Notify2(wtc.PubsubTestCase):    
        
    def test0_NotificationTopics(self):
        topicMgr = self.pub.getDefaultTopicMgr()
        from wx.lib.pubsub.utils.notification import useNotifyByPubsubMessage

        assert not topicMgr.getTopic('pubsub', okIfNone=True)
        useNotifyByPubsubMessage()
        assert topicMgr.getTopic('pubsub')
        
        assert topicMgr.getTopic('pubsub').hasSubtopic()
    
        pubsubTopicNames = [obj.getName() for obj in topicMgr.getTopic('pubsub').getSubtopics()]
        self.assertEqual(
            set( pubsubTopicNames ),
            set(['pubsub.sendMessage', 'pubsub.deadListener',
                 'pubsub.subscribe',   'pubsub.unsubscribe',
                 'pubsub.newTopic',    'pubsub.delTopic'])
            )
        
        
    def test1_SubscribeNotify(self):
        class MyListener:
            countSub = 0
            countUnsub = 0
            def listenerSub(self, msgTopic=self.pub.AUTO_TOPIC, listener=None,
                            topic=None, newSub=None):
                self.assertEqual(msgTopic.getName(), 'pubsub.subscribe' )
                assert topic.getName() in ('pubsub.unsubscribe', 'testSubscribeNotify')
                if newSub:
                    self.countSub += 1
            def listenerUnsub(self, msgTopic=self.pub.AUTO_TOPIC, topic=None,
                              listener=None, listenerRaw=None):
                assert topic.getName() in ('testSubscribeNotify', 'pubsub.subscribe' )
                self.assertEqual(msgTopic.getName(), 'pubsub.unsubscribe' )
                if listener is not None:
                    self.countUnsub += 1
            def listenerTest(self):
                raise NotImplementedError # should never get here
    
        self.pub.setNotificationFlags(subscribe=True, unsubscribe=True)
        self.pub.getOrCreateTopic('testSubscribeNotify')
        tmp = MyListener()
        tmp.assertEqual = self.assertEqual
    
        self.pub.subscribe(tmp.listenerSub, 'pubsub.subscribe')
        self.assertEqual(tmp.countSub, 0)   # don't notify of self subscription
        self.assertEqual(tmp.countUnsub, 0)
        sl, ok = self.pub.subscribe(tmp.listenerUnsub, 'pubsub.unsubscribe')
        assert ok
        self.assertEqual(tmp.countSub, 1)
        self.assertEqual(tmp.countUnsub, 0)
    
        self.pub.subscribe(tmp.listenerTest, 'testSubscribeNotify')
        self.assertEqual(tmp.countUnsub, 0)
        self.pub.unsubscribe(tmp.listenerTest, 'testSubscribeNotify')
        self.assertEqual(tmp.countUnsub, 1)
    
        self.pub.unsubscribe(tmp.listenerSub,   'pubsub.subscribe')
        self.assertEqual(tmp.countSub, 2)
        self.assertEqual(tmp.countUnsub, 2)
        self.pub.unsubscribe(tmp.listenerUnsub, 'pubsub.unsubscribe')
        self.assertEqual(tmp.countSub, 2)
        self.assertEqual(tmp.countUnsub, 2) # don't notify of self unsubscription
    
    
    def test2_SendNotify(self):
        # trap the pubsub.sendMessage topic:
        class SendHandler:
            def __init__(self):
                self.pre = self.post = 0
            def __call__(self, topic=None, stage=None, listener=None,
                         msgTopic=self.pub.AUTO_TOPIC):
                if stage == 'pre':
                    self.pre += 1
                else:
                    self.post += 1
                self.assertEqual(msgTopic.getName(), 'pubsub.sendMessage')
                self.assertEqual(topic.getName(), 'testSendNotify')
        sh = SendHandler()
        sh.assertEqual = self.assertEqual
        
        self.pub.subscribe(sh, 'pubsub.sendMessage')
        self.pub.setNotificationFlags(sendMessage=True)
    
        # generate a message that will cause pubsub.sendMessage to be generated too
        assert sh.pre == 0
        assert sh.post == 0
        self.pub.getOrCreateTopic('testSendNotify')
        self.pub.sendMessage('testSendNotify')
        assert sh.pre == 1
        assert sh.post == 1
    


#---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
