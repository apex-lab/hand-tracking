from os.path import join, dirname, realpath
import sys 
import os

# RoSeMotion makes a lot of references to internal files so 
# it's easier to just use its app module as working directory 
this_dir = dirname(realpath(__file__))
rose_dir = join(this_dir, 'RoSeMotion', 'app')
sys.path.append(rose_dir)
os.chdir(rose_dir)


from multiprocessing import Process, Event
from glove import FiveDTGlove, CH_NAMES
from resources.LeapSDK.v53_python39 import Leap 
from LeapData import LeapData
from time import time, strftime
import numpy as np
import pandas as pd

OUTPUT_DIR = 'output'
LEAP_OUTPUT_FILE = 'leap_%s.csv'%strftime('%Y%m%d-%H%M%S')
GLOVE_OUTPUT_FILE = 'glove_%s.csv'%strftime('%Y%m%d-%H%M%S')

class DataHandler(LeapData):
    '''
    Handles converting joint positions to joint angles 
    '''
    def add_frame(self, frame):
        if not self._check_frame(frame):
            return None

        # Get the first hand
        hand = frame.hands[0]
        if not self.first_frame:
            self.first_frame = frame
            channel_values = self._get_channel_values(hand, firstframe=True)
            self._motions.append((0, channel_values))
            return

        channel_values = self._get_channel_values(hand)
        self._motions.append((time(), channel_values))
        return frame

    def _motion2dataframe(self):
        """Returns all of the channels parsed from the LeapMotion sensor as a pandas DataFrame"""
        time_index = pd.to_timedelta([f[0] for f in self._motions], unit='s')
        frames = [f[1] for f in self._motions]
        channels = np.asarray([[channel[2] for channel in frame] for frame in frames])
        column_names = ['%s_%s' % (c[0], c[1]) for c in self._motion_channels]

        df = pd.DataFrame(data=channels, index=time_index, columns=column_names)
        df['timestamp'] = [f[0] for f in self._motions]
        return df


class Listener(Leap.Listener):
    '''
    Records samples from Leap Motion Controller,
    and returns sample dataframe (joint angles) upon exit
    '''

    def __init__(self):
        super(Listener, self).__init__()
        self.leap2bvh = DataHandler(frame_rate = 1/60)

    def on_connect(self, controller):
        print('Connected to Leap Motion controller.')

    def on_frame(self, controller):
        frame = controller.frame()
        self.leap2bvh.add_frame(frame)
        return

    def exit(self):
        df = self.leap2bvh.parse().values
        return df 


def record_from_glove(stop_event, glove_output):
    glove = FiveDTGlove()
    glove.open('USB0')
    data = []
    while not stop_event.is_set():
        is_new_data = glove.newData()
        if is_new_data:
            vals = glove.getSensorRawAll()
            ch_vals = {ch: vals[idx] for ch, idx in CH_NAMES.items()}
            ch_vals['timestamp'] = time()
            data.append(ch_vals)
    glove.close()
    df = pd.DataFrame(data) # TO-DO: for main experiment, we shouldn't be 
    df.to_csv(glove_output) # holding all the data in memory


if __name__ == '__main__':
    '''
    Record from the Leap Motion and the Data Glove simultaneously 
    '''
    output_dir = join(this_dir, OUTPUT_DIR)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    leap_f = join(output_dir, LEAP_OUTPUT_FILE)
    glove_f = join(output_dir, GLOVE_OUTPUT_FILE)
    ## set up recording from data glove
    print('starting data glove...')
    stop_event = Event()
    glove_process = Process(target = record_from_glove, args = (stop_event, glove_f))
    glove_process.start()
    ## set up recording from leap motion
    print('starting leap motion...')
    listener = Listener()
    controller = Leap.Controller()
    controller.add_listener(listener)
    input('press enter to stop...')
    stop_event.set()
    glove_process.join()
    print('done')
    controller.remove_listener(listener)
    df = listener.exit()
    df.to_csv(leap_f)
    print('saved!')

