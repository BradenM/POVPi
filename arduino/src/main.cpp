#include <Arduino.h>
#include <WiFiEsp.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// Init ESP Serial
SoftwareSerial ESPserial(2, 3);

// Init Client Object
WiFiEspClient client;

// Network Connection
char ssid[] = "RPIAP";
char pass[] = "raspberrypi";
int status = WL_IDLE_STATUS;

// Server
char webServer[] = "192.168.4.1";
const int webPort = 5000;

// JSON Buffer
const size_t capacity = JSON_OBJECT_SIZE(3) + 96;
DynamicJsonBuffer jsonBuffer(capacity);


// LED Pins
const int ledPins[] = {0, 1, 2, 3, 4, 5, 6, 7};
const int ledSize = sizeof(ledPins) / sizeof(ledPins[0]);

// Example Formula (Letter L - 8 Columns - 4 Rows )
int exampleFormula[4][8] = {
    {1, 1, 1, 1, 1, 1, 1, 1}, // STep 1
    {0, 0, 0, 0, 0, 0, 0, 1},
    {0, 0, 0, 0, 0, 0, 0, 1},
    {0, 0, 0, 0, 0, 0, 0, 1}  // Step 4
};

void getWifiStatus()
{
  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print your MAC address
  byte mac[6];
  WiFi.macAddress(mac);
  char buf[20];
  sprintf(buf, "%02X:%02X:%02X:%02X:%02X:%02X", mac[5], mac[4], mac[3], mac[2], mac[1], mac[0]);
  Serial.print("MAC address: ");
  Serial.println(buf);
}

// Connect to Flask Server and request shadow
void requestShadow() {
    Serial.println();
    Serial.print("Attempting to connect to web server @ ");
    Serial.println(webServer);
    if (client.connect(webServer, webPort)){
        Serial.println("Connected to Web Server");
        // Make a HTTP request
        Serial.println("Requesting device shadow...");
        client.println("GET /getshadow HTTP/1.1");
        client.print("Host: ");
        client.println(webServer);
        client.println("Connection: close");
        client.println();
    }
}

void setup(){

    // // Init LED Pins
    // for(int i=0; i <= ledSize; i++){
    //     pinMode(i, OUTPUT);
    // }

    // Start Serial
    Serial.begin(9600);
    ESPserial.begin(9600);

    // Init ESP
    WiFi.init(&ESPserial);
    client.setTimeout(10000);

    // attempt to connect to WiFi network
    while ( status != WL_CONNECTED) {
        Serial.print("Attempting to connect to WPA SSID: ");
        Serial.println(ssid);
        // Connect to WPA/WPA2 network
        status = WiFi.begin(ssid, pass);
    }

    // you're connected now, so print out the data
    Serial.println("Connected to the network");
    getWifiStatus();
    requestShadow();
}

void printCurrentNet()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to
  byte bssid[6];
  WiFi.BSSID(bssid);
  char buf[20];
  sprintf(buf, "%02X:%02X:%02X:%02X:%02X:%02X", bssid[5], bssid[4], bssid[3], bssid[2], bssid[1], bssid[0]);
  Serial.print("BSSID: ");
  Serial.println(buf);

  // print the received signal strength
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI): ");
  Serial.println(rssi);
}


void loop()
{
    char display;
    bool enabled;

    while(client.available()){
        JsonObject& root = jsonBuffer.parseObject(client);
        display = root["display"].as<char>();
        enabled = root["enabled"].as<bool>();
    }

    if(!client.connected()){
        Serial.println();
        Serial.print("[POVPi] DISPLAY: ");
        Serial.println(display);
        Serial.print("[POVPi] ENABLED: ");
        Serial.println(enabled);
        client.stop();
        while(true);
    }

  // check the network connection once every 10 seconds
//   Serial.println();
//   printCurrentNet();
//   getWifiStatus();
  
//   delay(10000);
}


// void loop(){
//     // Print Step By Step of Test Formula
//     for(int x=0; x<4; x++){
//         Serial.print("STEP ");
//         Serial.print(x);
//         Serial.print(": ");
//         for(int y=0; y<8; y++){
//             int ledState = exampleFormula[x][y];
//             int currentLed = ledPins[y];
//             // Write State (0 or 1, based on formula) to Current Led (y)
//             digitalWrite(currentLed, ledState);
//             Serial.print(exampleFormula[x][y]);
//             Serial.print(" ");
//             delay(150);
//         }
//         Serial.println(" ");
//     }
//     Serial.println(" ");

//     delay(10000);
// }