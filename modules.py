# submit(task_no, user_id, file, model_name)

import os
import io
import requests
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm


# from Kaggle API
class TqdmBufferedReader(io.BufferedReader):
    def __init__(self, raw, progress_bar):
        """ helper class to implement an io.BufferedReader
             Parameters
            ==========
            raw: bytes data to pass to the buffered reader
            progress_bar: a progress bar to initialize the reader
        """
        io.BufferedReader.__init__(self, raw)
        self.progress_bar = progress_bar

    def read(self, *args, **kwargs):
        """ read the buffer, passing named and non named arguments to the
            io.BufferedReader function.
        """
        buf = io.BufferedReader.read(self, *args, **kwargs)
        self.increment(len(buf))
        return buf

    def increment(self, length):
        """ increment the reader by some length
            Parameters
            ==========
            length: bytes to increment the reader by
        """
        self.progress_bar.update(length)
       

#---
def submit(task_no, user_id, file, model_name=None):
    if model_name == None:
        user_id + '_' + datetime.now().strftime("%Y%m%d%H%M%S") + '_' + os.path.basename(file)
    file_size = os.path.getsize(file)
    session = requests.Session() # 세션 열기
    url = 'http://223.194.90.113:10463/submit'
    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
        with open(file, 'rb', buffering=0) as f:
            reader = TqdmBufferedReader(f, progress_bar)
            retries = Retry(total=10, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retries)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            # files에서 tuple은 flask에서는 value로, 단일 파일은 files로 받는다.
            files = {'user_id': (None, user_id),
                     'task_no': (None, str(task_no)), 
                     'file_name': (None, os.path.basename(file)),
                     'file': reader, # flask에서 files로 받는 파트
                     'model_name': (None, model_name)}
            response = session.post(url, files=files, stream=True)
    print(f'\n{response.text}: {response.status_code}')
    session.close() 