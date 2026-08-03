import cv2
import mediapipe as mp
import math
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1)
mp_dibujo = mp.solutions.drawing_utils

camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not camara.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

estado_tiro = 0
angulo_liberacion = 0
repeticiones_correctas = 0
postura_ok_ciclo = True
tiempo_ultimo_tiro = 0
tiempo_inicio_fase = time.time()
fase_actual_texto = "Fase: Esperando..."

CONSEJOS = {
    "rodilla": "Flexiona mas las rodillas",
    "espalda": "Sube mas el brazo antes de tirar",
    "hombro": "Ajusta la altura del brazo (entre 70 y 100 grados)",
}

def calcular_angulo(a, b, c):
    angulo = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x) -
        math.atan2(a.y - b.y, a.x - b.x)
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

def dibujar_metrica(frame, nombre, valor, esta_ok, y):
    color = (0, 255, 0) if esta_ok else (0, 0, 255)
    cv2.putText(frame, f'{nombre}: {int(valor)}', (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def analizar_postura(frame, resultados):
    global estado_tiro
    global tiempo_ultimo_tiro
    global tiempo_inicio_fase
    global angulo_liberacion
    global repeticiones_correctas
    global postura_ok_ciclo
    global fase_actual_texto

    mp_dibujo.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    muneca = resultados.pose_landmarks.landmark[16]
    codo = resultados.pose_landmarks.landmark[14]
    hombro = resultados.pose_landmarks.landmark[12]
    cadera = resultados.pose_landmarks.landmark[24]
    rodilla = resultados.pose_landmarks.landmark[26]
    tobillo = resultados.pose_landmarks.landmark[28]

    angulo_codo = calcular_angulo(hombro, codo, muneca)
    angulo_rodilla = calcular_angulo(cadera, rodilla, tobillo)
    angulo_espalda = calcular_angulo(rodilla, cadera, hombro)
    angulo_hombro = calcular_angulo(cadera, hombro, codo)

    h, w, _ = frame.shape
    cx, cy = int(muneca.x * w), int(muneca.y * h)

    rodilla_ok = 150 <= angulo_rodilla <= 170
    espalda_ok = angulo_espalda >= 150
    hombro_ok = 70 <= angulo_hombro <= 100

    postura_valida = (
        rodilla_ok and
        espalda_ok and
        hombro_ok
    )

    postura_ok_ciclo = postura_ok_ciclo and postura_valida

    fallos = []

    if not rodilla_ok:
        fallos.append("rodilla")

    if not espalda_ok:
        fallos.append("espalda")

    if not hombro_ok:
        fallos.append("hombro")

    if estado_tiro != 0:
        if time.time() - tiempo_inicio_fase > 3:
            estado_tiro = 0
            postura_ok_ciclo = True
            tiempo_inicio_fase = time.time()
            fase_actual_texto = "Fase 0: Timeout"

    if estado_tiro == 0:

        fase_actual_texto = "Fase 0: Preparación"

        if angulo_rodilla < 165 and muneca.y > hombro.y:
            estado_tiro = 1
            tiempo_inicio_fase = time.time()

    elif estado_tiro == 1:

        fase_actual_texto = "Fase 1: Set Point"

        if muneca.y < hombro.y and 60 <= angulo_codo <= 125:
            estado_tiro = 2
            tiempo_inicio_fase = time.time()

        elif muneca.y > cadera.y:
            estado_tiro = 0
            postura_ok_ciclo = True
            tiempo_inicio_fase = time.time()

    elif estado_tiro == 2:

        fase_actual_texto = "Fase 2: Release (Tiro!)"

        if angulo_codo > 140 and muneca.y < hombro.y:

            if (time.time() - tiempo_ultimo_tiro) > 1.0:

                angulo_liberacion = angulo_codo

                if postura_ok_ciclo:
                    repeticiones_correctas += 1
                    print("Repetición completada con buena forma")
                else:
                    print("Repetición completada, pero con errores de postura")

                tiempo_ultimo_tiro = time.time()
                estado_tiro = 0
                postura_ok_ciclo = True
                tiempo_inicio_fase = time.time()        

        elif muneca.y > hombro.y:
            estado_tiro = 0
            postura_ok_ciclo = True
            tiempo_inicio_fase = time.time()

    cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)

    cv2.putText(frame, f"Repeticiones OK: {repeticiones_correctas}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    cv2.putText(frame, fase_actual_texto, (30, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    dibujar_metrica(frame, "Rodilla", angulo_rodilla, rodilla_ok, 100)
    dibujar_metrica(frame, "Espalda", angulo_espalda, espalda_ok, 130)
    dibujar_metrica(frame, "Hombro", angulo_hombro, hombro_ok, 160)

    cv2.putText(frame, f"Codo (informativo): {int(angulo_codo)}", (30, 190),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

    y_consejo = 220

    for fallo in fallos:
        cv2.putText(frame, CONSEJOS[fallo], (30, y_consejo),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        y_consejo += 25

    return frame


cv2.namedWindow("HoopCoach AI", cv2.WINDOW_NORMAL)
cv2.resizeWindow("HoopCoach AI", 960, 540)

while True:

    ret, frame = camara.read()

    if not ret or frame is None:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(frame_rgb)

    if resultados.pose_landmarks:
        frame = analizar_postura(frame, resultados)

    cv2.imshow("HoopCoach AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()

print("\n--- RESUMEN DE LA SESION ---")
print(f"Repeticiones completadas con buena forma: {repeticiones_correctas}")