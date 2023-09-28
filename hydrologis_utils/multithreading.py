"""
Utilities to work with multithreading.
"""

import concurrent.futures
import multiprocessing
import threading
from multiprocessing import Pool

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
    

class HyMultiProcessing():
    """
    A class to run a function in parallel with multiprocessing.

    Parameters
    ----------
    task: function
        The function to run in parallel. This needs to be a toplevel function,
        not include global variables that reference unpickable objects and 
        use standard library functions.

    cores: int, optional
        The number of cores to use. If not given, all available cores are used.


    """

    def __init__(self, task, cores = None) -> None:
        if not task:
            raise Exception("No task given to run in parallel.")
        else:
            self.task = task

        if not cores:
            self.cores = multiprocessing.cpu_count()
        else:
            self.cores = cores
        
        multiprocessing.set_start_method("fork", force=True)
        
    def runParallel(self, paramsList:list):
        """
        Run a function in parallel with multiprocessing.
        
        Parameters
        ----------
        paramsList: list
            A list of lists of parameters to pass in a loop to the function
            and run in parallel.
        
        Returns
        -------
        results: list
            A list of results from the function.
        
        """

        pool = Pool(self.cores)
        results = pool.map(self.task, paramsList)
        pool.close()
        pool.join()

        processed_data = list(results)

        return processed_data