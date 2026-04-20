#include <esp_now.h>
#include <WiFi.h>

//VARIABLES
#define NUM_ROBOTS 5

// Direccion de broadcast
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};  //direccion mac de la basestation: 08:D1:F9:F9:62:54

// Estructura del dato a enviar (Igual que antes)
typedef struct struct_mensaje{
    int8_t x_robot_1;
    int8_t y_robot_1;

    int8_t x_robot_2;
    int8_t y_robot_2;

    int8_t x_robot_3;
    int8_t y_robot_3;

    int8_t x_robot_4;
    int8_t y_robot_4;

    int8_t x_robot_5;
    int8_t y_robot_5;
} struct_mensaje;

struct_mensaje mimensaje;
esp_now_peer_info_t peerInfo;

//recibidos por el robotito:
typedef struct struct_telemetria{
  int id;
  float accelx;
  float accely;
  float anguloz;
  float velocidad_lineal;
} struct_telemetria;

struct_telemetria datosRobots;



void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status){
  // Opcional: Descomentar para debug, pero ensucia el monitor si mandas muy rapido
  // Serial.print("\r\nEstado: ");
  // Serial.println(status == ESP_NOW_SEND_SUCCESS ? "OK" : "Error");
}

void OnDataRecv(const esp_now_recv_info *info, const uint8_t *incomingData, int len){
  memcpy(&datosRobots, incomingData, sizeof(datosRobots));
  Serial.print("ID: ");
  Serial.print(datosRobots.id);
  Serial.print(" Velocidad: ");
  Serial.print(datosRobots.velocidad_lineal);
  Serial.print(" Aceleracion en x: ");
  Serial.print(datosRobots.accelx);
  Serial.print(" Aceleracion en y: ");
  Serial.print(datosRobots.accely);
  Serial.print(" Angulo: ");
  Serial.println(datosRobots.anguloz);
}

void setup() {
  Serial.begin(115200); 
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error inicializando ESP-NOW");
    return;
  }
  
  // Registrar Callback de envio
  esp_now_register_send_cb(OnDataSent);

  esp_now_register_recv_cb(OnDataRecv);

  // Registrar Peer (Broadcast)
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Fallo al agregar el peer de Broadcast");
    return;
  }
}

void loop() {
  if(Serial.available() > 0){
    String data = Serial.readStringUntil('\n');
    
    int x1, y1, x2, y2, x3, y3, x4, y4, x5, y5;

    int leidos = sscanf(data.c_str(), "%d,%d,%d,%d,%d,%d,%d,%d,%d,%d",
                        &x1, &y1, &x2, &y2, &x3, &y3, &x4, &y4, &x5, &y5);
    if (leidos == 10) {
        mimensaje.x_robot_1 = (int8_t)x1;
        mimensaje.y_robot_1 = (int8_t)y1;
        mimensaje.x_robot_2 = (int8_t)x2;
        mimensaje.y_robot_2 = (int8_t)y2;
        mimensaje.x_robot_3 = (int8_t)x3;
        mimensaje.y_robot_3 = (int8_t)y3;
        mimensaje.x_robot_4 = (int8_t)x4;
        mimensaje.y_robot_4 = (int8_t)y4;
        mimensaje.x_robot_5 = (int8_t)x5;
        mimensaje.y_robot_5 = (int8_t)y5;
        esp_now_send(broadcastAddress, (uint8_t *) &mimensaje, sizeof(mimensaje));
      }
  }
}