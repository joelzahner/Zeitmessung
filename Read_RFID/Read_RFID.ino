#include "SparkFun_UHF_RFID_Reader.h"

RFID rfidModule;

#include <SoftwareSerial.h>
SoftwareSerial softSerial(2, 3); //RX, TX


#define rfidSerial softSerial 

#define rfidBaud 38400

#define moduleType ThingMagic_M6E_NANO

void setup()
{
  Serial.begin(115200);
  while (!Serial); //Wait for the serial port to come online

  if (setupRfidModule(rfidBaud) == false)
  {
    Serial.println(F("Module failed to respond. Please check wiring."));
    while (1); //Freeze!
  }

  rfidModule.setRegion(REGION_EUROPE);

  rfidModule.setReadPower(2700); //27.00 dBm. Higher values may caues USB port to brown out
  //Max Read TX Power is 27.00 dBm and may cause temperature-limit throttling

  Serial.read(); //Throw away the user's character
  rfidModule.startReading(); //Begin scanning for tags
  //Serial.println(F("Program started"));
}

void loop()
{
  if (rfidModule.check() == true) //Check to see if any new data has come in from module
  {
    byte responseType = rfidModule.parseResponse(); //Break response into tag ID, RSSI, frequency, and timestamp

    if (responseType == RESPONSE_IS_KEEPALIVE)
    {
      //Serial.println(F("Scanning"));
    }
    else if (responseType == RESPONSE_IS_TAGFOUND)
    {
      byte tagEPCBytes = rfidModule.getTagEPCBytes();

      String tagID = "";
      for (byte x = 0 ; x < tagEPCBytes ; x++)
      {
        if (rfidModule.msg[31 + x] < 0x10) tagID += "0";
        tagID += String(rfidModule.msg[31 + x], HEX);
      }

      Serial.println(tagID); // RFID-ID als reine Zeichenkette (z.B. 300833B2DDD9014000000000)
    }


    else if (responseType == ERROR_CORRUPT_RESPONSE)
    {
      Serial.println("Bad CRC");
    }
    else if (responseType == RESPONSE_IS_HIGHRETURNLOSS)
    {
      Serial.println("High return loss, check antenna!");
    }
    else
    {
      //Unknown response
      Serial.println("Unknown error");
    }
  }
}

boolean setupRfidModule(long baudRate)
{
  rfidModule.begin(rfidSerial, moduleType); //Tell the library to communicate over serial port

  //Test to see if we are already connected to a module
  //This would be the case if the Arduino has been reprogrammed and the module has stayed powered
  rfidSerial.begin(baudRate); //For this test, assume module is already at our desired baud rate
  delay(100); //Wait for port to open

  //About 200ms from power on the module will send its firmware version at 115200. We need to ignore this.
  while (rfidSerial.available())
    rfidSerial.read();

  rfidModule.getVersion();

  if (rfidModule.msg[0] == ERROR_WRONG_OPCODE_RESPONSE)
  {
    //This happens if the baud rate is correct but the module is doing a ccontinuous read
    rfidModule.stopReading();

    //Serial.println(F("Module continuously reading. Asking it to stop..."));

    delay(500);
  }
  else
  {
    //The module did not respond so assume it's just been powered on and communicating at 115200bps
    rfidSerial.begin(115200); //Start serial at 115200

    rfidModule.setBaud(baudRate); //Tell the module to go to the chosen baud rate. Ignore the response msg

    rfidSerial.begin(baudRate); //Start the serial port, this time at user's chosen baud rate

    delay(250);
  }

  //Test the connection
  rfidModule.getVersion();
  if (rfidModule.msg[0] != ALL_GOOD)
    return false; //Something is not right

  //The module has these settings no matter what
  rfidModule.setTagProtocol(); //Set protocol to GEN2

  rfidModule.setAntennaPort(); //Set TX/RX antenna ports to 1

  return true; //We are ready to rock
}
