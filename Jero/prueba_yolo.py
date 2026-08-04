import cv2
import math
import time
import numpy as np
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

Kalman = cv2.KalmanFilter(4, 2)
Kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
Kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)

Kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

puntos_trayectoria = []
posicion_anterior = None
tiempo_anterior = time.time()
velocidad = 0.0
apice_x = None
apice_y = float('inf')
tiro_en_progreso = False
PÍXELES_POR_METRO = 500



while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    tiempo_actual = time.time()
    prediccion = Kalman.predict()
    pred_x, pred_y = int(prediccion[0][0]), int(prediccion[1][0])
    dt = tiempo_actual - tiempo_anterior
    tiempo_anterior =tiempo_actual

    results = model.track(frame, device= 'cpu', verbose=False, classes=[32], conf=0.08, persist=True, imgsz=480)

    centro_actual = None

    if results[0].boxes is not None and len(results[0].boxes) > 0:
        box = results[0].boxes[0]
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = xyxy

        centro_x = int((x1 + x2) / 2)
        centro_y = int((y1 + y2) / 2)
        centro_actual = (centro_x, centro_y)

        if centro_y < apice_y:
            apice_y = centro_y
            apice_x = centro_x
            

        medicion = np.array([[np.float32(centro_x)], [np.float32(centro_y)]])
        Kalman.correct(medicion)

        puntos_trayectoria.append((pred_x, pred_y))
    
        if posicion_anterior is not None and dt > 0:
            distancia_pixeles = math.sqrt((centro_x - posicion_anterior[0])**2 + (centro_y - posicion_anterior[1])**2)
            distancia_metros = distancia_pixeles / PÍXELES_POR_METRO
            velocidad_m_s = distancia_metros / dt
            velocidad = velocidad_m_s * 3.6

        posicion_anterior = centro_actual

        
    else: 
        puntos_trayectoria.append((pred_x, pred_y))
        posicion_anterior = None

    
    if len(puntos_trayectoria) > 30:
        puntos_trayectoria.pop(0)

    annotated_frame = results[0].plot()

    for i in range(1, len (puntos_trayectoria)):
        if puntos_trayectoria[i - 1] is None or puntos_trayectoria[i] is None:
            continue
        cv2.line(annotated_frame, puntos_trayectoria[i - 1], puntos_trayectoria[i], (0, 0, 255), 3)

    cv2.putText(annotated_frame, f"Velocidad: {velocidad: .1f} km/h", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if apice_x is not None and apice_y != float('inf'):
        cv2.circle(annotated_frame, (apice_x, apice_y), 8, (0, 255, 255), -1)
        cv2.putText(annotated_frame, "APICE", (apice_x - 20, apice_y -15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)






    cv2.imshow("Proyecto YOLO - Balon + trayectoria + velocidad", annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        apice_x = None
        apice_y = float('inf')
        tiro_en_progreso = False


cap.release()
cv2.destroyAllWindows()