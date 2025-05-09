import cv2
import mediapipe as mp
import time

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        return lmList
    def findMultipleHandsPositions(self, img, draw=True):
        lmLists = []
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((id, cx, cy))
                lmLists.append(lmList)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return lmLists
    def handType(self, lmList):
        # Baş parmak yönüne göre el tipi tahmini (sağ/sol)
        if lmList[17][1] < lmList[5][1]:
            return "Right"
        else:
            return "Left"
    @staticmethod
    def detect_number(finger_states):
        """
        finger_states: [thumb, index, middle, ring, pinky]
        return: sayı (1-9 arası gesture'a göre)
        """
        # Örnek gesture kuralları (senin resimlerine göre yazıldı)
        if finger_states == [1, 0, 0, 0, 0]:
            return 1
        elif finger_states == [1, 1, 0, 0, 0]:
            return 2
        elif finger_states == [1, 1, 1, 0, 0]:
            return 3
        elif finger_states == [1, 1, 1, 1, 0]:
            return 4
        elif finger_states == [1, 1, 1, 1, 1]:
            return 5
        elif finger_states == [1, 0, 0, 0, 1]:
            return 6
        elif finger_states == [1, 1, 0, 0, 1]:
            return 7
        elif finger_states == [1, 1, 1, 0, 1]:
            return 8
        elif finger_states == [1, 1, 1, 1, 1]:  # aynı gesture hem 5 hem 9 olmasın diye ayırt etmeliyiz
            return 9  # bu durumda gesture kombinasyonu dışında başka kontrol eklemen gerekir
        else:
            return 0  # tanımsız gesture

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            print(lmList[4])
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
# main fonksiyonunu çağırarak başka projelerde kullanabilirsin sadece bu dosyayı projene import etmen yeterli.

if __name__ == "__main__":
    main()

# This code is a simple hand tracking module using OpenCV and MediaPipe.
# It captures video from the webcam, detects hands, and draws landmarks on them. 
# The frame rate is also displayed on the video feed.