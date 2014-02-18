MarshalHeaderByte   = 0x7E

Op_Tuple            = 0x14
Op_EmptyTuple       = 0x24
Op_OneTuple         = 0x25
Op_TwoTuple         = 0x2C


class Marshal:
    marshalledData = bytearray()
    unmarhsalledData = bytearray()

    def __init__(self):

    def PutMarshalled(self, d):
        dataLen = len(d)
        marhsalledIndex = len(self.marshalledData)

        marshalledData += bytearray(d)

    def PutUnmarshalled(self, d):
        unmarhsalledData += bytearray(d)

    def Marshal(self, d):
        PutMarshalled(MarshallHeaderByte)
        PutMarshalled(bytes([0, 0, 0, 0])

        if type(d) is tuple:
            MarshalTuple(d)

    def MarshalTuple(self, d):
        tupleLen = len(d)

        if tupleLen == 0:
            PutMarshalled(Op_EmptyTuple)
        elif tupleLen == 1:
            PutMarshalled(Op_OneTuple)
        elif tupleLen == 2:
            PutMarshalled(Op_TwoTuple)
        else:
            PutMarshalled(Op_Tuple)
            #TODO: Put tuple size

        PutMarshalled(d)
