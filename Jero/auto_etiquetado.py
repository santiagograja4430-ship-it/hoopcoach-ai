import os
import cv2
import glob
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

RUTA_IMAGENES = "dataset_balon"
RUTA_LABELS = "dataset_balon_labels"

if not os.path.exists(RUTA_LABELS):
    os.makedirs(RUTA_LABELS)

imagenes = glob.glob(os.path.join(RUTA_IMAGENES, "*.jpg"))
print(f"Procesando {len(imagenes)} imagenes para auto-etiquetado...")

contador_exitos = 0 

for img_path in imagenes:
    img = cv2.imread(img_path)
    if img is None:
        continue

    h_img, w_img, _ = img.shape

    results = model.predict(img_path, classes=[32], conf=0.02, imgsz =640, verbose=False)

    lineas_etiquetas = []

    if results[0].boxes is not None and len(results[0].boxes) > 0:
        for box in results[0].boxes:

            xywhn = box.xywhn[0].cpu().numpy()
            x_center, y_center, w, h = xywhn

            lineas_etiquetas.append(f"0 {x_center: .6f} {y_center: .6f} {w: .6f} {h: .6f}\n")

    if lineas_etiquetas:
        nombre_base = os.path.basename(img_path).replace(".jpg", ".txt")
        ruta_txt = os.path.join(RUTA_LABELS, nombre_base)

        with open(ruta_txt, "w") as f:
            f.writelines(lineas_etiquetas)

        contador_exitos += 1

print("--------------------------------------------------")
print(f"¡Proceso terminado! Se etiquetaron automaticamente {contador_exitos} de {len(imagenes)} imagenes.")
print(f"Las etiquetas .txt quedaron guardadas en: {RUTA_LABELS}")


