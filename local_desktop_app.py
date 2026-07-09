"""
local_desktop_app.py
---------------------
OPTIONAL bonus script. Run directly with plain Python (no Streamlit,
no browser) for a quick desktop window with guaranteed offline audio:

    python local_desktop_app.py

Press 'q' to quit.
"""

import cv2
import threading
import pyttsx3

from gesture_utils import (
    get_hands_detector,
    mp_hands,
    mp_drawing,
    mp_drawing_styles,
    classify_gesture,
    classify_two_hand_gesture,
)

engine = pyttsx3.init()
engine.setProperty("rate", 170)
speaking_lock = threading.Lock()


def speak_async(text):
    def _run():
        with speaking_lock:
            engine.say(text)
            engine.runAndWait()
    threading.Thread(target=_run, daemon=True).start()


def main():
    cap = cv2.VideoCapture(0)
    hands = get_hands_detector(max_num_hands=2)
    last_gesture = None

    print("Press 'q' in the video window to quit.")

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        gesture_text = "No hand detected"

        if results.multi_hand_landmarks and results.multi_handedness:
            all_landmarks = []
            handedness_labels = []

            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
                all_landmarks.append(hand_landmarks.landmark)
                handedness_labels.append(handedness.classification[0].label)

            two_hand_label = classify_two_hand_gesture(all_landmarks, handedness_labels)
            if two_hand_label:
                gesture_text = two_hand_label
            else:
                gesture_text = classify_gesture(all_landmarks[0], handedness_labels[0])

        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (16, 16, 22), -1)
        cv2.putText(frame, f"Gesture: {gesture_text}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (74, 222, 222), 2)

        if gesture_text not in ("No hand detected", "Unknown") and gesture_text != last_gesture:
            spoken = " ".join(gesture_text.split(" ")[:-1]) or gesture_text
            speak_async(spoken)
            last_gesture = gesture_text
        elif gesture_text in ("No hand detected", "Unknown"):
            last_gesture = None

        cv2.imshow("GestureSpeak - Local Desktop Mode", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
