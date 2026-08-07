import cv2
import mediapipe as mp
import math
import time

# Inicialización de MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1)
mp_dibujo = mp.solutions.drawing_utils

# Configuración de cámara
camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not camara.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

# Variables globales de la máquina de estados y métricas
estado_tiro = 0
angulo_liberacion = 0
repeticiones_correctas = 0
tiros_intentados = 0
postura_ok_ciclo = True
tiempo_ultimo_tiro = 0
tiempo_inicio_fase = time.time()
tiempo_inicio_sesion = time.time()
fase_actual_texto = "Preparación"

puntaje_actual = 100
historial_puntajes = []
tiempo_frame_anterior = time.time()
PENALIZACION_POR_SEGUNDO = 15

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

def dibujar_hud(frame, estado_fase, repeticiones, puntaje, consejo=""):
    """
    Dibuja un HUD semi-transparente profesional sobre el video
    """
    h, w, _ = frame.shape
    overlay = frame.copy()

    # 1. Dibujar rectángulos oscuros para el fondo del HUD
    cv2.rectangle(overlay, (0, 0), (w, 55), (15, 15, 15), -1)
    if consejo:
        cv2.rectangle(overlay, (0, h - 45), (w, h), (15, 15, 15), -1)

    # 2. Mezclar capa semi-transparente
    alpha = 0.65
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # 3. Textos en la barra superior
    cv2.putText(frame, f"FASE: {estado_fase}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, f"REPS OK: {repeticiones}", (w // 2 - 70, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    color_score = (0, 255, 0) if puntaje >= 80 else ((0, 255, 255) if puntaje >= 50 else (0, 0, 255))
    cv2.putText(frame, f"SCORE: {int(puntaje)}/100", (w - 200, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_score, 2, cv2.LINE_AA)

    # 4. Consejo en la barra inferior (si existe)
    if consejo:
        cv2.putText(frame, f"CONSEJO: {consejo}", (20, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)

    return frame

def analizar_postura(frame, resultados=None):
    global estado_tiro
    global tiempo_ultimo_tiro
    global tiempo_inicio_fase
    global angulo_liberacion
    global repeticiones_correctas
    global tiros_intentados
    global postura_ok_ciclo
    global fase_actual_texto
    global puntaje_actual
    global historial_puntajes
    global tiempo_frame_anterior

    # Si no recibe resultados externos, procesa la pose
    if resultados is None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = pose.process(frame_rgb)

    # Si no detecta pose en la cámara, retorna el frame limpio
    if not resultados or not resultados.pose_landmarks:
        return frame

    ahora = time.time()
    dt = ahora - tiempo_frame_anterior
    tiempo_frame_anterior = ahora

    mp_dibujo.draw_landmarks(
        frame,
        resultados.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

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

    rodilla_ok = 150 <= angulo_rodilla <= 170
    espalda_ok = angulo_espalda >= 150
    hombro_ok = 70 <= angulo_hombro <= 100

    postura_valida = rodilla_ok and espalda_ok and hombro_ok
    postura_ok_ciclo = postura_ok_ciclo and postura_valida

    fallos = []
    if not rodilla_ok:
        fallos.append("rodilla")
    if not espalda_ok:
        fallos.append("espalda")
    if not hombro_ok:
        fallos.append("hombro")

    if estado_tiro != 0:
        if not rodilla_ok:
            puntaje_actual -= PENALIZACION_POR_SEGUNDO * dt
        if not espalda_ok:
            puntaje_actual -= PENALIZACION_POR_SEGUNDO * dt
        if not hombro_ok:
            puntaje_actual -= PENALIZACION_POR_SEGUNDO * dt
        puntaje_actual = max(0, puntaje_actual)

    if estado_tiro != 0:
        if time.time() - tiempo_inicio_fase > 3:
            estado_tiro = 0
            postura_ok_ciclo = True
            tiempo_inicio_fase = time.time()
            fase_actual_texto = "Timeout"

    if estado_tiro == 0:
        fase_actual_texto = "Preparación"
        if angulo_rodilla < 165 and muneca.y > hombro.y:
            estado_tiro = 1
            tiempo_inicio_fase = time.time()
            puntaje_actual = 100

    elif estado_tiro == 1:
        fase_actual_texto = "Set Point"
        if muneca.y < hombro.y and 60 <= angulo_codo <= 125:
            estado_tiro = 2
            tiempo_inicio_fase = time.time()
        elif muneca.y > cadera.y:
            estado_tiro = 0
            postura_ok_ciclo = True
            tiempo_inicio_fase = time.time()

    elif estado_tiro == 2:
        fase_actual_texto = "Release (Tiro!)"
        if angulo_codo > 140 and muneca.y < hombro.y:
            if (time.time() - tiempo_ultimo_tiro) > 1.0:
                angulo_liberacion = angulo_codo
                tiros_intentados += 1
                historial_puntajes.append(round(puntaje_actual))

                if postura_ok_ciclo:
                    repeticiones_correctas += 1
                    print("Repetición completada con buena forma")
                else:
                    print("Repetición completada, pero con errores de postura")

                print(f"Puntaje del lanzamiento: {round(puntaje_actual)}/100")

                tiempo_ultimo_tiro = time.time()
                estado_tiro = 0
                postura_ok_ciclo = True
                tiempo_inicio_fase = time.time()

        elif muneca.y > hombro.y:
            estado_tiro = 0
            postura_ok_ciclo = True
            tiempo_inicio_fase = time.time()

    consejo_principal = CONSEJOS[fallos[0]] if fallos else ""

    frame = dibujar_hud(
        frame,
        fase_actual_texto,
        repeticiones_correctas,
        puntaje_actual,
        consejo_principal
    )

    return frame


# Bucle principal de ejecución
cv2.namedWindow("HoopCoach AI", cv2.WINDOW_NORMAL)
cv2.resizeWindow("HoopCoach AI", 960, 540)

while True:
    ret, frame = camara.read()

    if not ret or frame is None:
        break

    frame = analizar_postura(frame)

    cv2.imshow("HoopCoach AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camara.release()
cv2.destroyAllWindows()