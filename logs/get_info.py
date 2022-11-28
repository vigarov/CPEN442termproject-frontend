# import required module
import os
from datetime import datetime
from Cryptodome.Hash import SHA256
import json
import pprint

if __name__ == '__main__':

    h = SHA256.new()
    h.update("6047385012".encode('utf-8'))

    # assign directory
    directory = h.hexdigest()[:6]

    # iterate over files in
    # that directory
    trials = []
    for filename in os.listdir(directory):
        fn = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(fn):
            f = open(fn, 'r')
            obj = json.loads(f.readline())
            trials.append(obj)


