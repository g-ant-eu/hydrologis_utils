from hydrologis_utils.multithreading import HyThreadingPool, HyMultiProcessing

import unittest

# run with python3 -m unittest discover tests/

def doMProcess(params:dict):
    start = params["start"]
    end = params["end"]

    # make a multiplication and division in a loop between start and end
    sum = 0
    for i in range(start, end):
        i = i * 2
        i = i / 2
        sum += i

    return sum

class TestMultithreading(unittest.TestCase):
    def _doProcess(self, params:dict):
        start = params["start"]
        end = params["end"]

        # make a multiplication and division in a loop between start and end
        sum = 0
        for i in range(start, end):
            i = i * 2
            i = i / 2
            sum += i

        return sum
    
    def test_simple_multithreading(self):
        pool = HyThreadingPool(task=self._doProcess)
        count = 1000
        paramsList = []
        for i in range(0, count):
            params = {
                "start": i,
                "end": i+100
            }
            paramsList.append(params)

        results = pool.runThreads(paramsList)

        self.assertEqual(len(results), count)

    def test_simple_multiprocessing(self):
        pool = HyMultiProcessing(task=doMProcess)
        count = 1000
        paramsList = []
        for i in range(0, count):
            params = {
                "start": i,
                "end": i+100
            }
            paramsList.append(params)

        results = pool.runParallel(paramsList)

        self.assertEqual(len(results), count)

    


    




if __name__ == "__main__":
    unittest.main()