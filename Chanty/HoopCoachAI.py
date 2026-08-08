import os
import cv2
import math
import time
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1)
mp_dibujo = mp.solutions.drawing_utils

# Carpeta para guardar las capturas de errores
CARPETA_ERRORES = "errores"

camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not camara.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

estado_tiro = 0
fase_actual_texto = "Listo para tirar"
tiempo_inicio_tiro = 0
tiempo_fin_tiro = 0

min_angulo_rodilla_tiro = 180
max_angulo_codo_tiro = 0
angulo_hombro_release = 0

tiros_intentados = 0
repeticiones_correctas = 0
historial_puntajes = []
ultimo_puntaje = 100
ultimo_consejo = ""

CONSEJOS = {
    "rodilla": "Flexiona mas las rodillas antes de subir",
    "codo": "Extiende completamente el codo al soltar",
    "hombro": "Ajusta la altura del brazo al tirar",
    "perfecto": "¡Excelente técnica de lanzamiento!"
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


def dibujar_hud(frame, estado_fase, repeticiones, total_tiros, puntaje, consejo=""):
    h, w, _ = frame.shape
    overlay = frame.copy()

    cv2.rectangle(overlay, (0, 0), (w, 55), (15, 15, 15), -1)
    
    if consejo:
        cv2.rectangle(overlay, (0, h - 50), (w, h), (15, 15, 15), -1)

    alpha = 0.65
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    color_fase = (0, 255, 255) if estado_fase == "ANALIZANDO TIRO..." else (255, 255, 255)
    cv2.putText(frame, f"ESTADO: {estado_fase}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_fase, 2, cv2.LINE_AA)

    cv2.putText(frame, f"TIROS: {repeticiones}/{total_tiros}", (w // 2 - 60, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    color_score = (0, 255, 0) if puntaje >= 80 else ((0, 255, 255) if puntaje >= 60 else (0, 0, 255))
    cv2.putText(frame, f"ULTIMO TIRO: {int(puntaje)}/100", (w - 240, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_score, 2, cv2.LINE_AA)

    if consejo:
        color_consejo = (0, 255, 0) if consejo == CONSEJOS["perfecto"] else (0, 165, 255)
        cv2.putText(frame, f"ANALISIS: {consejo}", (20, h - 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_consejo, 2, cv2.LINE_AA)

    return frame


def analizar_postura(frame, resultados=None):
    global estado_tiro
    global fase_actual_texto
    global tiempo_inicio_tiro
    global tiempo_fin_tiro
    global min_angulo_rodilla_tiro
    global max_angulo_codo_tiro
    global angulo_hombro_release
    global tiros_intentados
    global repeticiones_correctas
    global historial_puntajes
    global ultimo_puntaje
    global ultimo_consejo

    if resultados is None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = pose.process(frame_rgb)

    if not resultados or not resultados.pose_landmarks:
        return frame

    mp_dibujo.draw_landmarks(
        frame,
        resultados.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    pose_landmarks = resultados.pose_landmarks.landmark

    try:
        muneca = pose_landmarks[16]
        codo = pose_landmarks[14]
        hombro = pose_landmarks[12]
        cadera = pose_landmarks[24]
        rodilla = pose_landmarks[26]
        tobillo = pose_landmarks[28]
    except IndexError:
        return frame

    articulaciones_clave = [hombro, cadera, rodilla, tobillo]
    cuerpo_visible = all(art.visibility > 0.6 for art in articulaciones_clave)

    angulo_codo = calcular_angulo(hombro, codo, muneca)
    angulo_rodilla = calcular_angulo(cadera, rodilla, tobillo)
    angulo_hombro = calcular_angulo(cadera, hombro, codo)

    ahora = time.time()
    guardar_foto_error = False
    tipo_error = "postura"

    if estado_tiro == 0:
        fase_actual_texto = "Listo para tirar"
        if cuerpo_visible and angulo_rodilla < 155 and muneca.y > hombro.y:
            estado_tiro = 1
            tiempo_inicio_tiro = ahora
            fase_actual_texto = "ANALIZANDO TIRO..."
            min_angulo_rodilla_tiro = angulo_rodilla
            max_angulo_codo_tiro = angulo_codo
            angulo_hombro_release = angulo_hombro

    elif estado_tiro == 1:
        fase_actual_texto = "ANALIZANDO TIRO..."
        min_angulo_rodilla_tiro = min(min_angulo_rodilla_tiro, angulo_rodilla)
        max_angulo_codo_tiro = max(max_angulo_codo_tiro, angulo_codo)
        angulo_hombro_release = angulo_hombro

        if ahora - tiempo_inicio_tiro > 3.5:
            estado_tiro = 0
            fase_actual_texto = "Listo para tirar"

        elif muneca.y < hombro.y and angulo_codo > 135:
            tiros_intentados += 1
            score = 100
            fallos = []

            if min_angulo_rodilla_tiro > 150:
                score -= 35
                fallos.append("rodilla")

            if max_angulo_codo_tiro < 145:
                score -= 35
                fallos.append("codo")

            if not (65 <= angulo_hombro_release <= 110):
                score -= 30
                fallos.append("hombro")

            score = max(0, score)
            ultimo_puntaje = score
            historial_puntajes.append(score)

            if score >= 80:
                repeticiones_correctas += 1
                ultimo_consejo = CONSEJOS["perfecto"]
            else:
                ultimo_consejo = CONSEJOS[fallos[0]] if fallos else ""
                guardar_foto_error = True
                tipo_error = fallos[0] if fallos else "postura"

            tiempo_fin_tiro = ahora
            estado_tiro = 2

    elif estado_tiro == 2:
        fase_actual_texto = f"TIRO EVALUADO ({int(ultimo_puntaje)} pts)"
        if ahora - tiempo_fin_tiro > 3.0:
            estado_tiro = 0

    frame = dibujar_hud(
        frame,
        fase_actual_texto,
        repeticiones_correctas,
        tiros_intentados,
        ultimo_puntaje,
        ultimo_consejo
    )

    # Si hubo error, guarda la foto incluyendo la interfaz y el esqueleto
    if guardar_foto_error:
        os.makedirs(CARPETA_ERRORES, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nombre_archivo = os.path.join(CARPETA_ERRORES, f"error_{tipo_error}_{timestamp}.jpg")
        cv2.imwrite(nombre_archivo, frame)
        print(f"📸 Foto guardada en {CARPETA_ERRORES}/: {nombre_archivo}")

    return frame


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