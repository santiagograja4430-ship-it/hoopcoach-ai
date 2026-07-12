import cv2
import numpy as np

def nada(x):
    pass

cv2.namedWindow("Calibracion")

cv2.createTrackbar("H Bajo", "Calibracion", 5, 179, nada)
cv2.createTrackbar("S Bajo", "Calibracion", 100, 255, nada)
cv2.createTrackbar("V Bajo", "Calibracion", 100, 255, nada)
cv2.createTrackbar("H Alto", "Calibracion", 15, 179, nada)
cv2.createTrackbar("S Alto", "Calibracion", 255, 255, nada)
cv2.createTrackbar("V Alto", "Calibracion", 255, 255, nada)

cap = cv2.VideoCapture(0)


while True:
    ret, frame = cap.read()
    if not ret:
        break
    alto, ancho, _ = frame.shape

    centro_x = int(ancho / 2)
    centro_y = int(alto / 2)

    cv2.line(frame, (centro_x - 20, centro_y), (centro_x + 20, centro_y), (0, 255, 0), 2)
    cv2.line(frame, (centro_x, centro_y - 20), (centro_x, centro_y + 20), (0, 255, 0), 2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_bajo = cv2.getTrackbarPos("H Bajo", "Calibracion")
    s_bajo = cv2.getTrackbarPos("S Bajo", "Calibracion")
    v_bajo = cv2.getTrackbarPos("V Bajo", "Calibracion")
    h_alto = cv2.getTrackbarPos("H Alto", "Calibracion")
    s_alto = cv2.getTrackbarPos("S Alto", "Calibracion")
    v_alto = cv2.getTrackbarPos("V Alto", "Calibracion")

    rango_bajo = np.array([h_bajo, s_bajo, v_bajo])
    rango_alto = np.array([h_alto, s_alto, v_alto])

    mascara = cv2.inRange(hsv, rango_bajo, rango_alto)
    fuente = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(frame, "HoopCoach AI v1.0", (10, 30), fuente, 0.8, (0, 255, 255), 2)

    info_bajo = f"Filtro Bajo - H:{h_bajo} S:{s_bajo} V:{v_bajo}"
    cv2.putText(frame, info_bajo, (10, 430), fuente, 0.5, (0, 255, 255), 2)

    info_alto = f"Filtro Alto - H:{h_alto} S:{s_alto} V{v_alto}"
    cv2.putText(frame, info_alto, (10, 460), fuente, 0.5, (0, 165, 255), 2)

    cv2.imshow("Camara Normal", frame)
    cv2.imshow("Mascara en Tiempo Real", mascara)

    if cv2.waitKey(1) & 0xFF == ord ('q'):
        break

cap.release()
cv2.destroyAllWindows()
