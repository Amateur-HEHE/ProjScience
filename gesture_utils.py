"""
gesture_utils.py
-----------------
MediaPipe-based hand tracking + rule-based (geometric) gesture classification.

Uses the classic "Legacy Solutions" API (mp.solutions.hands), which is
present in mediapipe==0.10.21 (it was removed starting in mediapipe 0.10.30,
so this file assumes an older, pinned mediapipe version - see requirements.txt).
"""

import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

TIP_IDS = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
PIP_IDS = {"index": 6, "middle": 10, "ring": 14, "pinky": 18}


def get_hands_detector(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.6):
    """Factory for a configured MediaPipe Hands detector."""
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=max_num_hands,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )


def _dist(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def _tip_xy(landmarks, name):
    lm = landmarks[TIP_IDS[name]]
    return (lm.x, lm.y)


def _finger_states(landmarks, handedness_label):
    """Return a dict of finger_name -> True(extended)/False(curled)."""
    states = {}
    for finger in ("index", "middle", "ring", "pinky"):
        tip_idx, pip_idx = TIP_IDS[finger], PIP_IDS[finger]
        states[finger] = landmarks[tip_idx].y < landmarks[pip_idx].y

    if handedness_label == "Right":
        states["thumb"] = landmarks[4].x < landmarks[3].x
    else:
        states["thumb"] = landmarks[4].x > landmarks[3].x

    return states


def classify_gesture(landmarks, handedness_label):
    """
    Classify a single hand's 21 landmarks (a MediaPipe .landmark list) into
    one of the supported gesture labels. Returns "Unknown" if no rule
    matches confidently.
    """
    f = _finger_states(landmarks, handedness_label)
    thumb, index, middle, ring, pinky = (
        f["thumb"], f["index"], f["middle"], f["ring"], f["pinky"]
    )

    thumb_tip_y = landmarks[4].y
    thumb_mcp_y = landmarks[2].y

    # --- OK: thumb + index pinched, other three extended
    if _dist(_tip_xy(landmarks, "thumb"), _tip_xy(landmarks, "index")) < 0.06 and middle and ring and pinky:
        return "OK 👌"

    # --- Pinched Fingers (all 5 fingertips gathered together, hand pointing up)
    tips = [_tip_xy(landmarks, n) for n in ("thumb", "index", "middle", "ring", "pinky")]
    max_spread = max(_dist(tips[i], tips[j]) for i in range(5) for j in range(i + 1, 5))
    if max_spread < 0.09 and thumb_tip_y < landmarks[0].y:
        return "Pinched Fingers 🤌🏻"

    # --- All four fingers curled -> thumb direction decides Up / Down / Fist
    if not index and not middle and not ring and not pinky:
        if thumb_tip_y < thumb_mcp_y - 0.06:
            return "I Agree 👍"
        elif thumb_tip_y > thumb_mcp_y + 0.06:
            return "Nope 👎"
        else:
            return "Help ✊"

    # --- Call Me / Shaka: thumb + pinky extended, rest curled
    if thumb and pinky and not index and not middle and not ring:
        return "Call Me 🤙🏻"

    # --- Middle finger only
    if middle and not index and not ring and not pinky:
        return "🖕"

    # --- Peace / Victory
    if index and middle and not ring and not pinky and not thumb:
        return "Peace ✌️"

    # --- I Love You (ASL)
    if thumb and index and pinky and not middle and not ring:
        return "I Love You 🤟"

    # --- Single pointing finger
    if index and not middle and not ring and not pinky:
        return "Point ☝️"

    # --- Open palm
    if thumb and index and middle and ring and pinky:
        return "Hello ✋"

    return "Unknown"


def classify_two_hand_gesture(hands_landmarks_list, handedness_list):
    """
    Check for gestures that require both hands together (heart hands, shy
    pointing). Returns a label string if matched, else None.
    """
    if len(hands_landmarks_list) != 2:
        return None

    lm1, lm2 = hands_landmarks_list
    f1 = _finger_states(lm1, handedness_list[0])
    f2 = _finger_states(lm2, handedness_list[1])

    thumb_dist = _dist(_tip_xy(lm1, "thumb"), _tip_xy(lm2, "thumb"))
    index_dist = _dist(_tip_xy(lm1, "index"), _tip_xy(lm2, "index"))

    # --- Heart Hands: thumb tips close together AND index tips close together,
    # other three fingers curled on both hands
    if (
        thumb_dist < 0.09 and index_dist < 0.09
        and not f1["middle"] and not f1["ring"] and not f1["pinky"]
        and not f2["middle"] and not f2["ring"] and not f2["pinky"]
    ):
        return "Heart 🫶🏻"

    # --- Shy / pointing at each other: both hands doing "Point", index tips close
    def is_point(f):
        return f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]

    if is_point(f1) and is_point(f2) and index_dist < 0.14:
        return "Shy 👉🏻👈🏻"

    return None
