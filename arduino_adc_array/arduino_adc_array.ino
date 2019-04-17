#include <Wire.h>

int numSamples = 0;
/*
 * adcValues[0:9] are shunt resistor V+
 * adcValues[10:19] are shunt resistor V-
 * adcValues[20:29] are voltage
 */
volatile byte adcValues[30] = {0};
volatile byte adcIndex = 0;
volatile byte analogPin = 0; //0 == A0, 1 == A1, 2 == A2
volatile int avgVoltage = 0;
volatile int avgVoltagePlus = 0;
volatile int avgVoltageMinus = 0;
volatile int avgCurrent = 0;

/*
 * Use A0 for V+ measurement
 * Use A1 for V- measurement
 * Use A2 for current measurement
 */


void sendData(){
  ADCSRA &= ~(1 << ADIE); //Disable ADC interrupts
  avgVoltage = 0;
  for(int i = 0; i < 10; i++){
    avgVoltagePlus += adcValues[i];
    avgVoltageMinus += adcValues[i+10];
    avgCurrent += adcValues[i+20];
  }
  avgVoltage = (avgVoltagePlus/10) - (avgVoltageMinus/10);
  avgCurrent /= 10;
  Wire.write((byte) avgVoltage);
  Wire.write((byte) avgCurrent);
  avgVoltage = avgVoltagePlus = avgVoltageMinus = avgCurrent = 0;
  ADCSRA |= (1 << ADIE); //Re-enable ADC interrupts
}

void setup() {
  //Serial.begin(115200) //Debug

  ADCSRA = 0;             // clear ADCSRA register
  ADCSRB = 0;             // clear ADCSRB register
  ADMUX |= (analogPin & 0x07);    // set A0 analog input pin
  ADMUX |= (1 << REFS0);  // set reference voltage to Vcc
  ADMUX |= (1 << ADLAR);  // left align ADC value to 8 bits from ADCH register

  // sampling rate is [ADC clock] / [prescaler] / [conversion clock cycles]
  // for Arduino Uno ADC clock is 16 MHz and a conversion takes 13 clock cycles
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); //128 prescaler for 9.6 kHz
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS1);  //64 prescaler for 19.2 kHz
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS0);  //32 prescaler for 38.5 kHz
  //ADCSRA |= (1 << ADPS2);                 //16 prescaler for 76.9 kHz
  //ADCSRA |= (1 << ADPS1) | (1 << ADPS0);    // 8 prescaler for 153.8 kHz
  ADCSRA |= (1 << ADPS1);                 //4 prescaler for 307.7 kHz
  //ADCSRA |= (1 << ADS0);                  //2 prescaler for 615.4 kHz

  ADCSRA |= (1 << ADATE); // enable auto trigger
  ADCSRA |= (1 << ADIE);  // enable interrupts when measurement complete
  ADCSRA |= (1 << ADEN);  // enable ADC
  ADCSRA |= (1 << ADSC);  // start ADC measurements

  //DO NOT TOUCH 0x40 or 0x80, they're mapped to the crystal oscillator
  DDRB |= 0x20; //Set the LED to output (PB5)
  
  Wire.begin(0x04); //Slave address
  Wire.onRequest(sendData);
}

void loop() {
  delay(1000); //Don't do anything in loop, just sleep until interrupted

  /*//Debug stuff
  Serial.print("V+ values:\t");
  for(int i = 0; i < 10; i++){
    Serial.print(adcValues[i]);
    Serial.print(", ");
  }
  Serial.print("\n");

  Serial.print("V- values:\t");
  for(int i = 10; i < 20; i++){
    Serial.print(adcValues[i]);
    Serial.print(", ");
  }
  Serial.print("\n");

  Serial.print("Voltage values:\t");
  for(int i = 20; i < 30; i++){
    Serial.print(adcValues[i]);
    Serial.print(", ");
  }
  Serial.print("\n--------------------\n\n");
  */
  
}

ISR(ADC_vect){
  *(adcValues + 10*analogPin + adcIndex) = ADCH; //Read the top 8 bits of the ADC
  analogPin = (analogPin + 1)%3;
  ADMUX &= 0xF0 | (analogPin);
  adcIndex = (adcIndex + 1) % 10;

  //DO NOT TOUCH 0x40 or 0x80, they're mapped to the crystal oscillator
  PORTB ^= 0x20; //Toggle the LED for heartbeat (PB5)
}
