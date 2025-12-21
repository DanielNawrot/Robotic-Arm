#include <ESP8266WiFi.h>

const char *ssid = "XXX";
const char *password = "XXX";
WiFiServer server(1234);

const int servoPin = 13; // Use any PWM-capable pin
const int pwmChannel = 0;
const int pwmFreq = 50;       // Standard servo frequency: 50Hz
const int pwmResolution = 16; // 16-bit resolution (0-65535)

String inputStr;
char c;
char str[255];
uint8_t idx = 0;

void setServoAngle();

void setup()
{
  Serial.begin(115200);
  delay(10);
  Serial.setTimeout(1);
  Serial.println("Starting servo control...");

  Serial.println("Starting Wifi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }
  Serial.println("CONNECTED");
  server.begin();
  Serial.println(WiFi.localIP());
}

void setServoAngle(double angle)
{
  // Map angle (0-180) to duty cycle
  // Pulse width range for SG90: 500us (0°) to 2400us (180°)
  int minDuty = (65535 * 0.5) / 20; // 0.5ms / 20ms
  int maxDuty = (65535 * 2.4) / 20; // 2.4ms / 20ms

  int duty = map(angle, 0, 180, minDuty, maxDuty);

  analogWrite(pwmChannel, duty);
}

void loop()
{
  WiFiClient client = server.accept();
  if (client)
  {
    while (client.connected())
    {
      if (client.available())
      {
        String data = client.readStringUntil('\n');
        Serial.println("Data: " + data);

        data.trim();
        int p1 = data.indexOf('-');
        // int p2 = data.indexOf('-', p1 + 1);

        double elbow = data.substring(0, p1).toDouble();
        // double armVert = data.substring(p1 + 1, p2).toDouble();
        // double armHori = data.substring(p2 + 1).toDouble();
        setServoAngle(elbow);
      }
    }
    client.stop();
  }
  delay(50);
  /** if (Serial.available() > 0)
  {
    c = Serial.read();
    if (c != '\n')
    {
      str[idx++] = c;
    }
    else
    {
      str[idx] = '\0';
      idx = 0;
    }

    inputStr = str;
    inputStr.trim();
    Serial.println(inputStr);

    int p1 = inputStr.indexOf('-');
    int p2 = inputStr.indexOf('-', p1 + 1);

    double elbow = inputStr.substring(0, p1).toDouble();
    double armVert = inputStr.substring(p1 + 1, p2).toDouble();
    double armHori = inputStr.substring(p2 + 1).toDouble();

    setServoAngle(elbow);
    delay(0.2);
  }
    */
}