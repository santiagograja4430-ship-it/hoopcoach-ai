import cv2
import os
import time

CARPETA_DATASET = "dataset_balon"
if not os.path.exists(CARPETA_DATASET):
    os.makedirs(CARPETA_DATASET)

cap = cv2.VideoCapture(0)
contador = 0

INTERVALO_SEGUNDOS = 0.2
ultimo_tiempo_captura = time.time()
grabando_automatica = True

print("--- CAPTURA AUTOMÁTICA ACTIVADA ---")
print("P = Pausar / Reanudar ráfaga | Q = Salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    tiempo_actual = time.time()

    if grabando_automatica and (tiempo_actual - ultimo_tiempo_captura) >= INTERVALO_SEGUNDOS:
        nombre_archivo = os.path.join(CARPETA_DATASET, f"balon_{int(tiempo_actual * 1000)}.jpg")
        cv2.imwrite(nombre_archivo, frame)
        contador += 1
        ultimo_tiempo_captura = tiempo_actual
        print(f"Foto #{contador} guardada automaticamente")

    frame_mostrar = frame.copy()
    estado_texto = "GRABANDO RAFAGA" if grabando_automatica else "PAUSADO"
    color_texto = (0, 0, 255) if grabando_automatica else (0, 255, 255)

    cv2.putText(frame_mostrar, f"Estado: {estado_texto}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_texto, 2)
    cv2.putText(frame_mostrar, f"Fotos acumuladas: {contador}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_texto, 2)
    cv2.putText(frame_mostrar, f"P = Pausar/Reanudar | Q = Salir", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Captura Automatica para Dataset", frame_mostrar)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p'):
        grabando_automatica = not grabando_automatica

    cap.release()
    cv2.destroyAllWindows
    