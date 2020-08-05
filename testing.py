import threading

class KeyboardThread(threading.Thread):
    run_thread=True
    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while self.run_thread:
            print("WAITING")
            self.input_cbk(input()) #waits to get input + Return
    def stop(self):
        self.run_thread=False

showcounter = 0 #something to demonstrate the change

def my_callback(inp):
    #evaluate the keyboard input
    print('You Entered:', inp, ' Counter is at:', showcounter)

#start the Keyboard thread
kthread = KeyboardThread(my_callback)

while True:
    try:
        #the normal program executes without blocking. here just counting up
        showcounter += 1
    except KeyboardInterrupt:
        print("KEYBOARD")
        kthread.stop()
        kthread.join()
        break
print("Exited")