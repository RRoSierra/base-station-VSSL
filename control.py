import pygame
import serial
import time

#-----Configurations-----
SERIAL_PORT = 'COM6'  # Change as needed
#Puede que no se tengan los permisos necesarios en linux para acceder al puerto serial en linux
#usar: sudo usermod -a -G dialout $USER para ubuntu/debian
#usar: sudo usermod -a -G uucp $USER para archlinux/manjaro
BAUD_RATE = 115200
NUM_ROBOTS = 5 # Numero de robots a controlar modificar si se agregan mas robots
#--------------------------------

#iniciar pygame
pygame.init()
pygame.joystick.init()

num_mandos = pygame.joystick.get_count()
if num_mandos == 0:
    print("No se encontro ningun joystick.")
    exit()
print(f"Numero de joysticks conectados: {num_mandos}")

mandos = []
for i in range(num_mandos):
    j = pygame.joystick.Joystick(i)
    j.init()
    mandos.append(j)
    print(f"control {i}: {j.get_name()} -> Asignado a robot {i+1}")
    


#iniciar comunicacion serial
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)  # Esperar a que la conexion se establezca
    print(f'Conectado a Arduino en {SERIAL_PORT} a {BAUD_RATE} baudios.')
except:
    print(f'No se pudo conectar al puerto serial {SERIAL_PORT}.')
    exit()

print("Iniciando control de robots. Controlando {num_mandos}a la vez. Presiona Ctrl+C para salir.")
#main loop
try:
    while True:
        pygame.event.pump()
        valores_envio = [0] * NUM_ROBOTS * 2  # [robot1_x, robot1_y, robot2_x, robot2_y, ...]
        for i, joystick in enumerate(mandos):
            if i >= NUM_ROBOTS:
                break  # No mas robots que controlar
            x_axis = joystick.get_axis(0)  # Eje X
            y_axis = joystick.get_axis(1)  # Eje Y
            # Normalizar valores a rango -100 a 100
            x_val = int(x_axis * 100)
            y_val = int(y_axis * -100)

            if abs(x_val) < 10:
                x_val = 0
            if abs(y_val) < 10:
                y_val = 0

            valores_envio[i*2] = x_val
            valores_envio[(i*2) + 1] = y_val
        mensaje = ','.join(map(str, valores_envio)) + '\n'
        arduino.write(mensaje.encode())
        print(f'Enviado: {mensaje.strip()}', end='\r')

        time.sleep(0.015)

except KeyboardInterrupt:
    print("\nSaliendo...")
    arduino.close()
    pygame.quit()
