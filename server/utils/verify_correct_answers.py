from cryptography.fernet import Fernet, InvalidToken
import json


def verify_correct_answers(data, key):
  try:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(data["correct_answers"].encode())
    correct_data = json.loads(decrypted)

    expected_keys = [
      "dot_correct_answer",
      "stroop_correct_answer",
      "add_correct_answer",
      "subs_correct_answer",
      "mult_correct_answer",
    ]

    for key in expected_keys:
      if key not in correct_data:
        return False, f"Missing key in decrypted correct_answers: {key}"

      if not isinstance(correct_data[key], list) or len(correct_data[key]) != 5:
        return False, f"Invalid format for key: {key}"

      if not all(isinstance(x, int) and 0 <= x <= 3 for x in correct_data[key]):
        return False, f"Invalid values in {key}, must be ints 0-3"

    return True, correct_data

  except InvalidToken:
    return False, "Invalid encryption or tampered data"
  except Exception as e:
    return False, f"Error during decryption: {str(e)}"
