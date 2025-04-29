import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

###########################
wCam, hCam = 640, 480
###########################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector()

# Döngü öncesi, eşikler ve faktörleri tanımla
pinchThreshold         = 40    # px cinsinden, parmaklar bu mesafeden kısa ise 'kapalı' say
minMidDist, maxMidDist = 50, 400   # px cinsinden, midpoint mesafesinin minimum ve maksimum aralığı
slowAlpha, fastAlpha   = 0.03, 0.3 # yavaş ve hızlı güncelleme için α faktörleri

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
currentVol = volume.GetMasterVolumeLevel() # Başlangıçta mevcut ses düzeyini oku
volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0.0, None)
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img, draw=False)
    
    # Kaç el algılandı?
    hands = detector.results.multi_hand_landmarks or []
    numHands = len(hands)
    
    # 1. ve 2. el landmark listelerini al
    lm1 = detector.findPosition(img, handNo=0, draw=False) if numHands >= 1 else []
    lm2 = detector.findPosition(img, handNo=1, draw=False) if numHands >= 2 else []
    
    if lm1 and lm2:
        # 1. elin başparmak ve işaret parmağı uçları
        x1, y1 = lm1[4][1], lm1[4][2]
        x2, y2 = lm1[8][1], lm1[8][2]
        cx1, cy1 = (x1 + x2)//2, (y1 + y2)//2
        length1 = math.hypot(x2-x1, y2-y1)

        # 2. elin başparmak ve işaret parmağı uçları
        x3, y3 = lm2[4][1], lm2[4][2]
        x4, y4 = lm2[8][1], lm2[8][2]
        cx2, cy2 = (x3 + x4)//2, (y3 + y4)//2
        length2 = math.hypot(x4-x3, y4-y3)

        # Eller arası midpoint mesafesini hesapla
        cx3, cy3 = (cx1 + cx2)//2, (cy1 + cy2)//2
        midDist = math.hypot(cx2-cx1, cy2-cy1)

        # Pinch durumu: parmaklar kapalı mı?
        pinch1 = length1 < pinchThreshold
        pinch2 = length2 < pinchThreshold


        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx1, cy1), 8, (255, 0, 255), cv2.FILLED)
        
        cv2.circle(img, (x3, y3), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x4, y4), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x3, y3), (x4, y4), (255, 0, 255), 2)
        cv2.circle(img, (cx2, cy2), 8, (255, 0, 255), cv2.FILLED)
        
        cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 255), 2)
        cv2.circle(img, (cx3, cy3), 8, (255, 0, 255), cv2.FILLED)

        if pinch1:
            # İki parmağın midpoint'i
            cv2.circle(img, (cx1, cy1), 10, (0, 255, 0), cv2.FILLED)

            # Eller arası mesafe
            midDist = math.hypot(cx2 - cx1, cy2 - cy1)

            # Mesafeyi hedef volume'a eşle
            volTarget = np.interp(midDist, [minMidDist, maxMidDist], [minVol, maxVol])

            # Pinch2 kontrolü
            if pinch2:
                alpha = slowAlpha
                cv2.circle(img, (cx2, cy2), 10, (0, 255, 0), cv2.FILLED)
            else:
                alpha = fastAlpha

            # Yavaş veya hızlı şekilde currentVol'ü volTarget'a yaklaştır
            currentVol += (volTarget - currentVol) * alpha
            volume.SetMasterVolumeLevel(currentVol, None)

            # Ses barı ve yüzdesi için
            volBar = np.interp(currentVol, [minVol, maxVol], [400, 150])
            volPer = np.interp(currentVol, [minVol, maxVol], [0, 100])

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 2)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'Volume: {int(volPer)}%', (40, 450),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)