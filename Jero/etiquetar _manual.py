import cv2
import os
import glob

RUTA_IMG = "dataset_balon"
RUTA_TXT = "dataset_balon_labels"

imagenes = glob.glob(os.path.join(RUTA_IMG, "*.jpg"))
ix, iy = -1, -1
drawing = False
caja = []

def dibujar_caja(event, x, y, flags, param):
    global ix, iy, drawing, caja
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True 
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        param['temp_frame'] = param['frame'].copy()
        cv2.rectangle(param['temp_frame'], (ix, iy), (x, y), (255, 0, 0), 2)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        caja = [ix, iy, x, y]
        cv2.rectangle(param['frame'], (ix, iy), (x, y), (0, 255, 0), 2)

for img_path in imagenes:
    frame = cv2.imread(img_path)
    if frame is None:
        continue

    h, w, _ = frame.shape
    param ={'frame': frame.copy(), 'temp_frame': frame.copy()}
    cv2.namedWindow("Etiquetador manual")
    cv2.setMouseCallback("Etiquetador manual", dibujar_caja, param)

    caja = []
    print(f"Etiquetando: {os.path.basename(img_path)} (Espacio = Guardar | S = Saltar | Q = Salir)")

    while True:
        img_mostrar = param['temp_frame'] if drawing else param['frame']
        cv2.imshow("Etiquetador manual", img_mostrar)
        key = cv2.waitKey(1) & 0xFF

        if key == 32 and len(caja) == 4: 
            x1, y1, x2, y2 = caja
            xc = ((x1 + x2) / 2) / w
            yc = ((y1 + y2) / 2) / h
            bw = abs(x2 - x1) / w
            bh = abs(y2 - y1) / h

            nombre_txt = os.path.basename(img_path).replace(".jpg", ".txt")
            with open(os.path.join(RUTA_TXT, nombre_txt),"w") as f:
                f.write(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
            print(" -> Guardado!")
            break
        elif key == ord('r'):
            param['frame'] = cv2.imread(img_path)
            param['temp_frame'] = param['frame'].copy()
            caja = []
            print("Cuadro borrado. ¡Dibuja de nuevo!")
        elif key == ord('s'):
            print(" -> Saltado")
            break
        elif key == ord('q'):
            cv2.destroyAllWindows()
            exit()

cv2.destroyAllWindows()