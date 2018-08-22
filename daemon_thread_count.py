import threading
import time


class MyThread(threading.Thread):
    def run(self):
        print("{} started! This thread only lasts 3 seconds".format(self.getName()))              # "Thread-x started!"
        time.sleep(3)                                      # Pretend to work for a second
        print("{} finished after 3 seconds!".format(self.getName()))             # "Thread-x finished!"

if __name__ == '__main__':
    thread_list = []
    for x in range(4):                                     # Four times...
        mythread = MyThread(name = "Thread-{}".format(x + 1))  # ...Instantiate a thread and pass a unique ID to it
        mythread.daemon = True
        mythread.start()                                   # ...Start the thread
        thread_list.append(mythread)
        time.sleep(.9)                                     # ...Wait 0.9 seconds before starting another
        print "current active count: " + str(threading.active_count())

    time.sleep(10)
    print "current active thread count: " + str(threading.active_count())
    print "thread_list[1] is type: " + str(type(thread_list[1]))
    print "thread_list[1].is_alive(): " + str(thread_list[1].is_alive())

 