import random
from server.utils.database import db
from server.models.question import SubtestType, Question


def generate_choices(correct: int) -> list[str]:
  choices = {correct}
  while len(choices) < 4:
    choices.add(random.randint(correct - 10, correct + 10))
  return list(map(str, random.sample(list(choices), 4)))


def generate_questions():
  all_questions = []

  for subtest in SubtestType:
    for _ in range(50):
      if subtest == SubtestType.DOT:
        dot = random.randint(1, 50)
        correct = dot
        choices = generate_choices(correct)
        q = Question(
          subtest=subtest,
          dot_amount=dot,
          correct_answer=str(correct),
          choice_1=choices[0],
          choice_2=choices[1],
          choice_3=choices[2],
          choice_4=choices[3],
        )

      elif subtest == SubtestType.STROOP:
        left_value = random.randint(1, 9)
        right_value = random.randint(1, 9)
        while right_value == left_value:
          right_value = random.randint(1, 9)

        left_size = random.randint(12, 60)
        right_size = random.randint(12, 60)
        while right_size == left_size:
          right_size = random.randint(12, 60)

        compare_by = random.choice(["value", "size"])

        if compare_by == "value":
          correct = max(left_value, right_value)
        else:
          correct = left_value if left_size > right_size else right_value

        choices = generate_choices(correct)
        q = Question(
          subtest=subtest,
          left_value=str(left_value),
          right_value=str(right_value),
          left_font_size=left_size,
          right_font_size=right_size,
          correct_answer=str(correct),
          choice_1=choices[0],
          choice_2=choices[1],
          choice_3=choices[2],
          choice_4=choices[3],
        )

      else:
        left = random.randint(10, 99)
        right = random.randint(10, 99)
        if subtest == SubtestType.ADD:
          result = left + right
          op = "+"
        elif subtest == SubtestType.SUBS:
          if right > left:
            left, right = right, left
          result = left - right
          op = "-"
        else:  # MULT
          result = left * right
          op = "×"

        choices = generate_choices(result)
        q = Question(
          subtest=subtest,
          left=left,
          right=right,
          operation=op,
          correct_answer=str(result),
          choice_1=choices[0],
          choice_2=choices[1],
          choice_3=choices[2],
          choice_4=choices[3],
        )

      all_questions.append(q)

  db.session.add_all(all_questions)
  db.session.commit()
