import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, device= 'cpu', verbose=False, classes=[32], conf=0.10, persist=True, imgsz=320)

    annotated_frame = results[0].plot()

    cv2.imshow("Solo Balon - YOLO", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()