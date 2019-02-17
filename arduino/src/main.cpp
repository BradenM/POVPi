#define BLYNK_PRINT Serial
#define BLYNK_MAX_READBYTES 2048

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// Software Serial
SoftwareSerial ESPSerial(2, 3); // RX, TX

// Blink Timers
BlynkTimer shadowTimer;
BlynkTimer formulaTimer;

// Network Connection
char ssid[] = "RPIAP";
char pass[] = "raspberrypi";

// Blynk Settings
const int blynkPort = 8080;
char auth[] = "4b999209771a4321b80dd0633dc0f2b1";

// Server
char webServer[] = "192.168.4.1";
const int webPort = 5000;

// Device State
char* currentDisplay = "hello";
bool isPowered = false;

// Get Formula
void getFormula(){
  Blynk.virtualWrite(V7, currentDisplay);
}

// Update Device State
void updateShadow(const char* newDisplay, bool newPower){
  if(strcmp(currentDisplay, newDisplay) != 0){
    char* display = const_cast<char*>(newDisplay);
    strcpy(currentDisplay, display);
    Blynk.virtualWrite(V1, currentDisplay);
    formulaTimer.setTimeout(5000L, getFormula);
    Serial.print("New Display: ");
    Serial.println(currentDisplay);
  }
  if(isPowered != newPower){
    isPowered = newPower;
    Blynk.virtualWrite(V5, isPowered);
    Serial.print("Power: ");
    Serial.println(isPowered);
  }
}

// Webhook GET
BLYNK_WRITE(V0){
  // JSON Buffer
  const size_t capacity = JSON_OBJECT_SIZE(3) + 50;
  DynamicJsonBuffer jsonBuffer(capacity);

  // Parse Message
  JsonObject& msg = jsonBuffer.parse(param.asStr());
  if(!msg.success()){
    return;
  }
  const char* display = msg["display"];
  bool enabled = msg["enabled"];
  updateShadow(display, enabled);
}

// Update Display from App
BLYNK_WRITE(V2){
  Serial.print("Incoming Data: ");
  Serial.println(param.asStr());
  Blynk.virtualWrite(V3, param.asStr());
}

// Update Pwr from App
BLYNK_WRITE(V5){
  Serial.print("Incoming Data: ");
  Serial.println(param.asStr());
  Blynk.virtualWrite(V6, isPowered);
}

// Parse Generated Formula from Server
BLYNK_WRITE(V7){
  Serial.println("Retrieving Formula...");
  // JSON Buffer
  const size_t capacity = 5*JSON_ARRAY_SIZE(4) + 16*JSON_ARRAY_SIZE(8) + JSON_OBJECT_SIZE(2) + 310;
  DynamicJsonBuffer jsonBuffer(capacity);

  // Parse
  JsonObject& msg = jsonBuffer.parse(param.asStr());
  if(!msg.success()){
    Serial.println("Formula Parsing Failed");
    return;
  }
  JsonArray& formula = msg["formula"];
  formula.prettyPrintTo(Serial);

}

// Retrieve Shadow from AWS 
void getShadow(){
  Blynk.virtualWrite(V0, 1);
}

void setup()
{
  // Debug console
  Serial.begin(9600);

  Blynk.begin(auth, ssid, pass, webServer, blynkPort);

  while(!Blynk.connected());
  Serial.println("Blynk Ready");
  shadowTimer.setInterval(7000L, getShadow);
}

void loop()
{
  Blynk.run();
  shadowTimer.run();
  formulaTimer.run();
}
