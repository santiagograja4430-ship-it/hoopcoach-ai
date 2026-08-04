import cv2
import math
import time
from pathlib import Path
from ultralytics import YOLO

# ===============================
# Modelo YOLO
# ===============================

MODEL_PATH = Path(__file__).parent / "yolo11n.pt"
model = YOLO(str(MODEL_PATH))

# ===============================
# Variables globales
# ===============================

PÍXELES_POR_METRO = 500

puntos_trayectoria = []

posicion_anterior = None
tiempo_anterior = 0

velocidad = 0.0
velocidad_maxima = 0.0
distancia_total = 0.0

balon_detectado = False

# ===============================
# Funciones auxiliares
# ===============================

def calcular_velocidad(posicion_actual, dt):

    global posicion_anterior
    global velocidad
    global distancia_total

    if posicion_anterior is None or dt <= 0:
        posicion_anterior = posicion_actual
        velocidad = 0
        return

    distancia_pixeles = math.sqrt(
        (posicion_actual[0] - posicion_anterior[0]) ** 2 +
        (posicion_actual[1] - posicion_anterior[1]) ** 2
    )

    distancia_total += distancia_pixeles

    distancia_metros = distancia_pixeles / PÍXELES_POR_METRO

    velocidad = (distancia_metros / dt) * 3.6

    posicion_anterior = posicion_actual


def dibujar_trayectoria(frame):

    for i in range(1, len(puntos_trayectoria)):

        if puntos_trayectoria[i - 1] is None:
            continue

        if puntos_trayectoria[i] is None:
            continue

        cv2.line(
            frame,
            puntos_trayectoria[i - 1],
            puntos_trayectoria[i],
            (0, 0, 255),
            3
        )

def iniciar_deteccion_balon():

    global tiempo_anterior
    global posicion_anterior
    global velocidad
    global puntos_trayectoria
    global distancia_total
    global balon_detectado
    global velocidad_maxima

    puntos_trayectoria = []
    posicion_anterior = None
    velocidad = 0.0
    velocidad_maxima = 0.0
    distancia_total = 0
    balon_detectado = False

    tiempo_anterior = time.time()

    camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not camara.isOpened():
        print("No se pudo abrir la cámara.")
        return

    cv2.namedWindow("HoopCoach AI - Detección de balón", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("HoopCoach AI - Detección de balón", 960, 540)

    while True:

        ret, frame = camara.read()

        if not ret or frame is None:
            break

        tiempo_actual = time.time()
        dt = tiempo_actual - tiempo_anterior
        tiempo_anterior = tiempo_actual

        resultados = model.track(
            frame,
            device="cpu",
            classes=[32],
            conf=0.15,
            persist=True,
            imgsz=320,
            verbose=False
        )

        centro_actual = None

        if (
            resultados[0].boxes is not None
            and len(resultados[0].boxes) > 0
        ):

            caja = resultados[0].boxes[0]

            x1, y1, x2, y2 = caja.xyxy[0].cpu().numpy()

            centro_x = int((x1 + x2) / 2)
            centro_y = int((y1 + y2) / 2)

            centro_actual = (centro_x, centro_y)

            balon_detectado = True

            calcular_velocidad(centro_actual, dt)

            velocidad_maxima = max(velocidad_maxima, velocidad)

        else:

            balon_detectado = False
            posicion_anterior = None

        puntos_trayectoria.append(centro_actual)

        if len(puntos_trayectoria) > 20:
            puntos_trayectoria.pop(0)

        frame = resultados[0].plot()

        dibujar_trayectoria(frame)

        estado = "Detectado" if balon_detectado else "No detectado"

        cv2.putText(
            frame,
            f"Balon: {estado}",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Velocidad: {velocidad:.1f} km/h",
            (20,75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Trayectoria: {len(puntos_trayectoria)} puntos",
            (20,110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.imshow(
            "HoopCoach AI - Detección de balón",
            frame
        )

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break

    camara.release()
    cv2.destroyAllWindows()

    print("\n========== RESUMEN ==========")
    print(f"Balón detectado: {'Sí' if balon_detectado else 'No'}")
    print(f"Velocidad máxima aproximada: {velocidad_maxima:.1f} km/h")
    print(f"Distancia recorrida (pixeles): {distancia_total:.1f}")
    print(f"Puntos registrados: {len(puntos_trayectoria)}")


if __name__ == "__main__":
    iniciar_deteccion_balon()