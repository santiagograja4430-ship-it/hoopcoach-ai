import cv2
import mediapipe as mp
import math

# Configuración de MediaPipe para detección de pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_dibujo = mp.solutions.drawing_utils

# inicialización de cámara y variables de control
camara = cv2.VideoCapture(0)
contador = 0
anterior_y = None
subiendo = False
angulo_liberacion = 0
historial_angulos = []

# Función para calcular el ángulo entre estas partes del cuerpo: hombro, codo y muñeca
def calcular_angulo(hombro, codo, muneca):
    angulo = math.degrees(
        math.atan2(muneca.y - codo.y, muneca.x - codo.x) -
        math.atan2(hombro.y - codo.y, hombro.x - codo.x)
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

# Bucle principal para procesar cada frame de la cámara
while True:
    ret, frame = camara.read()
    contador += 1

    if not ret or frame is None:
        break

    # Conversión de color para MediaPipe 
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(frame_rgb)

    if resultados.pose_landmarks:
        mp_dibujo.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extracción de los puntos clave o coordenadas de (muñeca, codo, hombro) para calcular el ángulo
        muneca = resultados.pose_landmarks.landmark[16]
        codo = resultados.pose_landmarks.landmark[14]
        hombro = resultados.pose_landmarks.landmark[12]

        #Calculo del ángulo entre el hombro, codo y muñeca
        angulo = calcular_angulo(hombro, codo, muneca)
        h, w, _ = frame.shape
        cx, cy = int(muneca.x * w), int(muneca.y * h)

        #Definición de un umbral para detectar el movimiento de la muñeca y determinar si está subiendo o bajando
        umbral = 0.0015

        #Logica para determinar si la muñeca está subiendo o bajando y registrar el angulo de liberación
        if anterior_y is not None:
            if (anterior_y - muneca.y) > umbral:
                subiendo = True

            #Registro del angulo de liberación cuando la muñeca baja despues de haber subido
            if (muneca.y - anterior_y) > umbral and subiendo:
                angulo_liberacion = angulo
                historial_angulos.append(angulo)
                subiendo = False
        anterior_y = muneca.y

        #Los dibujos y textos que se muestran en la pantalla para indicar angulo de brazo y posición de la muñeca
        cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
        cv2.putText(frame, f'Muneca: {cx}', (cx, cy - 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Angulo: {int(angulo)}', (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f'Ultimo release: {int(angulo_liberacion)}', (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    
    cv2.putText(frame, f'Frame: {contador}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("HoopCoach AI - Postura", frame)

    if cv2.waitKey(1) == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()