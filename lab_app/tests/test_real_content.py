"""The shipped lessons in lab_app/content: schema, self-check, and typical beginner mistakes."""
import pytest

from lab_app.core.content import ContentRepository
from lab_app.core.errors import ErrorType
from lab_app.core.grader import grade, verify_lesson

REPO = ContentRepository()


def test_written_days_are_contiguous_and_clean():
    """Days are written in order from Day 1 with a review every 7th day; adding a day needs no edit here."""
    last = REPO.available_days[-1]
    assert last >= 35, "stage 1 (Day 1-35) must stay complete"
    assert REPO.available_days == list(range(1, last + 1))
    assert REPO.warnings == []
    assert REPO.curriculum.total_days == 168
    assert [d.day for d in REPO.curriculum.days if d.is_review] == list(range(7, last + 1, 7))
    for lesson in REPO.lessons():
        assert lesson.required_exercise_ids, f"Day {lesson.day} has no required exercise"


@pytest.mark.parametrize("day", REPO.available_days)
def test_lesson_self_check(day):
    """Solutions pass, starters fail, runnable examples print what the text claims."""
    assert verify_lesson(REPO.lesson(day)) == []


@pytest.mark.parametrize("exercise_id, code, error_type", [
    ("d01_code_1", 'print("총액: 13500")\nprint("<class \'int\'>")\n', ErrorType.NONE),  # fixed output: accepted
    ("d02_fill_1", "a = input()\nb = int(input())\nprint(a + b)\n", ErrorType.TYPE_ERROR),
    ("d02_code_1", "m = int(input())\nprint(m / 60)\nprint(m % 60)\n", ErrorType.WRONG_ANSWER),
    ("d03_code_1", 'name = input()\nage = int(input())\nprint(f"{name}님, 내년에 {age + 1}살이 됩니다")\n',
     ErrorType.WRONG_ANSWER),                                                     # forgot strip()
    ("d03_code_1", 'name = input().strip()\nage = int(input())\nprint(name + "님, 내년에 " + str(age + 1) + "살이 됩니다")\n',
     ErrorType.STATIC_CHECK_FAILED),                                              # correct output, no f-string
    ("d04_code_1", 'age = int(input())\nif age < 8 or age > 65:\n    print("무료")\nelif age < 18:\n    print("5000원")\n'
                   'else:\n    print("10000원")\n', ErrorType.WRONG_ANSWER),       # boundary mistakes
    ("d05_code_1", "n = int(input())\nprint(sum(range(2, n + 1, 2)))\n", ErrorType.STATIC_CHECK_FAILED),
    ("d05_code_1", "n = int(input())\ntotal = 0\ni = 0\nwhile i <= n:\n    total += i\n", ErrorType.TIMEOUT),
    ("d06_code_1", 'def grade(score):\n    if score >= 90:\n        return "A"\n    elif score >= 80:\n        return "B"\n'
                   '    elif score >= 70:\n        return "C"\n    return "F"\n', ErrorType.WRONG_EXCEPTION),
    ("d07_code_1", 'n = int(input())\ntotal = 0\nbest = 0\nfor _ in range(n):\n    s = int(input())\n    total += s\n'
                   '    best = s\nprint(f"평균: {total / n:.1f}")\nprint(f"최고: {best}")\nprint("합격" if total / n >= 60 else "불합격")\n',
     ErrorType.WRONG_ANSWER),                                                     # best = last, not max
    ("d08_code_1", "def trim(items):\n    return items[1:-1]\n", ErrorType.WRONG_EXCEPTION),  # no length check
    ("d09_code_1", "def move_to_front(items, value):\n    items = items.remove(value)\n    items.insert(0, value)\n"
                   "    return items\n", ErrorType.ATTRIBUTE_ERROR),                 # reassigned None from remove()
    ("d10_code_1", 'def find_max(nums):\n    if not nums:\n        raise ValueError("빈 리스트")\n    best = 0\n'
                   "    for n in nums:\n        if n > best:\n            best = n\n    return best\n",
     ErrorType.WRONG_ANSWER),                                                     # best = 0 fails all-negative list
    ("d10_code_1", 'def find_max(nums):\n    if not nums:\n        raise ValueError("빈 리스트")\n    for n in nums:\n'
                   "        pass\n    return max(nums)\n", ErrorType.STATIC_CHECK_FAILED),
    ("d11_code_1", 'nums = input().split()\nnums.sort()\nprint(f"정렬: {nums}")\nmiddle = nums[1:-1]\n'
                   'print(f"평균: {sum(middle) / len(middle):.1f}")\n', ErrorType.TYPE_ERROR),  # forgot int()
    ("d12_code_1", 'def best_student(records):\n    if not records:\n        raise ValueError("없음")\n'
                   "    best_name, best_score = records[0]\n    for name, score in records:\n        if score >= best_score:\n"
                   "            best_name, best_score = name, score\n    return best_name, best_score\n",
     ErrorType.WRONG_ANSWER),                                                     # >= picks the later of a tie
    ("d13_code_1", "def column_sums(grid):\n    result = []\n    for c in range(len(grid[0])):\n        total = 0\n"
                   "        for r in range(len(grid)):\n            total += grid[c][r]\n        result.append(total)\n"
                   "    return result\n", ErrorType.INDEX_ERROR),                    # row/column swapped
    ("d14_code_1", 'n = int(input())\nbest_name, best_score, total = "", 0, 0\nscores = []\nfor _ in range(n):\n'
                   "    name, score = input().split()\n    score = int(score)\n    scores.append(score)\n    total += score\n"
                   "    if score > best_score:\n        best_name, best_score = name, score\n"
                   "count = 0\nfor s in scores:\n    if s >= total / n:\n        count += 1\n"
                   'print(f"1등: {best_name} {best_score}")\nprint(f"평균: {total / n:.1f}")\nprint(f"평균 이상: {count}명")\n',
     ErrorType.WRONG_ANSWER),                                                     # best starts at 0: all-zero class
    ("d15_code_1", "def add_stock(stock, item, count):\n    stock[item] = stock.get(item, 0) + count\n    return stock\n",
     ErrorType.WRONG_EXCEPTION),                                                  # no count check
    ("d16_code_1", "def top_seller(sales):\n    if not sales:\n        raise ValueError\n    best = None\n"
                   "    for name, count in sales.items():\n        if best is None or count > sales[best]:\n"
                   "            best = name\n    return best\n", ErrorType.WRONG_ANSWER),  # tie keeps first, not a-z
    ("d18_code_1", "def unique_in_order(items):\n    return list(set(items))\n", ErrorType.WRONG_ANSWER),  # order lost
    ("d26_code_1", "def sum_digits(n):\n    if n < 0:\n        raise ValueError\n    total = 0\n    while n:\n"
                   "        total += n % 10\n        n //= 10\n    return total\n", ErrorType.STATIC_CHECK_FAILED),  # loop
    ("d29_code_1", "n = int(input())\ntotal = 0\nfor _ in range(n):\n    total += int(input())\nprint(total)\n",
     ErrorType.VALUE_ERROR),                                                      # no try/except
    ("d31_code_1", "n = int(input())\nwith open('diary.txt', 'w', encoding='utf-8') as f:\n    for i in range(1, n + 1):\n"
                   "        f.write(f'{i}. {input()}')\nwith open('diary.txt', encoding='utf-8') as f:\n"
                   "    for line in f:\n        print(line.strip())\nprint(f'총 {n}줄 저장')\n",
     ErrorType.WRONG_ANSWER),                                                     # forgot \n in write()
])
def test_typical_mistakes(exercise_id, code, error_type):
    result = grade(REPO.exercise(exercise_id), code)
    assert result.error_type is error_type, [(t.test_id, t.error_type, t.message) for t in result.tests]


@pytest.mark.parametrize("day, exercise_id", [(7, "d07_code_2"), (13, "d13_code_2"), (14, "d14_code_2"),
                                              (21, "d21_code_2"), (28, "d28_code_2"), (35, "d35_code_2")])
def test_optional_challenge_is_not_required(day, exercise_id):
    lesson = REPO.lesson(day)
    assert exercise_id not in lesson.required_exercise_ids
    assert lesson.exercise(exercise_id).kind == "coding"
