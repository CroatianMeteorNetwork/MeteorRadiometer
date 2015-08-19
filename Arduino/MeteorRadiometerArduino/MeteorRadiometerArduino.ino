#include <AD770X.h>

AD770X ad7706(0);
double result;


//// Define constants
const int irisRelayOut = 8;

//// Define variables
int irisCommand;
// Response wait timeout
int iris_timeout = 500; //us

int enableTimer = 0;
long sps_previous_micros = 0;

int ADCValue;
byte b1, b2;

void irisOff(){
  // Used for closing the iris
  digitalWrite(irisRelayOut, LOW);
  enableTimer = 0;
  delay(10);
  Serial.println("Response");
  
  }
  
void irisOn(){
  // Used for opening the iris
  digitalWrite(irisRelayOut, HIGH);
  Serial.println("Response");
  // Allow some to for Iris to open before starting to record
  delay(200);
  enableTimer = 1;
  }
  
void checkIris()
{
    long         previousMicros = 0;
    
    previousMicros = micros();
    while((micros()-previousMicros)<iris_timeout)
    {
        if(Serial.available()>0)
        {
            // look for the next valid integer in the incoming serial stream:
            irisCommand = Serial.read();
            
            if (irisCommand == '1') irisOn();
            else if (irisCommand == '0') irisOff();

        }
    }
}

void setup()
{
  

  ad7706.reset();
  ad7706.init(AD770X::CHN_AIN1);  
  //ad7706.init(AD770X::CHN_AIN2);
  
  Serial.begin(115200);
}

void loop()
{
    if(enableTimer){
      result = ad7706.readADResult(AD770X::CHN_AIN1);
      ADCValue = (int) result;
      
      // Convert data to 2 bytes for sending
      b1 = ADCValue&0xFF;
      b2 = ( ADCValue >> 8 )& 0xFF;
      
      // Send data
      Serial.write(b1);
      Serial.write(b2);
      }
    
    checkIris();

/*  Serial.println(v);
/*
  v = ad7706.readADResult(AD770X::CHN_AIN2);
  Serial.print(" : ");
  Serial.println(v);*/
}
