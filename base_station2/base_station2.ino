#include <esp_now.h>
#include <WiFi.h>

// VARIABLES
#define NUM_ROBOTS 5

// Direccion de broadcast
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// Estructura actualizada a int16_t (2 bytes por variable)
typedef struct struct_mensaje {
    int16_t x_robot_1;
    int16_t y_robot_1;
    int16_t x_robot_2;
    int16_t y_robot_2;
    int16_t x_robot_3;
    int16_t y_robot_3;
    int16_t x_robot_4;
    int16_t y_robot_4;
    int16_t x_robot_5;
    int16_t y_robot_5;
} struct_mensaje;

struct_mensaje mimensaje;
esp_now_peer_info_t peerInfo;

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  // Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Envío OK" : "Error de Envío");
}

void setup() {
  Serial.begin(115200); 
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error inicializando ESP-NOW");
    return;
  }
  
  esp_now_register_send_cb(OnDataSent);

  // Configurar el Peer de Broadcast
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Fallo al agregar el peer");
    return;
  }
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    // Variables temporales para sscanf
    int x1, y1, x2, y2, x3, y3, x4, y4, x5, y5;
    
    // Escaneamos 10 enteros desde el puerto serie
    int leidos = sscanf(data.c_str(), "%d,%d,%d,%d,%d,%d,%d,%d,%d,%d",
                        &x1, &y1, &x2, &y2, &x3, &y3, &x4, &y4, &x5, &y5);

    if (leidos == 10) {
      // Asignamos a la estructura con cast a int16_t
      mimensaje.x_robot_1 = (int16_t)x1;
      mimensaje.y_robot_1 = (int16_t)y1;
      mimensaje.x_robot_2 = (int16_t)x2;
      mimensaje.y_robot_2 = (int16_t)y2;
      mimensaje.x_robot_3 = (int16_t)x3;
      mimensaje.y_robot_3 = (int16_t)y3;
      mimensaje.x_robot_4 = (int16_t)x4;
      mimensaje.y_robot_4 = (int16_t)y4;
      mimensaje.x_robot_5 = (int16_t)x5;
      mimensaje.y_robot_5 = (int16_t)y5;
    
      Serial.print("Base leyo bien -> M1_Izq: ");
      Serial.print(mimensaje.x_robot_1);
      Serial.print(" | M1_Der: ");
      Serial.println(mimensaje.y_robot_1);
      // Enviamos el paquete completo
      esp_now_send(broadcastAddress, (uint8_t *) &mimensaje, sizeof(mimensaje));
    } else{
      Serial.println("No se leyeron 10 valores");
    }
  }
}