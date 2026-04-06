def count_pushups(elbow_angles):
    counter = 0
    stage = None
    for angle in elbow_angles:
        if angle < 90:
            stage = "down"
        if angle > 160 and stage == "down":
            stage = "up"
            counter += 1
    return counter


def count_squats(knee_angles):
    counter = 0
    stage = None
    for angle in knee_angles:
        if angle < 90:
            stage = "down"
        if angle > 170 and stage == "down":
            stage = "up"
            counter += 1
    return counter


def count_situps(hip_angles):
    counter = 0
    stage = None
    for angle in hip_angles:
        if angle < 100:
            stage = "down"
        if angle > 140 and stage == "down":
            stage = "up"
            counter += 1
    return counter


def count_plank(elbow_angles):
    stable_frames = 0
    for angle in elbow_angles:
        if 160 <= angle <= 180:
            stable_frames += 1
    return round(stable_frames / 30, 2)  # seconds


def generate_score(reps, angles=None, exercise=None):

    feedback = "Good effort"

    if exercise == "pushup":
        if angles and min(angles) > 90:
            feedback = "Go lower in push-up (bend more)"
        elif reps > 20:
            feedback = "Excellent push-ups"
        else:
            feedback = "Increase repetitions"

    elif exercise == "squat":
        if angles and min(angles) > 100:
            feedback = "Bend your knees more"
        else:
            feedback = "Good squat form"

    elif exercise == "plank":
        feedback = "Maintain straight body posture"

    # score logic
    if reps > 30:
        score = 90
    elif reps > 15:
        score = 70
    else:
        score = 50

    return score, feedback