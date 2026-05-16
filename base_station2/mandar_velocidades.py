import tkinter as tk
import serial
import time

# ----- Configuraciones -----
SERIAL_PORT = 'COM10'  # Acuérdate de cambiarlo si estás en Linux
BAUD_RATE = 115200
NUM_ROBOTS = 5 

# Multiplicador para convertir floats a enteros y no romper la base ESP32
FACTOR_CONVERSION = 1000 
# --------------------------------

# Iniciar comunicación serial
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)  
    print(f'Conectado en {SERIAL_PORT}')
except Exception as e:
    print(f'Error de conexión: {e}')
    arduino = None

def enviar_datos_continuamente():
    valores_envio = []
    
    for i in range(NUM_ROBOTS):
        try:
            vel_izq = int(float(entradas_izq[i].get()) * FACTOR_CONVERSION)
        except ValueError:
            vel_izq = 0 
            
        try:
            vel_der = int(float(entradas_der[i].get()) * FACTOR_CONVERSION)
        except ValueError:
            vel_der = 0
            
        valores_envio.extend([vel_izq, vel_der])
        
    mensaje = ','.join(map(str, valores_envio)) + '\n'
    
    if arduino:
        arduino.write(mensaje.encode())
        
        # --- LO NUEVO: LEER LO QUE RESPONDE LA BASE ---
        while arduino.in_waiting > 0:
            try:
                # Lee la linea, la decodifica y le quita espacios
                respuesta = arduino.readline().decode('utf-8').strip()
                if respuesta:
                    print(f"\n[BASE ESP32]: {respuesta}")
            except Exception:
                pass
        # ----------------------------------------------
    
    print(f"Enviado a base: {mensaje.strip()}          ", end='\r')
    root.after(15, enviar_datos_continuamente)

def parar_todo():
    for i in range(NUM_ROBOTS):
        entradas_izq[i].delete(0, tk.END)
        entradas_izq[i].insert(0, "0.0")
        entradas_der[i].delete(0, tk.END)
        entradas_der[i].insert(0, "0.0")

def al_cerrar():
    print("\nCerrando programa y apagando motores...")
    if arduino:
        ceros = "0," * (NUM_ROBOTS * 2 - 1) + "0\n"
        arduino.write(ceros.encode())
        time.sleep(0.1)
        arduino.close()
    root.destroy()

# ----- Armado de la Interfaz -----
root = tk.Tk()
root.title("Control Velocidad (m/s)")
root.geometry("450x300")
root.protocol("WM_DELETE_WINDOW", al_cerrar) 

tk.Label(root, text="Velocidades (m/s) - Motores N20", font=("Arial", 14, "bold")).pack(pady=10)

entradas_izq = []
entradas_der = []

for i in range(NUM_ROBOTS):
    frame = tk.Frame(root)
    frame.pack(pady=2)
    
    tk.Label(frame, text=f"Robot {i+1} | M. Izq:").pack(side=tk.LEFT)
    e_izq = tk.Entry(frame, width=6)
    e_izq.insert(0, "0.0") 
    e_izq.pack(side=tk.LEFT, padx=5)
    entradas_izq.append(e_izq)
    
    tk.Label(frame, text="M. Der:").pack(side=tk.LEFT)
    e_der = tk.Entry(frame, width=6)
    e_der.insert(0, "0.0") 
    e_der.pack(side=tk.LEFT, padx=5)
    entradas_der.append(e_der)

tk.Button(root, text="FRENAR TODO (0.0)", bg="red", fg="white", font=("Arial", 10, "bold"), command=parar_todo).pack(pady=15)

root.after(1000, enviar_datos_continuamente)
root.mainloop()