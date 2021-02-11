    #Below are all methods to write to Arduino. Each are different based on GUI input
    def writePID(self,P,I,D):
        values = f"S0,P{P},I{I},D{D},\0"
        self.ser.write(str.encode(values))
        print("S0:", values)
    #S1
    def writeSetpoint(self,Setpoint):
        values = f"S1,Z{Setpoint},\0"
        self.ser.write(str.encode(values))
        print("S1:", values)
    #S2
    def writeLabType(self,LabType):
        values = f"S2,Y{LabType},\0"
        self.ser.write(str.encode(values))
        print("S2:", values)
    #S3
    def writeController(self,Controller):
        values = f"S3,M{Controller},\0"
        self.ser.write(str.encode(values))
        print("S3:", values)
    #S4
    def writeSampleTime(self,SampleTime):
        values = f"S4,T{SampleTime},\0"
        self.ser.write(str.encode(values))
        print("S4:", values)
    #S5
    def writeSaturation(self,Saturation):
        Saturation = [item for item in Saturation.split(",") if item != ""]
        values = f"S5,L{Saturation[0]},U{Saturation[1]},\0"
        self.ser.write(str.encode(values))
        print("S5:", values)
        
        """
        if len(Saturation) != 2:
            raise ValueError("Saturation field is not inputted properly! Make sure it is a comma separated pair!")
        elif Saturation[0] >= Saturation[1]:
            raise ValueError("Second value should always be GREATER than the first")
        else:
            values = f"S5,L{Saturation[0]},U{Saturation[1]},\0"
            self.ser.write(str.encode(values))
            print("S5:", values)
        """     
    #S6
    def writeOLPWM(self,OLPWM):
        if OLPWM != None:
            values = f"S6,O{OLPWM},\0"
            self.ser.write(str.encode(values))
            print("S6:", values)
    #S7 A is coefficient to x^2, B is coefficient to x, C is coefficient to x^0 (constant)
    def writeFF(self,FF):
        if FF != None:
            FF = [item for item in FF.split(",") if item != ""]
            values = f"S7,A{FF[0]},B{FF[1]},C{FF[2]},\0"
            self.ser.write(str.encode(values))
            print("S7:", values)
            """
            if len(FF) != 3:
                raise ValueError("Feedforward field is not inputted properly! Make sure it is a comma separated triple!")
            else:
                values = f"S7,A{FF[0]},B{FF[1]},C{FF[2]},\0"
                self.ser.write(str.encode(values))
                print("S7:", values)                
            """
    #S8 T is binary (1 is activated, 0 is not)
    def writeOLCharacterization(self):
        values = f"S8,T1,\0"
        self.ser.write(str.encode(values))
        print("S8:", values)
    
    #S10 W is binary (1 is activated, 0 is not)
    def writeAntiWindup(self,AntiWindup):
        values = f"S10,W{AntiWindup},\0"
        self.ser.write(str.encode(values))
        print("S10:", values)
