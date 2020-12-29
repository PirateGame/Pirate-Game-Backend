import app
import threading

from threading import Thread
"""
See reference: 
https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python/40344234#40344234
Check the answer by GuySoft.
"""
class AsAThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None # child class's variable, not available in parent.
 
    def run(self):
        """
        The original run method does not return value after self._target is run.
        This child class added a return value.
        :return: 
        """
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
 
    def join(self, *args, **kwargs):
        """
        Join normally like the parent class, but added a return value which
        the parent class join method does not have. 
        """
        super().join(*args, **kwargs)
        return self._return

### WAIT FOR RESPONSE FROM THE WEBSITE...

result_available = threading.Event()
global response
response = []
def awaitResponse(choice):
    print("waiting on", choice)
    thread = AsAThread(target=app.awaitResponseProcess, args=[choice])
    thread.start()
    # wait here for the result to be available before continuing
    result_available.wait()
    return thread.join()