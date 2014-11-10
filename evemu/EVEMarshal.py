from struct import *
from operator import itemgetter
import logging, pdb

class EVEMarshal:
	global EVEMarshalOpCodes

	def __init__(self):
		self.EVEMarshalOpCodes = {
			'none': 		0x01,
			'longlong':		0x03,
			'long': 		0x04,
			'short': 		0x05,
			'byte':			0x06,
			'minusone':		0x07,
			'zero':			0x08,
			'one':			0x09,
			'double':		0x0A,
			'zerodouble':	0x0B,
			'longstring': 	0x13,
			'tuple': 		0x14,
			'dict':			0x16,
			'twotuple':		0x2C,
			'utf8string':	0x2E
		}

	def marshal(self, data):
		if type(data).__name__ == 'NoneType':
			return pack('<b', self.EVEMarshalOpCodes['none'])
		elif type(data).__name__ == 'int':
			if data == -1:
				return pack('<b', self.EVEMarshalOpCodes['minusone'])
			elif data == 0:
				return pack('<b', self.EVEMarshalOpCodes['zero'])
			elif data == 1:
				return pack('<b', self.EVEMarshalOpCodes['one'])
			elif data >= -128 and data <= 127:
				return self.marshalByte(data)
			elif data >= -32768 and data <= 32767:
				return self.marshalShort(data)
			elif data >= -2147483648 and data <= 2147483647:
				return self.marshalLong(data)
			else:
				return self.marshalLongLong(data)
		elif type(data).__name__ == 'float':
			if data == 0:
				return pack('<b', self.EVEMarshalOpCodes['zerodouble'])
			else:
				return self.marshalDouble(data)
		elif type(data).__name__ == 'str':
			return self.marshalLongString(data)
		elif type(data).__name__ == 'tuple':
			return self.marshalTuple(data)
		else:
			logging.error("Unknown data type to be marshalled: %s", type(data).__name__)
			return None

	def marshalByte(self, data):
		marshalledData =  pack('<b', self.EVEMarshalOpCodes['byte'])
		marshalledData += pack('<b', data)
		return marshalledData

	def marshalShort(self, data):
		marshalledData = pack('<b', self.EVEMarshalOpCodes['short'])
		marshalledData += pack('<h', data)
		return marshalledData

	def marshalLong(self, data):
		marshalledData = pack('<b', self.EVEMarshalOpCodes['long'])
		marshalledData += pack('<l', data)
		return marshalledData

	def marshalLongLong(self, data):
		marshalledData = pack('<b', self.EVEMarshalOpCodes['longlong'])
		marshalledData += pack('<q', data)
		return marshalledData

	def marshalDouble(self, data):
		marshalledData = pack('<b', self.EVEMarshalOpCodes['double'])
		marshalledData += pack('<d', data)
		return marshalledData

	def marshalLongString(self, data):
		marshalledData = pack('<b', self.EVEMarshalOpCodes['longstring'])
		marshalledData += pack('<b', len(data))
		marshalledData += bytes(data, "UTF-8")
		return marshalledData

	def marshalTuple(self, data):
		marshalledData = pack('<b', self.EVEMarshalOpCodes['tuple'])
		#TODO: fix self so strings over 255 bytes can be sent
		marshalledData += pack('<b', len(data))

		# Marshal each part of the tuple
		for element in data:
			marshalledData += self.marshal(element)

		return marshalledData

	def unmarshal(self, data):
		if data[0] == self.EVEMarshalOpCodes['none']:
			return None
		elif data[0] == self.EVEMarshalOpCodes['longlong']:
			marhsalledData = data[1:9]
			return unpack('<q', marhsalledData)[0]
		elif data[0] == self.EVEMarshalOpCodes['long']:
			marhsalledData = data[1:5]
			return unpack('<l', marhsalledData)[0]
		elif data[0] == self.EVEMarshalOpCodes['short']:
			marhsalledData = data[1:3]
			return unpack('<h', marhsalledData)[0]
		elif data[0] == self.EVEMarshalOpCodes['byte']:
			marshalledData = data[1]
			return unpack('<b', marshalledData)[0]
		elif data[0] == self.EVEMarshalOpCodes['minusone']:
			return -1
		elif data[0] == self.EVEMarshalOpCodes['zero']:
			return 0
		elif data[0] == self.EVEMarshalOpCodes['one']:
			return 1
		elif data[0] == self.EVEMarshalOpCodes['double']:
			marshalledData = data[1:9]
			return unpack('<d', marshalledData)[0]
		elif data[0] == self.EVEMarshalOpCodes['zerodouble']:
			return 0.0
		elif data[0] == self.EVEMarshalOpCodes['longstring']:
			marshalledData = data[2:data[2]+1]

			return marshalledData
		elif data[0] == self.EVEMarshalOpCodes['tuple']:
			unmarshaledList = list()
			numElements = data[1]

			element = 0
			currentByte = 2
			while element < numElements:
				# All opcode only data sets
				if data[currentByte] == self.EVEMarshalOpCodes['none'] or data[currentByte] == self.EVEMarshalOpCodes['minusone'] or data[currentByte] == self.EVEMarshalOpCodes['zero'] or data[currentByte] == self.EVEMarshalOpCodes['one'] or data[currentByte] == self.EVEMarshalOpCodes['zerodouble']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+1]))
					currentByte +=1
				# One byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['byte']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+2]))
					currentByte += 2
				# Two byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['short']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+3]))
					currentByte += 3
				# 4 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['long']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+5]))
					currentByte += 5
				# 8 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['longlong'] or data[currentByte] == self.EVEMarshalOpCodes['double']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+9]))
					currentByte += 9

				elif data[currentByte] == self.EVEMarshalOpCodes['longstring']:
					stringData = bytearray()
					for x in range(currentByte + 2, currentByte + data[currentByte + 1] + 2):
						stringData += pack('B', data[x])
					unmarshaledList.append(stringData.decode("utf-8"))
					currentByte += len(stringData) + 2

				elif data[currentByte] == self.EVEMarshalOpCodes['tuple']:
					logging.error("Unmarhsaling tuple within tuple is not supported yet")

				element += 1
			
			return tuple(unmarshaledList)

		elif data[0] == self.EVEMarshalOpCodes['dict']:
			# packed as value and then key
			numElements = data[1]
			element = 0
			currentByte = 2
			retDict = {}

			while element < numElements:
				#
				# Get value
				#

				# All opcode only data sets
				if data[currentByte] == self.EVEMarshalOpCodes['none'] or data[currentByte] == self.EVEMarshalOpCodes['minusone'] or data[currentByte] == self.EVEMarshalOpCodes['zero'] or data[currentByte] == self.EVEMarshalOpCodes['one'] or data[currentByte] == self.EVEMarshalOpCodes['zerodouble']:
					value = self.unmarshal(data[currentByte:currentByte+1])
					currentByte +=1
				# One byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['byte']:
					value = self.unmarshal(data[currentByte:currentByte+2])
					currentByte += 2
				# Two byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['short']:
					value = self.unmarshal(data[currentByte:currentByte+3])
					currentByte += 3
				# 4 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['long']:
					value = self.unmarshal(data[currentByte:currentByte+5])
					currentByte += 5
				# 8 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['longlong'] or data[currentByte] == self.EVEMarshalOpCodes['double']:
					value = self.unmarshal(data[currentByte:currentByte+9])
					currentByte += 9

				elif data[currentByte] == self.EVEMarshalOpCodes['longstring'] or data[currentByte] == self.EVEMarshalOpCodes['utf8string']:
					try:
						value = data[currentByte+2:currentByte+data[currentByte+1]+2].decode("utf-8")
					except UnicodeDecodeError:
						value = data[currentByte+2:currentByte+data[currentByte+1]+2]
					currentByte += data[currentByte+1] + 2
				else:
					logging.error("Can't decode dict value of type %s", data[currentByte])

				#
				# Get key
				#

				# All opcode only data sets
				if data[currentByte] == self.EVEMarshalOpCodes['none'] or data[currentByte] == self.EVEMarshalOpCodes['minusone'] or data[currentByte] == self.EVEMarshalOpCodes['zero'] or data[currentByte] == self.EVEMarshalOpCodes['one'] or data[currentByte] == self.EVEMarshalOpCodes['zerodouble']:
					key = self.unmarshal(data[currentByte:currentByte+1])
					currentByte +=1
				# One byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['byte']:
					key = self.unmarshal(data[currentByte:currentByte+2])
					currentByte += 2
				# Two byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['short']:
					key = self.unmarshal(data[currentByte:currentByte+3])
					currentByte += 3
				# 4 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['long']:
					key = self.unmarshal(data[currentByte:currentByte+5])
					currentByte += 5
				# 8 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['longlong'] or data[currentByte] == self.EVEMarshalOpCodes['double']:
					key = self.unmarshal(data[currentByte:currentByte+9])
					currentByte += 9

				elif data[currentByte] == self.EVEMarshalOpCodes['longstring'] or data[currentByte] == self.EVEMarshalOpCodes['utf8string']:
					try:
						#print(data)
						key = data[currentByte+2:currentByte+data[currentByte+1]+2].decode("utf-8")
					except UnicodeDecodeError:
						key = data[currentByte+2:currentByte+data[currentByte+1]+2]
					currentByte += data[currentByte+1] + 2
				else:
					logging.error("Can't decode dict key of type %s", data[currentByte])

				# add to dict
				retDict[key] = value
				element += 1

			return retDict

		elif data[0] == self.EVEMarshalOpCodes['twotuple']:
			unmarshaledList = list()

			element = 0
			currentByte = 1
			while element < 2:
				# All opcode only data sets
				if data[currentByte] == self.EVEMarshalOpCodes['none'] or data[currentByte] == self.EVEMarshalOpCodes['minusone'] or data[currentByte] == self.EVEMarshalOpCodes['zero'] or data[currentByte] == self.EVEMarshalOpCodes['one'] or data[currentByte] == self.EVEMarshalOpCodes['zerodouble']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+1]))
					currentByte +=1
				# One byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['byte']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+2]))
					currentByte += 2
				# Two byte data
				elif data[currentByte] == self.EVEMarshalOpCodes['short']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+3]))
					currentByte += 3
				# 4 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['long']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+5]))
					currentByte += 5
				# 8 byte
				elif data[currentByte] == self.EVEMarshalOpCodes['longlong'] or data[currentByte] == self.EVEMarshalOpCodes['double']:
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+9]))
					currentByte += 9

				elif data[currentByte] == self.EVEMarshalOpCodes['longstring']:
					stringData = bytearray()
					for x in range(currentByte + 2, currentByte + data[currentByte + 1] + 2):
						stringData += pack('B', data[x])
					unmarshaledList.append(stringData.decode("utf-8"))
					currentByte += len(stringData) + 2

				elif data[currentByte] == self.EVEMarshalOpCodes['tuple']:
					logging.error("Unmarhsaling tuple within tuple is not supported yet")

				elif data[currentByte] == self.EVEMarshalOpCodes['dict']:
					size = self.getMarshaledContainerSize(data[currentByte:])
					unmarshaledList.append(self.unmarshal(data[currentByte:currentByte+size+1]))


				element += 1
			
			return tuple(unmarshaledList)
		else:
			logging.error("Unknown marshal opcode: %s", data[0])

	def getMarshaledContainerSize(self, data):
		if data[0] == self.EVEMarshalOpCodes['tuple'] or data[0] == self.EVEMarshalOpCodes['dict']:
			numElements = data[1]
			tupleSize = 2
			currentElement = 0

			if (data[0] == self.EVEMarshalOpCodes['dict']):
				numElements *= 2

			while currentElement < numElements:
				if data[tupleSize] == self.EVEMarshalOpCodes['none'] or data[tupleSize] == self.EVEMarshalOpCodes['minusone'] or data[tupleSize] == self.EVEMarshalOpCodes['zero'] or data[tupleSize] == self.EVEMarshalOpCodes['one'] or data[tupleSize] == self.EVEMarshalOpCodes['zerodouble']:
					tupleSize += 1
				elif data[tupleSize] == self.EVEMarshalOpCodes['byte']:
					tupleSize += 2
				elif data[tupleSize] == self.EVEMarshalOpCodes['short']:
					tupleSize += 3
				elif data[tupleSize] == self.EVEMarshalOpCodes['long']:
					tupleSize += 5
				elif data[tupleSize] == self.EVEMarshalOpCodes['longlong'] or data[tupleSize] == self.EVEMarshalOpCodes['double']:
					tupleSize += 9
				elif data[tupleSize] == self.EVEMarshalOpCodes['longstring'] or data[tupleSize] == self.EVEMarshalOpCodes['utf8string']:
					tupleSize += data[tupleSize + 1] + 2
				else:
					logging.error("Unknown container opcode %s", data[tupleSize])

				currentElement += 1

			return tupleSize
		else:
			logging.error("Cannot get size of tuple with opcode ", data[0])
