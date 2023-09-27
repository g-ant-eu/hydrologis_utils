"""
Utilities to work with multithreading.
"""

import concurrent.futures
import multiprocessing
import threading

class HyThreadingPool():


    def __init__(self, task, threads = None, name = "hythread") -> None:
        self.name = name
        self.index = 0
        if not task:
            raise Exception("No task given to run in threads.")
        else:
            self.task = task
        if not threads:
            self.threads = multiprocessing.cpu_count()
        else:
            self.threads = threads

    def setThreadName(self):
        self.index += 1
        threading.current_thread().name = f"{self.name}-{self.index}"


    def runThreads(self, params:list):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:

            # Submit tasks to the thread pool and get futures
            futures = []
            for param in params:
                future = executor.submit(self.task, param)
                future.add_done_callback(lambda _: self.setThreadName())
                futures.append(future)

            # Wait for all tasks to complete and collect results
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

            return results
    
