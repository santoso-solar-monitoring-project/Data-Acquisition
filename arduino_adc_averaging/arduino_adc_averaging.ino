#include <Wire.h>

int numSamples = 0;
/*
 * adcValues[0] is shunt resistor V+
 * adcValues[1] is shunt resistor V-
 * adcValues[2] is voltage
 */
volatile byte adcValues[3] = {0,0,0};
volatile uint32_t adcIndex = 0; //The number of samples taken so far
volatile byte analogPin = 2; //Either A0 or A1
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
  Wire.write((byte)(adcValues[0] - adcValues[1]));
  Wire.write((byte) adcValues[2]);
  *adcValues = *(adcValues+1) = *(adcValues+2) = 0;
  adcIndex = 0;
  ADCSRA |= (1 << ADIE); //Re-enable ADC interrupts
}

void setup() {
  Serial.begin(115200); //Debug

  //DO NOT TOUCH 0x40 or 0x80, they're mapped to the crystal oscillator
  DDRB |= 1 << DDB7; //Set the LED to output
  //8.7654.3210
  //0.0000.0000

  ADCSRA = 0;             // clear ADCSRA register
  ADCSRB = 0;             // clear ADCSRB register
  ADMUX |= (analogPin & 0x07);    // set A0 analog input pin
  ADMUX |= (1 << REFS0);  // set reference voltage to Vcc
  ADMUX |= (1 << ADLAR);  // left align ADC value to 8 bits from ADCH register
  delay(50); //Let the ADMUX stabilize

  // sampling rate is [ADC clock] / [prescaler] / [conversion clock cycles]
  // for Arduino Uno ADC clock is 16 MHz and a conversion takes 13 clock cycles
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); //128 prescaler for 9.6 kHz
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS1);  //64 prescaler for 19.2 kHz
  ADCSRA |= (1 << ADPS2) | (1 << ADPS0);  //32 prescaler for 38.5 kHz
  //ADCSRA |= (1 << ADPS2);                 //16 prescaler for 76.9 kHz
  //ADCSRA |= (1 << ADPS1) | (1 << ADPS0);    // 8 prescaler for 153.8 kHz
  //ADCSRA |= (1 << ADPS1);                 //4 prescaler for 307.7 kHz
  //ADCSRA |= (1 << ADPS0);                  //2 prescaler for 615.4 kHz

  ADCSRA |= (1 << ADATE); // enable auto trigger interrupt
  ADCSRA |= (1 << ADIE);  // enable interrupts when measurement complete
  ADCSRA |= (1 << ADEN);  // enable ADC
  ADCSRA |= (1 << ADSC);  // start ADC measurements

  Wire.begin(0x04); //Slave address
  Wire.onRequest(sendData);
}

void loop() {
  delay(1000); //Don't do anything in loop, just sleep until interrupted

  //Debug stuff
  Serial.print("V+ value:\t");
  Serial.println(adcValues[0]);
  Serial.print("V- value:\t");
  Serial.println(adcValues[1]);
  Serial.print("Voltage value:\t");
  Serial.println(adcValues[2]);
  Serial.println(adcIndex);
  Serial.println("-------------------------");
  *adcValues = *(adcValues+1) = *(adcValues+2) = 0;
  adcIndex = 0;
  
}

ISR(ADC_vect){
  *(adcValues + analogPin) = (adcValues[analogPin]*adcIndex + ADCH)/(adcIndex+1); //Read the top 8 bits of the ADC
  //*(adcValues + analogPin) = ADCH;
  //if(analogPin == 2) adcIndex++;
  adcIndex++;
  if(analogPin == 3) analogPin = 0;
  ADMUX = bit (REFS0) | (analogPin & 7);

  //DO NOT TOUCH 0x40 or 0x80, they're mapped to the crystal oscillator
  //PORTB ^= bit(PORTB7); //Toggle the LED for output
}
