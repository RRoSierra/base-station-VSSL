import pygame
import serial
import time

#-----Configurations-----
SERIAL_PORT = 'COM6'  # O 'COM6' si estás en Windows, ajusta según necesites en tu Arch/Linux
BAUD_RATE = 115200
NUM_ROBOTS = 5 # Numero de robots a controlar modificar si se agragan mas robots
#--------------------------------

# Iniciar pygame
pygame.init()
pygame.joystick.init()

num_mandos = pygame.joystick.get_count()
if num_mandos == 0:
    print("No se encontro ningun joystick.")
    exit()
print(f"Numero de joysticks conectados: {num_mandos}")

mandos = []
# Mapeo inicial: cada control empieza manejando al robot de su mismo índice (o al 0 si faltan)
robot_asignado = [] 

for i in range(num_mandos):
    j = pygame.joystick.Joystick(i)
    j.init()
    mandos.append(j)
    robot_inicial = i % NUM_ROBOTS
    robot_asignado.append(robot_inicial)
    print(f"Control {i}: {j.get_name()} -> Asignado a robot {robot_inicial + 1}")

# Iniciar comunicacion serial
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)  # Esperar a que la conexion se establezca
    print(f'Conectado a la base en {SERIAL_PORT} a {BAUD_RATE} baudios.')
except:
    print(f'No se pudo conectar al puerto serial {SERIAL_PORT}.')
    exit()

print(f"Iniciando control de robots. Controlando {num_mandos} a la vez. Presiona Ctrl+C para salir.")
print("Tip: Usa los botones 4 y 5 (usualmente LB/RB o L1/R1) para cambiar de robot.")

# Main loop
try:
    while True:
        # Procesar eventos (esto reemplaza a pygame.event.pump() para detectar botones)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.JOYBUTTONDOWN:
                joystick_id = event.joy
                button_id = event.button
                
                # Cambiar de robot hacia abajo (Boton 4, ej: LB)
                if button_id == 4:
                    robot_asignado[joystick_id] = (robot_asignado[joystick_id] - 1) % NUM_ROBOTS
                    print(f"Control {joystick_id} ahora maneja al Robot {robot_asignado[joystick_id] + 1}")
                
                # Cambiar de robot hacia arriba (Boton 5, ej: RB)
                elif button_id == 5:
                    robot_asignado[joystick_id] = (robot_asignado[joystick_id] + 1) % NUM_ROBOTS
                    print(f"Control {joystick_id} ahora maneja al Robot {robot_asignado[joystick_id] + 1}")

        # Preparar el array de envío (todos en 0 por defecto)
        valores_envio = [0] * NUM_ROBOTS * 2
        
        for i, joystick in enumerate(mandos):
            x_axis = joystick.get_axis(0)  # Eje X
            y_axis = joystick.get_axis(1)  # Eje Y
            
            # Normalizar valores a rango -100 a 100
            x_val = int(x_axis * 100)
            y_val = int(y_axis * -100)

            # Zona muerta
            if abs(x_val) < 10: x_val = 0
            if abs(y_val) < 10: y_val = 0

            # Obtener a qué robot está apuntando este control actualmente
            target_robot = robot_asignado[i]

            # Inyectar las velocidades en la posición correcta del payload
            # Si dos controles apuntan al mismo robot, el mando con mayor índice sobreescribe al anterior
            valores_envio[target_robot * 2] = x_val
            valores_envio[(target_robot * 2) + 1] = y_val

        # Armar y enviar el mensaje
        mensaje = ','.join(map(str, valores_envio)) + '\n'
        arduino.write(mensaje.encode())
        
        # Opcional: limpiar la línea para que el print no haga spam hacia abajo
        print(f'Enviado: {mensaje.strip()} | Mapeo: {robot_asignado}', end='          \r')

        time.sleep(0.015)

except KeyboardInterrupt:
    print("\nSaliendo...")
    if 'arduino' in locals() and arduino.is_open:
        # Mandar un último mensaje de freno a todos los robots
        freno = ','.join(['0'] * (NUM_ROBOTS * 2)) + '\n'
        arduino.write(freno.encode())
        arduino.close()
    pygame.quit()