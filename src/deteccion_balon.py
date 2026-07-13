import cv2
import numpy as np

cap = cv2.VideoCapture(0)
puntos_trayectoria = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo acceder a la camara")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    naranja_bajo = np.array([5, 100, 100])
    naranja_alto = np.array([15, 255, 255])

    mascara = cv2.inRange(hsv, naranja_bajo, naranja_alto)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contornos) > 0:
        c = max(contornos, key=cv2.contourArea)

    ((x, y), radio) = cv2.minEnclosingCircle(c)

    if radio > 10:
        cv2.circle(frame, (int(x), int(y)), int(radio), (0, 0, 255), 2)
        cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
        print(f"Balon detectado en la posicion X: {int(x)}, {int(y)}")
        puntos_trayectoria.append((int(x), int(y)))
    
    if len(puntos_trayectoria) > 20:
        puntos_trayectoria.pop(0)

    for i in range(1, len(puntos_trayectoria)):
        if puntos_trayectoria[i - 1] is None or puntos_trayectoria[i] is None:
            continue
        cv2.line(frame, puntos_trayectoria[i - 1], puntos_trayectoria[i], (0, 0, 255), 3)


        

cap.release()
cv2.destroyAllWindows()





