/*
  This code is made from "Serial Call and Response" written by Tom Igoe - 
  sourced from arduino library. The code establish a handshake with the 
  python listener on PC, and sends a Potentiometer resistance, as well as 
  a generated sine wave to the PC via serial connection.
  http://www.arduino.cc/en/Tutorial/SerialCallResponse
*/

int inByte = 0;         // incoming serial byte
float Vin = 5;    // POT circuit voltage
float R2 = 10000; // Resistance of other resistor
float V1;         // POT voltage
float R1;         // POT resistance
float sig2;       // Second signal


void setup() {
  // start serial port at 9600 bps:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  pinMode(2, INPUT);   // digital sensor is on digital pin 2
  pinMode(5, INPUT);   // Analog 5 read POT voltage
  establishContact();  // send a byte to establish contact until receiver responds
  Serial.flush();
  Serial.println("Contact established");
}

void loop() {
  // if we get a valid byte, read analog ins:
  if (Serial.available() > 0) {
    inByte = Serial.read();  // get incoming byte:
    if(inByte == 'B'){
      Serial.flush();
      V1 = float(analogRead(5))/float(1024)*Vin;
      R1 = V1/(Vin-V1) * R2;

      sig2 = sin(0.1*millis());
      Serial.print("R1 = ");
      Serial.print(R1);
      Serial.print(" Signal2 = ");
      Serial.println(sig2);
    }
  }
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}
