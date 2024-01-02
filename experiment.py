from os.path import join, dirname, realpath
from time import strftime
import numpy as np
import pandas as pd
import sys
import os

from glove import GloveRecorder, WinClock
from glove.logging import TSVLogger

from psychopy import visual, core
from util import (
    init_keyboard,
    fixation,
    show_instructions,
    _display_text,
    generate_order,
    TRSync
    )

clock = WinClock() # clock.time() is essentially time.perf_counter(),
# but perf_counter doesn't have consistent zero across processes in Python 3.9

###### Config ############

LOG_DIR = 'logs'
MRI_EMULATED_KEY = 's'
KB_NAME = 'Keyboard'

###### Experiment code #######

def main(log_fpath):

    # create log file
    log = TSVLogger(log_fpath,
        fields = ['timestamp', 'target_position']
        )

    win = visual.Window(
        size = (1920, 1080),
        color = (-1, -1, -1),
        screen = -1,
        units = "norm",
        fullscr = False,
        pos = (0, 0),
        allowGUI = False
        )
    kb = init_keyboard(KB_NAME)
    positions = generate_order()

    show_instructions(win, kb,
    '''
    In this task, you will be show pictures of hand gestures.
    Your job is to mimic the position of the displayed hand with your own.

    As each new image appears, please transition your hand directly
    from the previous gesture to the new gesture and hold the position
    until another gesture appears.
    '''
    )
    show_instructions(win, kb,
    '''
    As you do this, please keep your wrist straight and palm facing down,
    and try not to move any part of your body other than your fingers.

    It is especially important that your head remain still while in the scanner.
    '''
    )
    show_instructions(win, kb,
    '''
    You may now begin.
    '''
    )

    def record_event(name):
        log.write(timestamp = clock.time(), target_position = name)

    for position in positions:
        image = visual.ImageStim(win, position)
        image.draw()
        win.callOnFlip(record_event, name = position)
        win.flip()
        core.wait(5.)
    log.write(timestamp = clock.time(), target_position = 'n/a')
    log.close()

    _display_text(win,
    '''
    You have finished this block!

    Please continue to remain still as you await instructions.
    '''
    )

    # await experimenter
    print('\n\nExperiment has finished!\nIs MRI finished?')
    input('\nPress enter to end script.')
    return


###### Setup & Recording #########

if __name__ == '__main__':

    ## get run params from experimenter
    subj_num = input("Enter subject number: ")
    sub = '%02d'%int(subj_num)
    run_num = int(input("Enter run number: "))
    run = '%02d'%int(run_num)

    output_dir = os.path.join(LOG_DIR, 'sub-%s'%sub, 'run-%s'%run)
    if os.path.exists(output_dir):
        raise Exception('sub-%s_run-%s already exists!')
    else:
        os.makedirs(output_dir)
    glove_f = os.path.join(output_dir, 'glove.tsv')
    log_f = os.path.join(output_dir, 'events.tsv')
    tr_f = os.path.join(output_dir, 'TRs.tsv')

    glove_recorder = GloveRecorder(glove_f, port = 'USB0')
    glove_recorder.start()

    tr_listener = TRSync(tr_f, KB_NAME, MRI_EMULATED_KEY)
    tr_listener.start()
    print('\n\nListening for TRs!\n\n')

    print('\n\nIs MRI ready?')
    input('\nPress enter to begin experiment.')
    main(log_f)

    tr_listener.stop()
    glove_recorder.stop()
