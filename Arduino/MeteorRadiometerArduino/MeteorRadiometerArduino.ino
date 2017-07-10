
#include <AD770X.h>

// Init the ADC. The value in parenthesis is the scaler - because the ADC is
// 16-bit, we want the max. value to be 2^16
AD770X ad7705(65536);

// Define constants
const int irisRelayOut = 8;

//// Define variables
int irisCommand;

// Response wait timeout
int iris_timeout = 500; //us

int enableTimer = 0;
long sps_previous_micros = 0;

unsigned int ADCValue;
byte b1, b2;




// Starts recording and turns on the iris connected to the iris port
void irisOn(){

  // Used for opening the iris
  digitalWrite(irisRelayOut, HIGH);

  Serial.println("Response");

  // Allow some to for Iris to open before starting to record
  delay(200);

  enableTimer = 1;

}


// End recording and closes the iris connected to the iris port
void irisOff()
{

    // Used for closing the iris
    digitalWrite(irisRelayOut, LOW);

    enableTimer = 0;

    delay(10);

    Serial.println("Response");
  
}



// Waits for commands from PC and starts/ends recording
void checkIris()
{
    long previousMicros = 0;
    
    previousMicros = micros();
    while((micros() - previousMicros) < iris_timeout)
    {
        if(Serial.available() > 0)
        {
            // Look for the next valid integer in the incoming serial stream
            irisCommand = Serial.read();
            
            // If '1' is received, start recording
            if (irisCommand == '1') 
                irisOn();
            
            // If '0' is received, end recording
            else if (irisCommand == '0') 
                irisOff();

        }
    }
}

void setup()
{
    ad7705.reset();

    // Init the fist ADC input. The second one is not used.
    ad7705.init(AD770X::CHN_AIN1);  
  
    Serial.begin(115200);
}


void loop()
{
    if(enableTimer){

      // Read value from ADC
      ADCValue = ad7705.readADResult(AD770X::CHN_AIN1);
      
      // Convert data to 2 bytes for sending
      b1 = ADCValue&0xFF;
      b2 = ( ADCValue >> 8 )& 0xFF;
      
      // Send data
      Serial.write(b1);
      Serial.write(b2);

      // Serial.println(ADCValue);
      }
    
    // Check for flags from the PC    
    checkIris();
  
}
