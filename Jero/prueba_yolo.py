import cv2
import math
import time
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


puntos_trayectoria = []
posicion_anterior = None
tiempo_anterior = time.time()
velocidad = 0.0

PÍXELES_POR_METRO = 500

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    tiempo_actual = time.time()
    dt = tiempo_actual - tiempo_anterior
    tiempo_anterior =tiempo_actual

    results = model.track(frame, device= 'cpu', verbose=False, classes=[32], conf=0.15, persist=True, imgsz=320)

    centro_actual = None

    if results[0].boxes is not None and len(results[0].boxes) > 0:
        box = results[0].boxes[0]
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = xyxy

        centro_x = int((x1 + x2) / 2)
        centro_y = int((y1 + y2) / 2)
        centro_actual = (centro_x, centro_y)

        if posicion_anterior is not None and dt > 0:
            distancia_pixeles = math.sqrt((centro_x - posicion_anterior[0])**2 + (centro_y - posicion_anterior[1])**2)
            distancia_metros = distancia_pixeles / PÍXELES_POR_METRO
            velocidad_m_s = distancia_metros / dt
            velocidad = velocidad_m_s * 3.6

        posicion_anterior = centro_actual
    else: 
        pass

    puntos_trayectoria.append(centro_actual)
    if len(puntos_trayectoria) > 15:
        puntos_trayectoria.pop(0)

    annotated_frame = results[0].plot()

    for i in range(1, len (puntos_trayectoria)):
        if puntos_trayectoria[i - 1] is None or puntos_trayectoria[i] is None:
            continue
        cv2.line(annotated_frame, puntos_trayectoria[i - 1], puntos_trayectoria[i], (0, 0, 255), 3)

    cv2.putText(annotated_frame, f"Velocidad: {velocidad: .1f} km/h", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)




    cv2.imshow("Proyecto YOLO - Balon + trayectoria + velocidad", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()