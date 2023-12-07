from multiprocessing import Process, Event
from .glove import FiveDTGlove
from .logging import TSVLogger

from time import time
from ctypes import wintypes
import ctypes

CH_NAMES = dict( # channel names and indices for 14 channel glove
	FD_THUMBNEAR = 0,
	FD_THUMBFAR = 1,
	FD_THUMBINDEX = 2,
	FD_INDEXNEAR = 3,
	FD_INDEXFAR = 4,
	FD_INDEXMIDDLE = 5,
	FD_MIDDLENEAR = 6,
	FD_MIDDLEFAR = 7,
	FD_MIDDLERING = 8,
	FD_RINGNEAR = 9,
	FD_RINGFAR = 10,
	FD_RINGLITTLE = 11,
	FD_LITTLENEAR = 12,
	FD_LITTLEFAR = 13
)

class WinClock:
	'''
	provides more precise time than built-in time.time() for Windows
	'''
	def __init__(self):
	    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
	    kernel32.QueryPerformanceFrequency.argtypes = (
	        wintypes.PLARGE_INTEGER,) # lpFrequency
	    kernel32.QueryPerformanceCounter.argtypes = (
	        wintypes.PLARGE_INTEGER,) # lpPerformanceCount
	    _qpc_frequency = wintypes.LARGE_INTEGER()
	    if not kernel32.QueryPerformanceFrequency(ctypes.byref(_qpc_frequency)):
	        raise ctypes.WinError(ctypes.get_last_error())
	    self._qpc_frequency = _qpc_frequency.value
		self._k32 = kernel32

	def time(self):
		count = wintypes.LARGE_INTEGER()
        if not self._k32.QueryPerformanceCounter(ctypes.byref(count)):
            raise ctypes.WinError(ctypes.get_last_error())
        return count.value / self._qpc_frequency


def record_from_glove(stop_event, glove_output, glove_port):
    glove = FiveDTGlove()
    glove.open(glove_port)
	ch_names = [key for key in CH_NAMES]
	ch_names.sort(key = lambda ch: CH_NAMES[ch])
	log = TSVLogger(glove_output, ch_names + ['timestamp'])
	clock = WinClock()
    while not stop_event.is_set():
        is_new_data = glove.newData()
        if is_new_data:
            vals = glove.getSensorRawAll()
            ch_vals = {ch: vals[idx] for ch, idx in CH_NAMES.items()}
            ch_vals['timestamp'] = clock.time()
            log.write(**ch_vals)
	log.close()
    glove.close()


class GloveRecorder:

	def __init__(self, rec_fpath, port = 'USB0'):
		self.fpath = rec_fpath
		self.port = port

	def start(self):
		self._stop_event = Event()
		self._process = Process(
			target = record_from_glove,
			args = (self._stop_event, self.fpath, self.port)
			)
		self._process.start()

	def stop(self):
		self._stop_event.set()
		self._process.join()
