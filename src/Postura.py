import cv2
import mediapipe as mp
import math

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=2)
mp_dibujo = mp.solutions.drawing_utils

camara = cv2.VideoCapture(0)
contador = 0
anterior_y = None
subiendo = False
angulo_liberacion = 0
historial_angulos = []
lista_temporal_angulos = []

def calcular_angulo(hombro, codo, muneca):
    angulo = math.degrees(
        math.atan2(muneca.y - codo.y, muneca.x - codo.x) -
        math.atan2(hombro.y - codo.y, hombro.x - codo.x)
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

cooldown = 0
mensaje_mostrado = True

while True:
    ret, frame = camara.read()
    contador += 1

    if cooldown > 0:
        cooldown -= 1

    if not ret or frame is None:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(frame_rgb)

    if resultados.pose_landmarks:
        mp_dibujo.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        muneca = resultados.pose_landmarks.landmark[16]
        codo = resultados.pose_landmarks.landmark[14]
        hombro = resultados.pose_landmarks.landmark[12]
        if muneca.visibility > 0.5 and codo.visibility > 0.5 and hombro.visibility > 0.5:
            if not mensaje_mostrado:
                print("Brazo detectado")
                mensaje_mostrado = True 
        else:
            if mensaje_mostrado:
             print("Puntos perdidos: No se encuentra el brazo")
             mensaje_mostrado = False

        angulo = calcular_angulo(hombro, codo, muneca)
        h, w, _= frame.shape
        cx, cy = int(muneca.x * w), int(muneca.y * h)

        umbral = 0.04

        if anterior_y is not None:
            if (anterior_y - muneca.y) > umbral:
                subiendo = True
            if (muneca.y - anterior_y) > umbral and subiendo and angulo > 140:
                lista_temporal_angulos.append(angulo)
                if len(lista_temporal_angulos) >= 5:
                    angulo_liberacion = sum(lista_temporal_angulos) / len(lista_temporal_angulos)
                    historial_angulos.append(angulo_liberacion)
                    lista_temporal_angulos = []
                    subiendo = False
                    cooldown = 40
        anterior_y = muneca.y

        cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
        if 100 <= angulo <= 120:
            color_angulo = (0, 255, 255)
        else:
            color_angulo = (0, 255, 255)
        cv2.putText(frame, f'Angulo: {int(angulo)}', (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, color_angulo, 2)

        cv2.putText(frame, f'Muneca: {cx}', (cx, cy - 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Ultimo release: {int(angulo_liberacion)}', (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    cv2.putText(frame, f'Frame: {contador}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("HoopCoach AI - Postura", frame)

    if cv2.waitKey(1) == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()

if historial_angulos:
    promedio = sum(historial_angulos) / len(historial_angulos)
    print(f"Tiros detectados: {len(historial_angulos)}")
    print(f"Angulo promedio de liberacion: {promedio:.1f}")
else:
    print("No se detectaron tiros en la sesion.")                                 