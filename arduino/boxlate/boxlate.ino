#include <LiquidCrystal.h>
#include <SPI.h>
#include <Ethernet.h>
#include <EthernetClient.h>
#include <aJSON.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 6, 5, 4, 7, 2);

byte mac[] = {0x90, 0xA2, 0xDA, 0x00, 0x44, 0xD2};
byte ip[] = {10, 30, 163, 53 }; 
byte ddns[] = {10,30,255,255}; 
byte gateway[] = {10,30,254,254};
byte server[] = {10,30,161,44};

unsigned long lastConnectionTime = 0;
boolean lastConnected = false; 
const unsigned long postingInterval = 15*1000; 

aJsonObject* time;
aJsonObject* arret;
aJsonObject* color;
aJsonObject* direc;
aJsonObject* jsonObject;
char charBuf[230];
char c;
    
EthernetClient client;


char inString[320]; // string for incoming serial dataping 
int stringPos = 0; // string index counter
boolean startRead = false; // is reading?
boolean haveData = false;
boolean change = false;

String jsonString = " ";

void setup() {
  pinMode(9, OUTPUT); // Red
  pinMode(3, OUTPUT); // Green
  Serial.begin(9600);
  lcd.begin(16, 2); // initialize lcd 
  Serial.println("HELLOOO...");
  Ethernet.begin(mac, ip,ddns,gateway); // initialize ethernet 
  delay(2000);
  httpRequest();
}

void loop() {
  
  if(client.available()){
      Serial.println("available...");
      startRead = false;
      jsonString = " ";
      haveData = true;
      while (client.available()){
        c = client.read();      
        if( c == '{' ) { startRead = true; }
        if ( startRead ) { jsonString += c; }
      }
      Serial.println(jsonString);
      jsonString.toCharArray(charBuf, 230);
      jsonObject = aJson.parse(charBuf);
      arret = aJson.getObjectItem(jsonObject, "stop");
      if(change){
        change = false;
        time = aJson.getObjectItem(jsonObject, "time1");
        color = aJson.getObjectItem(jsonObject, "color1");
        direc = aJson.getObjectItem(jsonObject, "destination1");
      }else{
        change=true;
        time = aJson.getObjectItem(jsonObject, "time2");
        color = aJson.getObjectItem(jsonObject, "color2");
        direc = aJson.getObjectItem(jsonObject, "destination2");
      }
      lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(arret->valuestring);
    
    lcd.setCursor(11, 0);
    lcd.print(time->valuestring);
    lcd.setCursor(0,1);
    lcd.print(direc->valuestring);
    switch (color->valueint) {
      case 1: // cas vert
        analogWrite(9, 0);
        analogWrite(3, 50);
        break;
      case 2: // cas orange
        analogWrite(9, 90);
        analogWrite(3, 20);
        break;
      case 3: // cas rouge
        analogWrite(9, 90);
        analogWrite(3, 0);
        break;
      default: // Requete erronée
        analogWrite(9, 0);
        analogWrite(3, 0);
    }
  }
        
         
  if (!client.connected() && lastConnected) {
    Serial.println("disconnecting.");
    client.stop();
  }

  if(!client.connected() && (millis() - lastConnectionTime > postingInterval)) {
    haveData = false;
    httpRequest();
  }

  lastConnected = client.connected();

}

void httpRequest() {
  Serial.println("connecting...");
  if (client.connect(server, 3000)) {
    Serial.println("connecting...");
    client.println("GET /getJSON HTTP/1.0");
    client.println("User-Agent: arduino-ethernet");
    client.println("Connection: close");
    client.println();
    lastConnectionTime = millis();
  } 
  else {
    client.stop();
  }
}
