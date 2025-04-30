import cv2
import time
import os
import HandTrackingModule as htm

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

folderPath = "FingerImages"
myList = sorted(os.listdir(folderPath))  # Dosya sırası garanti altına alınır
overlayList = [cv2.imread(f'{folderPath}/{imgPath}') for imgPath in myList]

pTime = 0
detector = htm.handDetector(detectionCon=1, maxHands=2)

tipIds = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmLists = detector.findMultipleHandsPositions(img, draw=False)  # Tüm elleri döndürsün

    if lmLists:
        for lmList in lmLists:
            fingers = []

            # El tipi tespiti (Thumb yönü için)
            handType = detector.handType(lmList)  # "Right" or "Left"

            # Baş parmak kontrolü (el tipine göre yön değişir)
            if handType == "Right":
                fingers.append(1 if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1] else 0)
            else:
                fingers.append(1 if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1] else 0)

            # Diğer parmaklar
            for id in range(1, 5):
                fingers.append(1 if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2] else 0)

            totalFingers = fingers.count(1)
            print(f"El: {handType}, Sayı: {totalFingers}")

            if 0 <= totalFingers < len(overlayList):
                h, w, c = overlayList[totalFingers].shape
                img[0:h, 0:w] = overlayList[totalFingers]

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (200, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
