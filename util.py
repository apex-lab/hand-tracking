import numpy as np
import os

from psychopy.hardware.keyboard import Keyboard
from psychtoolbox import hid

def init_keyboard(dev_name = 'Dell Dell USB Entry Keyboard'):
    devs = hid.get_keyboard_indices()
    idxs = devs[0]
    names = devs[1]
    try:
        idx = [idxs[i] for i, nm in enumerate(names) if nm == dev_name][0]
    except:
        raise Exception(
    'Cannot find %s! Available devices are %s.'%(dev_name, ', '.join(names))
        )
    return Keyboard(idx)

def fixation(win, t):
    '''
    displays a fixation cross for `t` seconds
    '''
    cross = visual.TextStim(win, text = '+', color = WHITE, height = MASK_SIZE / 10)
    cross.draw()
    win.flip()
    core.wait(.5)
    return

def _display_text(win, txt, **txt_kwargs):
    '''
    Parameters
    ----------
    win : psychopy.visual.Window
    txt : str
        Text to display.
    '''
    msg = visual.TextStim(
        win,
        text = txt,
        pos = (0,0),
        font = 'Arial',
        depth = -4.0,
        **txt_kwargs
        )
    msg.draw()
    win.flip()

def _wait_for_spacebar(kb):
    '''
    Parameters
    ----------
    kb : psychopy.hardware.Keyboard
    '''
    kb.waitKeys(keyList = ['space'], clear = True)

def show_instructions(win, kb, msg, max_width = None):
    if max_width is None:
        max_width = win.size[0]
    msg += '\n(Press the space bar to continue.)'
    _display_text(win, msg, wrapWidth = max_width)
    _wait_for_spacebar(kb)

def _generate_order():

	# gather stimuli and possible transitions between them
	positions = [os.path.join('stimuli', 'image_%d.jpeg'%i) for i in range(1, 9)]
	transitions = {pos: [p for p in positions if p != pos] for pos in positions}

	pos_list = []
	pos_list.append(np.random.choice(positions)) # start on a random position
	# then exhaust all possible transitions
	for i in range(len(positions) * (len(positions) - 1)): 
		np.random.shuffle(transitions[pos_list[-1]])
		next_pos = transitions[pos_list[-1]].pop()
		pos_list.append(next_pos)

	return pos_list

def generate_order():
	'''
	exhausts all possible transitions in random order, and then does it again
	'''
	order = []
	while len(order) < 100:
		try:
			order += _generate_order()
		except:
			continue
	return order




