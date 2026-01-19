def calculate_score(questions, user_answers):
    score = 0
    for q in questions:
        if user_answers.get(str(q.id)) == q.correct_option:
            score += 1
    return score
