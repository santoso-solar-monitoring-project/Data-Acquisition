#include <Wire.h>

#define SLAVE_ADDRESS 0x04

int data = 0;
int brightness = round(255*0.6);

void massDigitalWrite(int powerLevel){
  for (int i = 1; i <= powerLevel; i++){
    digitalWrite(i, HIGH);
  }
  for (int j = 5; j > powerLevel; j--){
    digitalWrite(j, LOW); 
  }
}

// callback for received data
void receiveData(int byteCount){

  while(Wire.available()) {
    data = Wire.read();
    Serial.print("data received: ");
    Serial.println(data);
    int led = data % 16;
    int pwm = (data-led)/16;
    // Inversion
    pwm = -(pwm - 1);
    brightness = max(55, min(255, brightness + pwm));

    Serial.print("Power Level: ");
    Serial.print(led);
    Serial.print("\tPWM: ");
    Serial.println(pwm);
    Serial.print("Brightness: ");
    Serial.println(brightness);
    
    analogWrite(6, brightness);
    massDigitalWrite(led);
  }
}

// callback for sending data
void sendData(){
  Wire.write(data);
}

void setup() {
  // Power Gauge LEDs
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);

 // Set pin 6 to run at 62.5 kHz
  byte mode = 0x01;
  TCCR0B = TCCR0B & 0b11111000 | mode;

  analogWrite(6, brightness);

  Serial.begin(9600); // start serial for output
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);
  
  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  
  Serial.println("Ready!");
}
  
void loop() {
  delay(100);
}
