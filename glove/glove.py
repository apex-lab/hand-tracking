from os.path import join, dirname, realpath
import ctypes.wintypes as wintypes
from ctypes import *
import sys 
import os

## make sure Python knows where to look for glove driver
this_dir = dirname(realpath(__file__))
os.add_dll_directory(this_dir)


class FiveDTGlove:
    """5DT Glove Ultra Python Wrapper

    Wraps the fglove.dll driver

    Usage:
    glove = FiveDTGlove()
    glove.open("USB0")
    glove.getSensorScaled(glove.FD_THUMBNEAR)
    glove.close()
    
    """

    # TODO: check if we can map these values directly from the DLL?
    
    # Glove Types
    FD_GLOVENONE = 0  
    FD_GLOVE5U = 1	
    FD_GLOVE5UW = 2	
    FD_GLOVE5U_USB = 3
    FD_GLOVE7 = 4     
    FD_GLOVE7W = 5    
    FD_GLOVE16 = 6    
    FD_GLOVE16W = 7   
    FD_GLOVE14U = 8	
    FD_GLOVE14UW = 9	
    FD_GLOVE14U_USB = 10

    # Glove Hand Types
    FD_HAND_LEFT = 0
    FD_HAND_RIGHT = 1

    # Sensor Types
    FD_THUMBNEAR = 0
    FD_THUMBFAR = 1
    FD_THUMBINDEX = 2
    FD_INDEXNEAR = 3
    FD_INDEXFAR = 4
    FD_INDEXMIDDLE = 5
    FD_MIDDLENEAR = 6
    FD_MIDDLEFAR = 7
    FD_MIDDLERING = 8
    FD_RINGNEAR = 9
    FD_RINGFAR = 10
    FD_RINGLITTLE = 11
    FD_LITTLENEAR = 12
    FD_LITTLEFAR = 13
    FD_THUMBPALM = 14
    FD_WRISTBEND = 15
    FD_PITCH = 16
    FD_ROLL = 17
    
    def __init__(self):
        '''
        I've updated this class from 5DT's demo for Python 3 and 64bit compatibility.

        Only some methods work, since I only changed the ones I need. If you want to make 
        a currently dysfunctional method work for you, my first suggestion would be to set 
        the restype and argtypes for the relevant call to fglove64, since ctypes 
        uses 32 bit integer encodings by default - and we're now using 64 bit python 
        with a 64 bit library. The second thing I'd check is string encoding. fglove64 
        expects ascii, but Python 3 (unlike Python 2) uses unicode by default. You should
        change the encoding as I did in the .open() method. 
        '''

        self._as_parameter_ = 5
        
        self.gloveDLL = cdll.LoadLibrary("fglove64")
        self.gloveDLL.fdOpen.restype = c_int64
        self.gloveDLL.fdClose.argtypes = [c_int64]
        self.gloveDLL.fdGetSensorRawAll.argtypes = [c_int64]
        self.gloveDLL.fdGetNumSensors.restype = c_int64
        self.gloveDLL.fdNewData.argtypes = [c_int64]
        self.gloveDLL.fdNewData.restype = c_bool

        if self.gloveDLL == None:
            raise IOError("Could not open fglove.dll")

    def open(self, port):
        """Opens the 5DT Glove Ultra.

        port: string value of the port name. For example 'USB0'
            
        Opens the 5DT Glove
        This function needs to be called first
        
        """
        port = port.encode('ascii') # accomodate Python 2->3 change 
        self.glovePntr = 0;
        self.glovePntr = self.gloveDLL.fdOpen(port)
        if self.glovePntr == 0:
            raise IOError("Could not connect to 5DT glove.")            
            
    def close(self):
        """Close the connection with the glove."""
        self.gloveDLL.fdClose(self.glovePntr)

    def getGloveHand(self):
        """Get the glove hand type. Returns either FD_HAND_LEFT or FD_HAND_RIGHT"""
        return self.gloveDLL.fdGetGloveHand(self.glovePntr)

    def getGloveType(self):
        """Get the glove type number. Returns FD_GLOVENONE, FD_GLOVE5U etc"""
        return self.gloveDLL.fdGetGloveType(self.glovePntr)

    def getNumSensors(self):
        """Get the number of sensors on the Glove."""
        return self.gloveDLL.fdGetNumSensors(self.glovePntr)

    def getSensorRawAll(self):
        """Get a list of all the current raw sensor values."""
        arrTypeUShortArray20 = c_ushort*20
        sensorRawValues = arrTypeUShortArray20()
        self.gloveDLL.fdGetSensorRawAll(self.glovePntr, sensorRawValues)
        #numSensors = self.gloveDLL.fdGetNumSensors(self.glovePntr)
        return list(sensorRawValues)

    def getSensorRaw(self, nSensor):
        """Get a single raw sensor value, with index defined by argument 'nSensor'"""
        sensorVal = c_ushort(0)
        funct = self.gloveDLL.fdGetSensorRaw
        funct.restype = c_ushort
        sensorVal = funct(self.glovePntr, nSensor)
        return sensorVal

    def getSensorScaledAll(self):
        """Get a list of all the current scaled sensor values."""
        arrTypeFloatArray20 = c_float*20
        sensorRawValues = arrTypeFloatArray20()     
        self.gloveDLL.fdGetSensorScaledAll(self.glovePntr, sensorRawValues)          
        return list(sensorRawValues)

    def getSensorScaled(self, nSensor):
        """Get a single scaled sensor value, with index defined by argument 'nSensor'"""
        sensorVal = c_float(0)
        funct = self.gloveDLL.fdGetSensorScaled
        funct.restype = c_float
        sensorVal = funct(self.glovePntr, nSensor)
        return sensorVal        

    def getNumGestures(self):
        """Get the number of Gestures available.
        The different gestures are explained in the manual.

        """
        return self.gloveDLL.fdGetNumGestures(self.glovePntr)
   
    def getGesture(self):
        """Get the current gesture.
        The different gestures are explained in the manual."""    
        return self.gloveDLL.fdGetGesture(self.glovePntr)

    def getCalibration(self, nSensor):
        """Get the calibration of the sensor index given by argument 'nSensor'
        Return a list of 2 items, containing the upper value and lower value.
        """
        calibrationUpper = c_ushort(0)         
        calibrationLower = c_ushort(0)        
        self.gloveDLL.fdGetCalibration(self.glovePntr, nSensor, pointer(calibrationUpper), pointer(calibrationLower))
        return [calibrationUpper.value, calibrationLower.value]    

    def getCalibrationAll(self):
        """Get all the calibration information.
        Return a list of 2 lists: [list_of_upper_vals, list_of_lower_vals]
        
        """
        arrTypeUShortArray20 = c_ushort*20
        calibrationUpper = arrTypeUShortArray20()           
        calibrationLower = arrTypeUShortArray20()        
        self.gloveDLL.fdGetCalibrationAll(self.glovePntr, calibrationUpper, calibrationLower)
        return [list(calibrationUpper), list(calibrationLower)]

    def resetCalibration(self, nSensor):
        """Reset the calibration of a specific sensor index, indicated by argument nSensor"""
        self.gloveDLL.fdResetCalibration(self.glovePntr, nSensor)

    def resetCalibrationAll(self):
        """Reset the calibration of all the sensors."""
        self.gloveDLL.fdResetCalibrationAll(self.glovePntr)

    def getThresholdAll(self):
        """Get the current gesture recognition threshold settings of the driver."""
        arrTypeFloatArray20 = c_float*20
        thresholdUpper = arrTypeFloatArray20()           
        thresholdLower = arrTypeFloatArray20()        
        self.gloveDLL.fdGetThresholdAll(self.glovePntr, thresholdUpper, thresholdLower)
        return [list(thresholdUpper), list(thresholdLower)]

    def setThresholdAll(self, lstUpper, lstLower):
        """Set the gesture recognition thresholds of all the sensors.
        lstUpper should contain a list of all the upper values.
        lstLower should contain a list of all the lower values.

        Please see the manual for an explanation on glove gestures.

        """
        if not isinstance(lstUpper, list) or not isinstance(lstUpper, list):
            raise ValueError("Input argument lstUpper and lstLower should be of type list")
            
        arrTypeFloatArray20 = c_float*20
        thresholdUpper = arrTypeFloatArray20(*lstUpper)           
        thresholdLower = arrTypeFloatArray20(*lstLower)        
        self.gloveDLL.fdSetThresholdAll(self.glovePntr, thresholdUpper, thresholdLower)
        return
        
    def setThreshold(self, nSensor, valUpper, valLower):
        """Set the gesture recognition threshold of a specific sensor.
        nSensor: The index of the senor to set the threshold of
        valUpper: The upper value for gesture recognition
        valLower: The lower value for gesture recognition

        Please see the manual for an explanation on glove gestures.
        
        """
        self.gloveDLL.fdSetThreshold(self.glovePntr, nSensor, c_float(valUpper), c_float(valLower))
        return

    def getGloveInfo(self):
        """Get glove information and return it as a string"""
        charBuffer = create_string_buffer(256)
        self.gloveDLL.fdGetGloveInfo(self.glovePntr, byref(charBuffer))
        return str(charBuffer.value)

    def getDriverInfo(self):
        """Get driver information and return it as a string"""
        charBuffer = create_string_buffer(256)
        self.gloveDLL.fdGetDriverInfo(self.glovePntr, byref(charBuffer))
        return str(charBuffer.value)

    def _set_callback_func(self):
        def function(call):
            print('new sample')
        CMPFUNC = CFUNCTYPE(None, wintypes.LPVOID)
        func = CMPFUNC(function)
        self.gloveDLL.fdSetCallback.argtypes = [c_int64, POINTER(CMPFUNC), wintypes.LPVOID]
        self.gloveDLL.fdSetCallback(self.glovePntr, byref(func), wintypes.LPVOID(None)) 
        

    def setCallback(self, function):
        """Set the callback function.

        This function will be called each time the driver receives new data.

        """
        CMPFUNC = CFUNCTYPE(c_bool, wintypes.LPVOID)
        func = CMPFUNC(function)
        ptr = c_void_p(pointer(self))
        self.gloveDLL.fdSetCallback(self.glovePntr, func, wintypes.LPVOID(None))    
        return

    def removeCallback(self):
        """Remove the current callback function."""
        self.gloveDLL.fdRemoveCallback(self.glovePntr)
        return

    def getPacketRate(self):
        """Get the rate of packets recieved from the glove by the driver."""
        return self.gloveDLL.fdGetPacketRate(self.glovePntr)

    def newData(self):
        """Return a boolean value indicating if new data has been received."""
        return self.gloveDLL.fdNewData(self.glovePntr)
    
    def getFWVersionMajor(self):
        """Get the major version of the firmware."""
        return self.gloveDLL.fdGetFWVersionMajor(self.glovePntr)

    def getFWVersionMinor(self):
        """Get the minor version of the firmware."""
        return self.gloveDLL.fdGetFWVersionMinor(self.glovePntr)

    def getAutoCalibrate(self):
        """Get the current state of the Autocalibration feature.
        If a glove is set to use autocalibration, the sensor scaled values will automatically
        be calculated from the maximum and minimum raw values recorded since the driver
        was loaded.

        """
        return self.gloveDLL.fdGetAutoCalibrate(self.glovePntr)

    def setAutoCalibrate(self, bAutocalibrate):
        """Set the autocalibraiton feature on or off.
        If a glove is set to use autocalibration, the sensor scaled values will automatically
        be calculated from the maximum and minimum raw values recorded since the driver
        was loaded.

        """
        if not isinstance(bAutocalibrate, bool):
            raise ValueError("Input argument bAutocalibrate needs to be a boolean value")
        return self.gloveDLL.fdSetAutoCalibrate(self.glovePntr, bAutocalibrate)

    def saveCalibration(self, sFileName):
        """Save calibration to file."""
        if not isinstance(sFileName, str):
            raise ValueError("Input argument sFileName needs to be a string value")
        cFileString = create_string_buffer(sFileName)
        return self.gloveDLL.fdSaveCalibration(self.glovePntr, cFileString)

    def loadCalibration(self, sFileName):
        """Load calibration from file."""
        if not isinstance(sFileName, str):
            raise ValueError("Input argument sFileName needs to be a string value")
        cFileString = create_string_buffer(sFileName)
        return self.gloveDLL.fdLoadCalibration(self.glovePntr, cFileString)

    def getSerialNumber(self):
        """Get the glove serial number."""
        sSerialNumberbuffer = create_string_buffer(256)
        self.gloveDLL.fdGetSerialNumber(self.glovePntr, sSerialNumberbuffer)
        return str(sSerialNumberbuffer.value)


