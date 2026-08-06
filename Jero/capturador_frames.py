import cv2
import os
import time

CARPETA_DATASET = "dataset_balon"
if not os.path.exists(CARPETA_DATASET):
    os.makedirs(CARPETA_DATASET)

    cap = cv2.VideoCapture(0)
    contador = 0

    print("--- INSTRUCCIONES ---")
    print("Presiona 'ESPACIO' para guardar una foto")
    print("Presiona 'q' para salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_mostrar = frame.copy()
        cv2.putText(frame_mostrar, f"Fotos guardadas: {contador}", (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame_mostrar, "ESPACIO = Guardar | Q = Salir", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Captura de frames para dataset", frame_mostrar)

        key = cv2.waitKey(1) & 0xFF

        if key == 32:
            nombre_archivo = os.path.join(CARPETA_DATASET, f"balon_{int(time.time()*1000)}.jpg")
            cv2.imwrite(nombre_archivo, frame)
            contador += 1
            print(f"Foto #{contador} guardada: {nombre_archivo}")

        elif key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
