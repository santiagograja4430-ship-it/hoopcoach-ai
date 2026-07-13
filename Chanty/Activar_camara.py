import cv2
import time

camara = cv2.VideoCapture(0)
inicio_tiempo = time.time()
mostrar_gris = False

print("Cámara abierta. Presiona 'q' para salir.")

while True:
    funciona, video = camara.read()

    if not funciona:
        break

    if mostrar_gris:
        video = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
        video = cv2.cvtColor(video, cv2.COLOR_GRAY2BGR)

    tiempo_transcurrido = int(time.time() - inicio_tiempo)
    cv2.putText(video, f"Tiempo: {tiempo_transcurrido} s", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("HoopCoach AI", video)

    tecla = cv2.waitKey(1)
    if tecla == ord('q'):
        break
    elif tecla == ord('g'):
        mostrar_gris = not mostrar_gris

camara.release()
cv2.destroyAllWindows()