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
            handType = detector.handType(lmList)
            fingers = []

            # Baş parmak
            if handType == "Right":
                fingers.append(1 if lmList[4][1] > lmList[3][1] else 0)
            else:
                fingers.append(1 if lmList[4][1] < lmList[3][1] else 0)

            # Diğer 4 parmak
            for tipId in [8, 12, 16, 20]:
                fingers.append(1 if lmList[tipId][2] < lmList[tipId - 2][2] else 0)

            # gesture'a göre sayı belirle
            number = detector.detect_number(fingers)
            print("Gesture:", fingers, "Tahmin:", number)

            if number < len(overlayList):
                h, w, c = overlayList[number].shape
                img[0:h, 0:w] = overlayList[number]


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (200, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
