def generate_score(angle):

    if angle is None:
        return 0, "No Pose Detected"

    if 160 <= angle <= 180:
        return 90, "Excellent Form"
    elif 120 <= angle < 160:
        return 75, "Good Form"
    else:
        return 50, "Improve Arm Extension"
