#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import sys
import serial #pip3 install pyserial
import modbus_tk #pip3 install modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
import struct
import time


def GetModbusConnect(device):
	master = modbus_rtu.RtuMaster(serial.Serial(device, baudrate=115200, bytesize=8, parity='N', stopbits=2))
	master.set_timeout(1)
	master.set_verbose(True)
	master.open()
	return master
#end define

def ReadModbus(master, modbusID, reg, count):
	data = master.execute(modbusID, cst.READ_HOLDING_REGISTERS, reg, count)
	return data
#end define

def ModbusClose(master):
	master.close()
#end define

def ModbusDataToInt(data):
	buffer = b''
	for item in reversed(data):
		buffer += int.to_bytes(item, length=2, byteorder="big")
	return int.from_bytes(buffer, byteorder="big")
#end define

def ModbusDataToFloat(data):
	buffer = b''
	for item in reversed(data):
		buffer += int.to_bytes(item, length=2, byteorder="big")
	return struct.unpack('>f', buffer)[0]
#end define

def ModbusDataToDouble(data):
		buffer = b''
		for item in reversed(data):
				buffer += int.to_bytes(item, length=2, byteorder="big")
		return struct.unpack('>d', buffer)[0]
#end define

def ScanModbus():
	result = list()
	master = GetModbusConnect(device)
	master.set_timeout(0.3)
	for modbusID in range(1, 248):
		try:
			if (modbusID%25 == 0):
				print("percent:", int(modbusID/25)*10)
			data = ReadModbus(master, modbusID, 2, 4) # modbusID=1, reg=1, count=1
			print("find modbus device with adress:", modbusID)
			sn = ModbusDataToInt(data)
			buffer = {"modbusID":modbusID, "sn":sn}
			result.append(buffer)
		except modbus_tk.exceptions.ModbusInvalidResponseError:
			pass
		except KeyboardInterrupt:
			break
	ModbusClose(master)
	print("ScanModbus result:", result)
	return result
#ned define

def GetDataFromDevice(modbusID):
	outputData = list()
	master = GetModbusConnect(device)
	sn = ModbusDataToInt(ReadModbus(master, modbusID, 2, 4)) # modbusID=1, reg=2, count=4
	temp = ModbusDataToFloat(ReadModbus(master, modbusID, 6, 2)) # modbusID=1, reg=6, count=2
	buffer = {"sensorID":sensorID, "sn":sn, "temp":temp}
	outputData.append(buffer)
	ModbusClose(master)
	return outputData
#end define


###
### Start of the program
###

params = sys.argv
if ("-d" in params):
		device = params[params.index("-d")+1]
else:
		exit("{0} {1} {2} {3} {4}".format("Device not set.", "Set device with parameter -d.", "Example: python3", params[0], "-d /dev/ttyRS485-2 --scan"))
if ("--scan" in params):
		ScanModbus()
elif ("--get" in params and "-m" in params):
		modbusID_str = params[params.index("-m")+1]
		modbusID = int(modbusID_str)

		data = GetDataFromDevice(modbusID)
		print("data:", data)
else:
		exit("{0} {1} {2} {3} {4}".format("No parameters set.", "Set parameters.", "Example: python3", params[0], "-d /dev/ttyRS485-2 --get -m 1"))
#end if
