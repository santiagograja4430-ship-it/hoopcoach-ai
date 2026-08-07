import cv2
import glob
import os

RUTA_IMG = "dataset_balon"
RUTA_TXT = "dataset_balon_labels"

imagenes = glob.glob(os.path.join(RUTA_IMG, "*.jpg"))
print("=== VISUALIZADOR DE ETIQUETAS ===")
print("Presiona cualquier tecla para la siguiente foto | 'q' para salir")

for img_path in imagenes: 
    frame = cv2.imread(img_path)
    if frame is None: 
        continue

    h, w, _ = frame.shape
    nombre_txt = os.path.basename(img_path).replace(".jpg", ".txt")
    ruta_etiqueta = os.path.join(RUTA_TXT, nombre_txt)

    if os.path.exists(ruta_etiqueta):
        with open (ruta_etiqueta, "r") as f:
            lineas = f.readlines()

        for linea in lineas:
            partes = linea.strip().split()
            if len(partes) == 5:
                clase, xc, yc, bw, bh = map(float, partes)

                x1 = int((xc - bw / 2) * w)
                y1 = int((yc - bh / 2) * h)
                x2 = int((xc + bw / 2) * w)
                y2 = int((yc + bh / 2) * h)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Balon", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("comprobacion Dataset", frame)
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):
        break
cv2.destroyAllWindows