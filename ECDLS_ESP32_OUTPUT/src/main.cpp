#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char *ssid = "EKI-6333AC-2G-2.4G";
const char *password = "t5njce747!";

// MQTT broker setup
const char *mqtt_server = "192.168.131.114";
const int mqtt_port = 1883;                 // Change if your MQTT broker uses a different port
const char *mqtt_username = "admin";        // If your broker requires authentication
const char *mqtt_password = "t5njce747";    // If your broker requires authentication
const char *mqtt_client_id = "ESP32Output"; // MQTT client ID

int GREEN_LED = 16;
int RED_LED = 17;
int DO1 = 12;
int DO2 = 13;
int DO3 = 14;
int DO4 = 25;
int DO5 = 26;
int DO6 = 27;
int DO7 = 32;
int DO8 = 33;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi()
{
  Serial.println("\nConnecting to Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);
  Serial.println("\nWiFi connected");
  Serial.println("IP address: " + WiFi.localIP().toString());
}

void reconnect_wifi()
{
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi connection lost. Reconnecting...");
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);
    setup_wifi();
  }
}

void doHandler(char payload, int outputPin)
{
  if (payload == '1')
  {
    digitalWrite(outputPin, LOW);
    Serial.print("TRUN ON --> ");
    Serial.println(outputPin);
  }
  else
  {
    digitalWrite(outputPin, HIGH);
    Serial.print("TRUN OFF --> ");
    Serial.println(outputPin);
  }
}

void mqtt_callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");
  for (int i = 0; i < length; i++)
  {
    switch (i)
    {
    case 0:
      doHandler((char)payload[i], DO1);
      break;
    case 1:
      doHandler((char)payload[i], DO2);
      break;
    case 2:
      doHandler((char)payload[i], DO3);
      break;
    case 3:
      doHandler((char)payload[i], DO4);
      break;
    case 4:
      doHandler((char)payload[i], DO5);
      break;
    case 5:
      doHandler((char)payload[i], DO6);
      break;
    case 6:
      doHandler((char)payload[i], DO7);
      break;
    case 7:
      doHandler((char)payload[i], DO8);
      break;
    default:
      break;
    }
  }
}

void reconnect_mqtt()
{
  while (!client.connected())
  {
    Serial.println("Attempting MQTT connection...");
    if (client.connect(mqtt_client_id, mqtt_username, mqtt_password))
    {
      Serial.println("Connected to MQTT broker");
      client.subscribe("/esp32/output");
    }
    else
    {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(". Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(115200);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  digitalWrite(RED_LED, HIGH);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
  pinMode(DO1, OUTPUT); // DO1
  pinMode(DO2, OUTPUT); // DO2
  pinMode(DO3, OUTPUT); // DO3
  pinMode(DO4, OUTPUT); // DO4
  pinMode(DO5, OUTPUT); // DO5
  pinMode(DO6, OUTPUT); // DO6
  pinMode(DO7, OUTPUT); // DO7
  pinMode(DO8, OUTPUT); // DO8
}

// void publish_data()
// {
//   static int value = 0;
//   char msg[50];
//   sprintf(msg, "Hello from ESP32: %d", value++);
//   client.publish("/esp32/test", msg);
// }

void subscribe()
{
  client.loop();
}

void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    reconnect_wifi();
  }
  if (!client.connected())
  {
    reconnect_mqtt();
  }
  subscribe(); // Subscribe and handle incoming messages
}
