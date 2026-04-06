def detect_cheating(angle_history):

    if len(angle_history) < 5:
        return False

    for i in range(1, len(angle_history)):
        if abs(angle_history[i] - angle_history[i-1]) > 60:
            return True

    return False
