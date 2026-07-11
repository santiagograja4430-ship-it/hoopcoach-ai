import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_dibujo = mp.solutions.drawing_utils

camara = cv2.VideoCapture(0)
contador = 0

while True:
    ret, frame = camara.read()
    contador += 1

    if not ret or frame is None:
        break
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(frame_rgb)

    if resultados.pose_landmarks:
        mp_dibujo.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        muneca = resultados.pose_landmarks.landmark[16]
        h, w, _ = frame.shape
        cx, cy = int(muneca.x * w), int(muneca.y * h)

        cv2.circle(frame, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
        cv2.putText(frame, f'Muñeca: {cx},{cy}', (cx, cy - 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0,), 2)

    cv2.putText(frame, f'Frame: {contador}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("HoopCoach AI - Detectando Postura...", frame)

    if cv2.waitKey(1) == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()