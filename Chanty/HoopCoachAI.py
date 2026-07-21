import cv2
import mediapipe as mp
import math
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1)
mp_dibujo = mp.solutions.drawing_utils

camara = cv2.VideoCapture(0)
camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)
contador = 0
anterior_y = None
subiendo = False
angulo_liberacion = 0
historial_angulos = []
tiempo_ultimo_tiro = 0
angulo_maximo_subida = 0
mensaje_mostrado = True
postura_valida = False
mensaje_postura = ""

CONSEJOS = {
    "rodilla": "Flexiona mas las rodillas",
    "codo": "Ajusta el codo (entre 80 y 110 grados)",
    "espalda": "Mantén mas la espalda recta",
    "hombro": "Sube mas el brazo antes de tirar",
}

def calcular_angulo(a, b, c):
    angulo = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x) -
        math.atan2(a.y, a.x - b.x)
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

def analizar_postura(frame, resultados):
    global anterior_y, subiendo, tiempo_ultimo_tiro, angulo_liberacion
    global historial_angulos, mensaje_mostrado, angulo_maximo_subida
    global postura_valida, mensaje_postura

    mp_dibujo.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    muneca = resultados.pose_landmarks.landmark[16]
    codo = resultados.pose_landmarks.landmark[14]
    hombro = resultados.pose_landmarks.landmark[12]
    cadera = resultados.pose_landmarks.landmark[24]
    rodilla = resultados.pose_landmarks.landmark[26]
    tobillo = resultados.pose_landmarks.landmark[28]

    if muneca.visibility > 0.5 and codo.visibility > 0.5 and hombro.visibility > 0.5:
        if not mensaje_mostrado:
            print("Brazo detectado")
            mensaje_mostrado = True
    else:
        if mensaje_mostrado:
            print("Puntos perdidos: No se encuentra el brazo")
            mensaje_mostrado = False

    angulo = calcular_angulo(hombro, codo, muneca)
    angulo_rodilla = calcular_angulo(cadera, rodilla, tobillo)
    angulo_espalda = calcular_angulo(rodilla, cadera, hombro)
    angulo_hombro = calcular_angulo(cadera, hombro, codo)

    h, w, _ = frame.shape
    cx, cy = int(muneca.x * w), int(muneca.y * h)
    umbral = 0.04

    if anterior_y is not None:
        if (anterior_y - muneca.y) > umbral:
            if not subiendo:
                rodilla_ok = 150 <= angulo_rodilla <= 170
                codo_ok = 80 <= angulo >= 110
                espalda_ok = angulo_espalda >= 150
                hombro_ok = 70 <= angulo_hombro <= 100
                postura_valida = rodilla_ok and codo_ok and espalda_ok and hombro_ok

                fallos = []
                if not rodilla_ok:
                    fallos.append("rodilla")
                if not codo_ok:
                    fallos.append("codo")
                if not espalda_ok:
                    fallos.append("espalda")
                if not hombro_ok:
                    fallos.append("hombro")

                if postura_valida:
                    mensaje_postura = "Postura OK"
                else:
                    mensaje_postura = " | ".join(CONSEJOS[f] for f in fallos)

            subiendo = True
            angulo_maximo_subida = max(angulo_maximo_subida, angulo)

        if (muneca.y - anterior_y) > umbral and subiendo and (time.time() - tiempo_ultimo_tiro) > 1.0:
            print(f"Posible tiro, angulo maximo alcanzo: {int(angulo_maximo_subida)}")
            if angulo_maximo_subida > 140 and postura_valida:
                angulo_liberacion = angulo_maximo_subida
                historial_angulos.append(angulo_liberacion)
                tiempo_ultimo_tiro = time.time()
                print("Tiro contado")
            elif angulo_maximo_subida > 140 and not postura_valida:
                print("Tiro NO contado: postura incorrecta")
            subiendo = False
            angulo_maximo_subida = 0
    anterior_y = muneca.y

    cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
    cv2.putText(frame, f'Ultimo tiro: {int(angulo_liberacion)} grados', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

    color_msg = (0, 255, 0) if mensaje_postura == "Postura OK" else (0, 0, 255)
    cv2.putText(frame, mensaje_postura, (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_msg, 2)

    return frame

while True:
    ret, frame = camara.read()
    contador += 1

    if not ret or frame is None:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(frame_rgb)

    if resultados.pose_landmarks:
        frame = analizar_postura(frame, resultados)

    cv2.imshow("HoopCoach AI", frame)

    if cv2.waitKey(1) == ord ('q'):
        break

camara.release()
cv2.destroyAllWindows()

if historial_angulos:
    promedio = sum(historial_angulos) / len(historial_angulos)
    print(f"Tiros detectados: {len(historial_angulos)}")
    print(f"Angulo promedio de liberacion: {promedio:.1f}")
else:
    print("No se detectaron tiros en esta sesion.")