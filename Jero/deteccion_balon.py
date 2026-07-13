import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

puntos_trayectoria = []

ultimo_tiempo = time.time()
ultimo_x, ultimo_y = None, None

archivo_datos = open("Jero/trayectoria.txt", "w")
archivo_datos.write("X, Y\n")

while True:
    ret, frame = cap.read()

    if not ret:
        print("No se pudo acceder a la camara")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    naranja_bajo = np.array([5, 80, 80])
    naranja_alto = np.array([28, 255, 255])

    mascara = cv2.inRange(hsv, naranja_bajo, naranja_alto)

 

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contornos) > 0:
        c = max(contornos, key=cv2.contourArea)
        ((x, y), radio) = cv2.minEnclosingCircle(c)

        if radio > 5:

            cv2.circle(frame, (int(x), int(y)), int(radio), (0, 0, 255), 2)
            cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)

            print(f"Balon detectado en la posicion X: {int(x)}, {int(y)}")
            
            puntos_trayectoria.append((int(x), int(y)))
            archivo_datos.write(f"{int(x)}, {int(y)}\n")

            tiempo_actual = time.time()
            dt = tiempo_actual - ultimo_tiempo
            
            if ultimo_x is not None and dt > 0:
                distancia = ((x - ultimo_x)**2 + (y - ultimo_y)**2)**0.5
                
                if distancia > 6:
                    velocidad = distancia / dt
                else:
                    velocidad = 0
                    
                cv2.putText(frame, f"Vel: {int(velocidad)} px/s", (int(x) - 50, int(y) - int(radio) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            else: 
                cv2.putText(frame, "Vel 0 px/s", (int(x) - 50, int (radio) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            ultimo_x, ultimo_y = x, y
        
        else:
            puntos_trayectoria.append(None)
            ultimo_x, ultimo_y = None, None

    else: 
        puntos_trayectoria.append(None)
        ultimo_x, ultimo_y = None, None

    ultimo_tiempo = time.time()

    
    if len(puntos_trayectoria) > 20:
        puntos_trayectoria.pop(0)

    for i in range(1, len(puntos_trayectoria)):
        if puntos_trayectoria[i - 1] is None or puntos_trayectoria[i] is None:
            continue
        cv2.line(frame, puntos_trayectoria[i - 1], puntos_trayectoria[i], (0, 0, 255), 3)

    cv2.imshow('Camara Normal - jeronimo', frame)
    cv2.imshow('Deteccion de balon (Filtro naranja)', mascara)
    
archivo_datos.close() 
cap.release()
cv2.destroyAllWindows()





