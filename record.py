from os.path import join, dirname, realpath
import sys
import os

# RoSeMotion makes a lot of references to internal files so
# it's easier to just use its app module as working directory
this_dir = dirname(realpath(__file__))
rose_dir = join(this_dir, 'RoSeMotion', 'app')
sys.path.append(rose_dir)
os.chdir(rose_dir)

from resources.LeapSDK.v53_python39 import Leap
from LeapData import LeapData
from glove import GloveRecorder, WinClock

from time import time, strftime
import numpy as np
import pandas as pd

OUTPUT_DIR = 'output'
str_time = strftime('%Y%m%d-%H%M%S')
LEAP_OUTPUT_FILE = 'leap_%s.tsv'%str_time
GLOVE_OUTPUT_FILE = 'glove_%s.tsv'%str_time

clock = WinClock()

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
        self._motions.append((clock.time(), channel_values))
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
    glove_recorder = GloveRecorder(glove_f, port = 'USB0')
    glove_recorder.start()
    ## set up recording from leap motion
    print('starting leap motion...')
    listener = Listener()
    controller = Leap.Controller()
    controller.add_listener(listener)
    input('Press enter to stop...')
    glove_recorder.stop()
    print('Terminated glove recording...')
    controller.remove_listener(listener)
    print('Terminated Leap recording...')
    df = listener.exit()
    df.iloc[1:, :].to_csv(leap_f, sep = '\t', index = False)
    print('Saved!')
