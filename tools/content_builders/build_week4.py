"""Week 4 (Day 22-28): 함수 심화와 모듈. Expected values come from independent reference code below."""
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import code, ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402

W = 4


# ---------------------------------------------------------------- reference implementations

def ref_price(amount, currency="원", comma=True):
    if amount < 0:
        raise ValueError
    return f"{amount:,}{currency}" if comma else f"{amount}{currency}"


def ref_stats(*nums):
    return [len(nums), sum(nums), sum(nums) / len(nums)]


def ref_bank(txs):
    balance, rejected = 0, 0
    for tx in txs:
        amount = int(tx)
        if balance + amount < 0:
            rejected += 1
        else:
            balance += amount
    return lines(f"잔액: {balance:,}원", f"거절: {rejected}건")


def ref_rank(scores):
    return [name for name, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]


def ref_fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def ref_top_words(text_, n):
    return [list(p) for p in Counter(text_.lower().split()).most_common(n)]


def ref_ranking(rows):
    ordered = sorted(rows, key=lambda r: (-r[1], r[0]))
    out, prev_score, rank = [], None, 0
    for i, (name, score) in enumerate(ordered, start=1):
        if score != prev_score:
            rank, prev_score = i, score
        out.append(f"{rank}. {name} {score}")
    return lines(*out)


def ref_flatten(x):
    out = []
    for item in x:
        out.extend(ref_flatten(item) if isinstance(item, list) else [item])
    return out


# ====================================================================== Day 22
price_cases = [((12000,), {}, "t1", "기본값"), ((12000,), {"currency": "달러"}, "t2", "통화 지정"),
               ((5000,), {"comma": False}, "t3", "쉼표 없음"), ((0,), {}, "h1", ""),
               ((1234567, "엔", False), {}, "h2", ""), ((999,), {"currency": ""}, "h3", "")]
day22 = lesson(
    22, "기본값과 키워드 인자", W, ["default_args", "function", "fstring"],
    ["매개변수에 기본값을 주어 생략 가능한 인자를 만들 수 있다.", "키워드 인자로 순서와 상관없이 값을 전달할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "3주차에는 딕셔너리·집합·문자열 처리를 배웠습니다. 이번 주는 **함수**를 더 유연하게 만드는 방법을 배웁니다. "
        "Day 6에서 `def`와 `return`, Day 12에서 튜플로 여러 값 돌려주기를 이미 해 봤어요."),
        "quiz": [quiz("d22_review_q1", "`sorted([3, 1, 2], reverse=True)`의 결과는?", ["`[1, 2, 3]`", "`[3, 2, 1]`", "`[3, 1, 2]`", "오류"], 1,
                      "`reverse=True`는 내림차순입니다. 오늘 배울 **키워드 인자**의 예이기도 합니다.")]},
    concept={"title": "생략 가능한 인자", "blocks": [
        text("`def 함수(이름, 매개변수=기본값):`처럼 기본값을 주면 호출할 때 그 인자를 생략할 수 있습니다. "
             "호출할 때 `이름=값` 형태로 쓰는 것을 **키워드 인자**라고 하며, 순서를 바꿔 써도 됩니다."),
        code('''
            def greet(name, greeting="안녕하세요"):
                return f"{greeting}, {name}님"

            print(greet("민준"))
            print(greet("서연", "반가워요"))
            print(greet(greeting="환영합니다", name="지호"))
        ''', lines("안녕하세요, 민준님", "반가워요, 서연님", "환영합니다, 지호님")),
        text("이미 써 온 `print()`의 `sep`, `end`와 `sorted()`의 `reverse`도 키워드 인자입니다."),
        code('''
            print("a", "b", sep="-")
            print("줄바꿈 없이", end=" ")
            print("이어서")
            print(sorted([3, 1, 2], reverse=True))
        ''', lines("a-b", "줄바꿈 없이 이어서", [3, 2, 1])),
        tip("기본값이 있는 매개변수는 기본값이 없는 매개변수 **뒤에** 와야 합니다. 그리고 기본값으로 리스트(`items=[]`)를 쓰면 호출할 때마다 같은 리스트가 공유되는 함정이 있습니다. "
            "대신 `None`을 기본값으로 두고 함수 안에서 새 리스트를 만드세요."),
        code('''
            def add_item(item, items=None):
                if items is None:
                    items = []
                items.append(item)
                return items

            print(add_item("a"))
            print(add_item("b"))
        ''', lines(["a"], ["b"])),
    ]},
    fill_intro="기본값이 있는 매개변수를 만들어 보세요. 채점은 위치 인자와 키워드 인자 호출을 모두 사용합니다.",
    coding_intro="기본값 두 개와 예외 처리를 함께 씁니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`def f(a, b=기본값)`: `b`는 생략 가능.",
        "키워드 인자 `f(b=1, a=2)`는 순서와 상관없다.",
        "기본값 매개변수는 뒤쪽에 둔다.",
        "바뀌는 값(리스트 등)은 기본값으로 쓰지 말고 `None`을 쓴다."],
        "quiz": [
            quiz("d22_summary_q1", "`def f(a, b=2): return a * b` 일 때 `f(3)`은?", ["3", "5", "6", "오류"], 2, "`b`가 생략되어 기본값 2가 쓰입니다."),
            quiz("d22_summary_q2", "올바른 함수 정의는?", ["`def f(a=1, b):`", "`def f(a, b=1):`", "`def f(=1 a):`", "`def f(a b=1):`"], 1,
                 "기본값이 없는 매개변수가 앞에 와야 합니다.")]},
    exercises=[
        ex("d22_fill_1", "fill_blank", "거듭제곱",
           "`base`의 `exp`제곱을 **반환**하는 함수를 완성하세요. `exp`를 생략하면 제곱(2)을 계산합니다.\n\n"
           "예: `power(3)` → `9`, `power(2, 10)` → `1024`, `power(exp=3, base=5)` → `125`",
           ["default_args", "operator"], 1,
           '''
            def power(base, exp____):
                return base ____ exp
           ''',
           [t("t1", args=[3], ret=9, desc="exp 생략"), t("t2", args=[2, 10], ret=1024, desc="exp 지정"),
            t("h1", kwargs={"exp": 3, "base": 5}, ret=125), t("h2", args=[7, 0], ret=1)],
           ["매개변수 이름 뒤에 `=기본값`을 붙이면 생략할 수 있게 됩니다.", "거듭제곱 연산자는 별표 두 개입니다."],
           '''
            def power(base, exp=2):
                return base ** exp
           ''', mode="function", name="power"),
        ex("d22_code_1", "coding", "가격 표시",
           "금액을 보기 좋은 문자열로 **반환**하는 `format_price(amount, currency=\"원\", comma=True)`를 작성하세요.\n\n"
           "- `comma`가 `True`이면 천 단위 쉼표를 넣습니다.\n- 금액이 음수이면 `ValueError`를 발생시킵니다.\n\n"
           "예: `format_price(12000)` → `\"12,000원\"`, `format_price(5000, comma=False)` → `\"5000원\"`, "
           "`format_price(12000, currency=\"달러\")` → `\"12,000달러\"`",
           ["default_args", "fstring", "formatting", "exception"], 2,
           '''
            def format_price(amount):
                # 매개변수를 더 추가하고 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), kwargs=kw or None, ret=ref_price(*a, **kw), desc=d) for a, kw, tid, d in price_cases if tid[0] == "t"]
           + [t("t4", args=[-1], raises="ValueError", desc="음수")]
           + [t(tid, args=list(a), kwargs=kw or None, ret=ref_price(*a, **kw)) for a, kw, tid, d in price_cases if tid[0] == "h"],
           ["함수 정의에 `currency`와 `comma` 매개변수를 기본값과 함께 추가하세요.",
            "음수 검사를 먼저 하고, `comma` 값에 따라 두 가지 f-string 중 하나를 반환합니다.",
            "천 단위 쉼표 서식은 `{amount:,}`입니다 (Day 20)."],
           '''
            def format_price(amount, currency="원", comma=True):
                if amount < 0:
                    raise ValueError("금액은 0 이상이어야 합니다")
                if comma:
                    return f"{amount:,}{currency}"
                return f"{amount}{currency}"
           ''', mode="function", name="format_price", checks={"required_syntax": ["def", "if", "fstring"], "max_lines": 10}),
    ])

# ====================================================================== Day 23
stats_cases = [((1, 2, 3), "t1", "세 수"), ((10,), "t2", "한 수"), ((2.5, 3.5), "h1", ""), ((-4, 4, 0, 8), "h2", "")]
day23 = lesson(
    23, "가변 인자와 여러 값 반환", W, ["variadic_args", "tuple", "unpacking", "function"],
    ["*args로 개수가 정해지지 않은 인자를 받을 수 있다.", "**kwargs와 인자 풀기(*리스트)를 이해하고 여러 값을 반환할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 기본값과 키워드 인자로 함수를 유연하게 만들었습니다.",
            "quiz": [quiz("d23_review_q1", "`def f(a, b=1): return a + b`일 때 `f(b=5, a=2)`는?", ["3", "6", "7", "오류"], 2,
                          "키워드 인자는 순서와 상관없이 이름으로 전달됩니다. 2 + 5 = 7.")]},
    concept={"title": "개수가 정해지지 않은 인자", "blocks": [
        text("매개변수 앞에 `*`를 붙이면 넘어온 위치 인자를 모두 **튜플**로 모아 받습니다. 관례적으로 `*args`라고 씁니다."),
        code('''
            def total(*numbers):
                print(numbers)
                return sum(numbers)

            print(total(1, 2, 3))
            print(total())
        ''', lines((1, 2, 3), 6, (), 0)),
        text("`**`를 붙이면 키워드 인자를 **딕셔너리**로 모아 받습니다(`**kwargs`). 반대로 호출할 때 `*리스트`를 쓰면 리스트를 낱개 인자로 풀어서 넘깁니다."),
        code('''
            def profile(name, **info):
                print(name, info)

            profile("민준", age=20, city="서울")

            def min_max(*values):
                return min(values), max(values)

            nums = [4, 9, 1]
            low, high = min_max(*nums)
            print(low, high)
        ''', lines("민준 {'age': 20, 'city': '서울'}", "1 9")),
        tip("`return a, b`는 튜플 `(a, b)` 하나를 돌려주는 것이고, 받는 쪽에서 `x, y = 함수()`로 나눠 받습니다(Day 12의 언패킹)."),
    ]},
    fill_intro="몇 개든 받을 수 있는 평균 함수를 완성하세요.",
    coding_intro="가변 인자로 받고, 여러 값을 한 번에 돌려줍니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`def f(*args)`: 위치 인자를 튜플로 모은다.",
        "`def f(**kwargs)`: 키워드 인자를 딕셔너리로 모은다.",
        "호출할 때 `f(*리스트)`는 리스트를 풀어서 전달한다.",
        "`return a, b`는 튜플을 돌려주고 `x, y = f()`로 받는다."],
        "quiz": [
            quiz("d23_summary_q1", "`def f(*a): return len(a)`일 때 `f(1, 2, 3)`은?", ["1", "3", "6", "오류"], 1, "`a`는 `(1, 2, 3)` 튜플입니다."),
            quiz("d23_summary_q2", "`def g(**k): return k`일 때 `g(x=1)`의 결과는?", ["`(1,)`", "`{'x': 1}`", "`['x']`", "`1`"], 1,
                 "키워드 인자가 딕셔너리로 모입니다.")]},
    exercises=[
        ex("d23_fill_1", "fill_blank", "몇 개든 평균",
           "점수를 몇 개든 받아 평균을 **반환**하세요. 아무것도 받지 않으면 `0`을 반환합니다.\n\n예: `average(80, 90)` → `85.0`, `average()` → `0`",
           ["variadic_args"], 1,
           '''
            def average(____scores):
                if len(scores) == 0:
                    return 0
                return sum(scores) / ____(scores)
           ''',
           [t("t1", args=[80, 90], ret=85.0, desc="두 점수"), t("t2", args=[], ret=0, desc="인자 없음"),
            t("h1", args=[100], ret=100.0), t("h2", args=[70, 80, 95], ret=(70 + 80 + 95) / 3, compare={"mode": "float", "tol": 1e-9})],
           ["인자를 튜플로 모아 받으려면 매개변수 앞에 기호 하나를 붙입니다.", "개수를 세는 내장 함수로 나누면 평균입니다."],
           '''
            def average(*scores):
                if len(scores) == 0:
                    return 0
                return sum(scores) / len(scores)
           ''', mode="function", name="average"),
        ex("d23_code_1", "coding", "개수·합계·평균 한 번에",
           "숫자를 몇 개든 받아 **(개수, 합계, 평균)** 세 값을 반환하는 `stats(*nums)`를 작성하세요. 숫자가 하나도 없으면 `ValueError`를 발생시킵니다.\n\n"
           "예: `count, total, avg = stats(1, 2, 3)` → `3, 6, 2.0`",
           ["variadic_args", "tuple", "exception"], 2,
           '''
            def stats(nums):
                # 매개변수를 고치고 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_stats(*a), compare={"mode": "float", "tol": 1e-9}, desc=d) for a, tid, d in stats_cases if tid[0] == "t"]
           + [t("t3", args=[], raises="ValueError", desc="인자 없음")]
           + [t(tid, args=list(a), ret=ref_stats(*a), compare={"mode": "float", "tol": 1e-9}) for a, tid, d in stats_cases if tid[0] == "h"],
           ["매개변수를 가변 인자로 바꾸세요.", "빈 튜플인지 먼저 확인합니다.", "`return 개수, 합계, 평균`처럼 쉼표로 이어 쓰면 세 값을 한 번에 돌려줍니다."],
           '''
            def stats(*nums):
                if not nums:
                    raise ValueError("숫자가 하나 이상 필요합니다")
                total = sum(nums)
                return len(nums), total, total / len(nums)
           ''', mode="function", name="stats", checks={"required_syntax": ["def", "return"], "max_lines": 8}),
    ])

# ====================================================================== Day 24
bank_cases = [["+5000", "-2000", "-4000", "+1000"], ["-100"], ["+300000", "-1", "-299999", "-1"], []]


def bank_stdin(txs):
    return lines(len(txs), *txs)


day24 = lesson(
    24, "변수의 범위", W, ["scope", "function", "return"],
    ["함수 안(지역)과 밖(전역) 변수의 차이를 설명할 수 있다.", "전역 변수 대신 매개변수와 반환값으로 데이터를 주고받을 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `*args`, `**kwargs`로 개수가 정해지지 않은 인자를 받았습니다.",
            "quiz": [quiz("d24_review_q1", "`def f(*a): return a`일 때 `f()`의 결과는?", ["`None`", "`()`", "`[]`", "오류"], 1,
                          "인자가 없으면 빈 튜플이 됩니다.")]},
    concept={"title": "변수가 사는 곳", "blocks": [
        text("함수 안에서 값을 저장한 변수는 그 함수 안에서만 존재하는 **지역 변수**입니다. 바깥의 같은 이름 변수(**전역 변수**)와는 별개입니다."),
        code('''
            x = 10

            def show():
                x = 5
                print("안:", x)

            show()
            print("밖:", x)
        ''', lines("안: 5", "밖: 10")),
        text("함수 안에서 바깥 변수를 **바꾸려고** 하면 오류가 납니다. 아래 코드는 `UnboundLocalError`를 냅니다."),
        code('''
            total = 0

            def add(n):
                total += n   # UnboundLocalError
        '''),
        text("가장 좋은 해결법은 값을 **매개변수로 받고 `return`으로 돌려주는** 것입니다. 함수가 어디서 무엇을 바꾸는지 한눈에 보입니다."),
        code('''
            def add(total, n):
                return total + n

            total = 0
            total = add(total, 3)
            total = add(total, 4)
            print(total)
        ''', lines(7)),
        tip("리스트·딕셔너리는 함수 안에서 `append` 등으로 **내용을 바꾸면** 바깥에도 반영됩니다(같은 객체를 가리키기 때문). "
            "의도한 게 아니라면 새 리스트를 만들어 반환하세요. `global` 키워드도 있지만 코드가 복잡해져 권하지 않습니다."),
    ]},
    fill_intro="원본을 바꾸지 않고 새 리스트를 만들어 반환하세요.",
    coding_intro="잔액을 전역 변수로 바꾸지 말고, 함수의 반환값으로 갱신하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "함수 안에서 저장한 변수는 지역 변수, 바깥 변수와 별개.",
        "함수 안에서 바깥 변수에 `+=` 하면 `UnboundLocalError`.",
        "데이터는 매개변수로 받고 `return`으로 돌려준다.",
        "리스트·딕셔너리를 함수 안에서 수정하면 바깥에도 반영된다."],
        "quiz": [
            quiz("d24_summary_q1", "다음 코드의 출력은?\n```python\nn = 1\ndef f():\n    n = 2\nf()\nprint(n)\n```", ["1", "2", "None", "오류"], 0,
                 "함수 안의 `n`은 지역 변수라 바깥 `n`은 그대로 1입니다."),
            quiz("d24_summary_q2", "다음 코드의 출력은?\n```python\ndef f(items):\n    items.append(9)\na = [1]\nf(a)\nprint(a)\n```",
                 ["`[1]`", "`[1, 9]`", "`[9]`", "오류"], 1, "리스트 내용 변경은 바깥에도 반영됩니다.")]},
    exercises=[
        ex("d24_fill_1", "fill_blank", "보너스 점수 (원본 유지)",
           "점수 리스트와 보너스를 받아, 각 점수에 보너스를 더한 **새 리스트**를 반환하세요. 원래 리스트는 바꾸지 않습니다.\n\n"
           "예: `with_bonus([80, 90], 5)` → `[85, 95]`",
           ["scope", "list"], 1,
           '''
            def with_bonus(scores, bonus):
                result = ____
                for s in scores:
                    result.append(s ____ bonus)
                return result
           ''',
           [t("t1", args=[[80, 90], 5], ret=[85, 95], desc="기본"), t("h1", args=[[], 3], ret=[]), t("h2", args=[[0, -1], 0], ret=[0, -1])],
           ["새 리스트는 비어 있는 상태에서 시작합니다.", "각 점수에 보너스를 더하는 연산자를 쓰세요."],
           '''
            def with_bonus(scores, bonus):
                result = []
                for s in scores:
                    result.append(s + bonus)
                return result
           ''', mode="function", name="with_bonus"),
        ex("d24_code_1", "coding", "통장 거래",
           "첫째 줄에 거래 수 `n`, 다음 `n`줄에 `+5000`, `-2000`처럼 입금(+)/출금(-) 금액이 주어집니다. 잔액은 0원에서 시작합니다.\n\n"
           "- 출금 후 잔액이 음수가 되는 거래는 **거절**하고 잔액을 바꾸지 않습니다.\n"
           "- 함수 `apply(balance, amount)`를 만들어 **새 잔액과 성공 여부**를 반환하고, 그 반환값으로 잔액을 갱신하세요.\n\n"
           "**입력 예시**\n```\n" + bank_stdin(bank_cases[0]) + "```\n**출력 예시**\n```\n" + ref_bank(bank_cases[0]) + "```",
           ["scope", "function", "return", "formatting"], 2,
           '''
            def apply(balance, amount):
                # 새 잔액과 성공 여부(True/False)를 반환하세요
                pass


            n = int(input())
            balance = 0
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=bank_stdin(bank_cases[0]), out=ref_bank(bank_cases[0]), desc="거절 1건 포함")]
           + [t(f"h{i}", stdin=bank_stdin(c_), out=ref_bank(c_)) for i, c_ in enumerate(bank_cases[1:], start=1)],
           ["`int(\"+5000\")`과 `int(\"-2000\")`은 그대로 양수·음수 정수가 됩니다.",
            "`apply` 안에서는 새 잔액이 음수인지 검사해 `return balance, False` 또는 `return 새잔액, True`를 돌려줍니다.",
            "반복문에서 `balance, ok = apply(balance, amount)`로 받고, `ok`가 거짓이면 거절 횟수를 늘립니다."],
           '''
            def apply(balance, amount):
                new_balance = balance + amount
                if new_balance < 0:
                    return balance, False
                return new_balance, True


            n = int(input())
            balance = 0
            rejected = 0
            for _ in range(n):
                balance, ok = apply(balance, int(input()))
                if not ok:
                    rejected += 1
            print(f"잔액: {balance:,}원")
            print(f"거절: {rejected}건")
           ''', checks={"required_syntax": ["def", "return", "fstring"]}),
    ])

# ====================================================================== Day 25
sort_cases = [(["banana", "kiwi", "apple", "fig"], "t1", "길이·사전순"), ([], "h1", ""), (["bb", "aa", "c"], "h2", "")]
rank_cases = [({"민준": 85, "서연": 92, "지호": 78}, "t1", "기본"), ({"b": 90, "a": 90, "c": 95}, "t2", "동점"),
              ({}, "h1", ""), ({"하나": 0}, "h2", ""), ({"d": 1, "c": 2, "b": 2, "a": 1}, "h3", "")]
day25 = lesson(
    25, "lambda와 정렬 기준", W, ["lambda", "sorting", "dict", "tuple"],
    ["lambda로 짧은 함수를 만들 수 있다.", "sorted()/sort()/max()의 key로 원하는 기준을 정할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 지역·전역 변수를 구분하고 반환값으로 데이터를 주고받았습니다.",
            "quiz": [quiz("d25_review_q1", "함수 안에서 바깥 변수를 바꾸는 가장 권장되는 방법은?",
                          ["`global` 사용", "매개변수로 받고 `return`으로 돌려주기", "같은 이름으로 다시 저장", "방법이 없다"], 1,
                          "입력과 출력이 분명해져 버그가 줄어듭니다.")]},
    concept={"title": "기준을 정해 정렬하기", "blocks": [
        text("`lambda 매개변수: 식`은 이름 없는 한 줄 함수입니다. `sorted()`, `sort()`, `max()`, `min()`의 `key=`에 \"무엇을 기준으로 비교할지\" 알려 줄 때 주로 씁니다."),
        code('''
            square = lambda x: x * x
            print(square(4))
            words = ["banana", "kiwi", "apple"]
            print(sorted(words, key=len))
            print(sorted(words, key=lambda w: w[-1]))
        ''', lines(16, sorted(["banana", "kiwi", "apple"], key=len), sorted(["banana", "kiwi", "apple"], key=lambda w: w[-1]))),
        text("딕셔너리를 **값** 기준으로 정렬하려면 `items()`를 정렬하면서 `key=lambda kv: kv[1]`을 줍니다."),
        code('''
            scores = {"민준": 85, "서연": 92, "지호": 78}
            ranking = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            print(ranking)
            print(max(scores, key=scores.get))
        ''', lines(sorted({"민준": 85, "서연": 92, "지호": 78}.items(), key=lambda kv: kv[1], reverse=True), "서연")),
        text("기준이 여러 개면 **튜플**을 돌려줍니다. 앞 값이 같을 때 다음 값을 비교합니다. 숫자 앞에 `-`를 붙이면 그 기준만 내림차순이 됩니다."),
        code('''
            people = [("민준", 20), ("서연", 19), ("지호", 20)]
            people.sort(key=lambda p: (-p[1], p[0]))
            print(people)
        ''', lines(sorted([("민준", 20), ("서연", 19), ("지호", 20)], key=lambda p: (-p[1], p[0])))),
        tip("`sorted()`는 새 리스트를 돌려주고, `리스트.sort()`는 원본을 바꾸고 `None`을 돌려줍니다(Day 11). `key=len`처럼 이미 있는 함수 이름을 그대로 넘길 수도 있습니다."),
    ]},
    fill_intro="두 가지 기준(길이, 사전 순)으로 정렬하세요.",
    coding_intro="점수 내림차순, 동점이면 이름 오름차순으로 순위를 매깁니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`lambda x: 식`은 한 줄짜리 이름 없는 함수.",
        "`sorted(목록, key=기준함수)`: 기준 값으로 비교한다.",
        "여러 기준은 튜플로: `key=lambda p: (-p[1], p[0])`.",
        "`max(d, key=d.get)`은 값이 가장 큰 키."],
        "quiz": [
            quiz("d25_summary_q1", "`sorted([\"ccc\", \"a\", \"bb\"], key=len)`의 결과는?",
                 ["`['a', 'bb', 'ccc']`", "`['ccc', 'bb', 'a']`", "`['a', 'ccc', 'bb']`", "오류"], 0, "길이 1, 2, 3 순서입니다."),
            quiz("d25_summary_q2", "`(lambda a, b: a - b)(5, 2)`의 결과는?", ["3", "-3", "7", "오류"], 0, "람다를 정의하자마자 5, 2로 호출했습니다.")]},
    exercises=[
        ex("d25_fill_1", "fill_blank", "길이 먼저, 그다음 사전 순",
           "단어 리스트를 **길이가 짧은 순**, 길이가 같으면 **사전 순**으로 정렬한 새 리스트를 반환하세요.\n\n"
           "예: `[\"banana\", \"kiwi\", \"apple\", \"fig\"]` → `[\"fig\", \"kiwi\", \"apple\", \"banana\"]`",
           ["lambda", "sorting"], 1,
           '''
            def sort_words(words):
                return sorted(words, key=____ w: (len(w), ____))
           ''',
           [t(tid, args=[w], ret=sorted(w, key=lambda x: (len(x), x)), desc=d) for w, tid, d in sort_cases],
           ["이름 없는 한 줄 함수를 만드는 키워드를 쓰세요.", "튜플의 두 번째 값은 \"사전 순\" 기준, 즉 단어 자체입니다."],
           '''
            def sort_words(words):
                return sorted(words, key=lambda w: (len(w), w))
           ''', mode="function", name="sort_words"),
        ex("d25_code_1", "coding", "순위표",
           "이름 → 점수 딕셔너리를 받아 **점수 높은 순**(동점이면 이름 사전 순)으로 정렬한 **이름 리스트**를 반환하세요. `lambda`를 사용하세요.\n\n"
           "예: `{\"민준\": 85, \"서연\": 92, \"지호\": 78}` → `[\"서연\", \"민준\", \"지호\"]`",
           ["lambda", "sorting", "dict_iteration"], 2,
           '''
            def rank_students(scores):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_rank(s), desc=d) for s, tid, d in rank_cases],
           ["`scores.items()`를 정렬하면 (이름, 점수) 튜플 목록이 나옵니다.",
            "점수는 내림차순, 이름은 오름차순이므로 `key`에서 점수에만 `-`를 붙인 튜플을 만드세요.",
            "정렬된 튜플들에서 이름만 꺼내 새 리스트로 만듭니다."],
           '''
            def rank_students(scores):
                ordered = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
                names = []
                for name, _ in ordered:
                    names.append(name)
                return names
           ''', mode="function", name="rank_students", checks={"required_syntax": ["lambda"], "max_lines": 8}),
    ])

# ====================================================================== Day 26
digit_cases = [(1234, "t1", "네 자리"), (0, "t2", "0"), (9, "h1", ""), (99999, "h2", ""), (1000000, "h3", "")]
day26 = lesson(
    26, "재귀 함수", W, ["recursion", "function", "condition"],
    ["자기 자신을 호출하는 재귀 함수를 작성할 수 있다.", "종료 조건(base case)과 재귀 단계를 구분할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `lambda`와 `key=`로 원하는 기준의 정렬을 했습니다.",
            "quiz": [quiz("d26_review_q1", "점수(p[1]) 내림차순, 이름(p[0]) 오름차순 정렬 key는?",
                          ["`lambda p: (p[1], p[0])`", "`lambda p: (-p[1], p[0])`", "`lambda p: (p[0], -p[1])`", "`lambda p: -p`"], 1,
                          "내림차순으로 바꿀 숫자 기준에만 `-`를 붙입니다.")]},
    concept={"title": "자기 자신을 부르는 함수", "blocks": [
        text("**재귀 함수**는 문제를 \"조금 더 작은 같은 문제\"로 바꿔 자기 자신을 호출합니다. 반드시 더 이상 나누지 않고 바로 답을 내는 **종료 조건**이 있어야 합니다."),
        code('''
            def factorial(n):
                if n <= 1:          # 종료 조건
                    return 1
                return n * factorial(n - 1)   # 더 작은 문제

            print(factorial(5))
        ''', lines(math.factorial(5))),
        code('''
            def countdown(n):
                if n == 0:
                    print("발사!")
                    return
                print(n)
                countdown(n - 1)

            countdown(3)
        ''', lines(3, 2, 1, "발사!")),
        text("리스트도 \"첫 원소 + 나머지\"로 나누어 재귀로 처리할 수 있습니다."),
        code('''
            def total(items):
                if not items:
                    return 0
                return items[0] + total(items[1:])

            print(total([1, 2, 3, 4]))
        ''', lines(10)),
        tip("종료 조건이 없거나 영원히 도달하지 못하면 함수가 끝없이 호출되다가 `RecursionError`가 납니다(기본 한도 약 1000단계). "
            "재귀 단계마다 문제가 **반드시 작아지는지** 확인하세요."),
    ]},
    fill_intro="피보나치 수를 재귀로 구하세요. F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).",
    coding_intro="반복문 없이 재귀만으로 자릿수 합을 구합니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "재귀 = 종료 조건 + 더 작은 문제로 자기 호출.",
        "종료 조건이 없으면 `RecursionError`.",
        "리스트는 `items[0]`과 `items[1:]`로 나눠 재귀할 수 있다.",
        "재귀는 반복문으로 바꿀 수도 있다. 더 읽기 쉬운 쪽을 고른다."],
        "quiz": [
            quiz("d26_summary_q1", "`def f(n): return 0 if n == 0 else n + f(n - 1)`일 때 `f(4)`는?", ["4", "6", "10", "오류"], 2,
                 "4 + 3 + 2 + 1 + 0 = 10."),
            quiz("d26_summary_q2", "재귀 함수에 반드시 필요한 것은?", ["반복문", "전역 변수", "종료 조건", "lambda"], 2,
                 "종료 조건이 있어야 호출이 멈춥니다.")]},
    exercises=[
        ex("d26_fill_1", "fill_blank", "피보나치 수",
           "n번째 피보나치 수를 **재귀**로 반환하세요.\n\n예: `fib(0)` → `0`, `fib(1)` → `1`, `fib(10)` → `55`",
           ["recursion"], 1,
           '''
            def fib(n):
                if n ____ 1:
                    return n
                return fib(n - 1) + fib(n ____ 2)
           ''',
           [t("t1", args=[0], ret=0, desc="F(0)"), t("t2", args=[10], ret=ref_fib(10), desc="F(10)"),
            t("h1", args=[1], ret=1), t("h2", args=[2], ret=1), t("h3", args=[15], ret=ref_fib(15))],
           ["n이 0이나 1이면 n 자신이 답입니다. 이 경우를 하나의 비교식으로 쓰세요.", "두 단계 전의 피보나치 수는 n에서 얼마를 뺀 값인가요?"],
           '''
            def fib(n):
                if n <= 1:
                    return n
                return fib(n - 1) + fib(n - 2)
           ''', mode="function", name="fib"),
        ex("d26_code_1", "coding", "자릿수의 합 (재귀)",
           "0 이상의 정수 `n`의 각 자릿수를 더한 값을 **재귀**로 반환하세요. 음수이면 `ValueError`를 발생시킵니다.\n\n"
           "- `for`/`while`, `sum()`, `str()`은 사용할 수 없습니다. `n % 10`(마지막 자리)과 `n // 10`(나머지 자리)을 이용하세요.\n\n"
           "예: `sum_digits(1234)` → `10`",
           ["recursion", "operator", "exception"], 2,
           '''
            def sum_digits(n):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[n], ret=sum(map(int, str(n))), desc=d) for n, tid, d in digit_cases if tid[0] == "t"]
           + [t("t3", args=[-5], raises="ValueError", desc="음수")]
           + [t(tid, args=[n], ret=sum(map(int, str(n)))) for n, tid, d in digit_cases if tid[0] == "h"],
           ["음수 검사를 먼저 하세요. 종료 조건은 \"한 자리 수\"일 때입니다.",
            "1234 → 4 + (123의 자릿수 합)처럼 마지막 자리와 나머지로 나눕니다.",
            "마지막 자리는 `n % 10`, 나머지 자리는 `n // 10`."],
           '''
            def sum_digits(n):
                if n < 0:
                    raise ValueError("0 이상의 정수만 가능합니다")
                if n < 10:
                    return n
                return n % 10 + sum_digits(n // 10)
           ''', mode="function", name="sum_digits",
           checks={"forbidden_syntax": ["for", "while"], "forbidden_calls": ["sum", "str", "map"], "max_lines": 8}),
    ])

# ====================================================================== Day 27
random.seed(42)
rand_out = [random.randint(1, 6), random.choice(["가위", "바위", "보"])]
word_texts = [("the cat and the hat and the bat", 2, "t1", "상위 2개"), ("Hello hello HELLO world", 1, "t2", "대소문자"),
              ("one", 3, "h1", ""), ("b a c b a b", 5, "h2", ""), ("", 2, "h3", "")]
day27 = lesson(
    27, "모듈과 import", W, ["module", "function"],
    ["import로 표준 라이브러리 모듈을 불러 쓸 수 있다.", "math, random, collections, statistics의 기본 기능을 활용할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 종료 조건과 자기 호출로 재귀 함수를 만들었습니다.",
            "quiz": [quiz("d27_review_q1", "재귀 함수가 끝없이 호출되면 나는 오류는?", ["`ValueError`", "`RecursionError`", "`IndexError`", "`KeyError`"], 1,
                          "호출 깊이 한도를 넘으면 `RecursionError`가 납니다.")]},
    concept={"title": "이미 만들어진 도구 쓰기", "blocks": [
        text("**모듈**은 함수·값을 모아 둔 파이썬 파일입니다. Python에는 바로 쓸 수 있는 **표준 라이브러리** 모듈이 많습니다. `import 모듈`로 불러오고 `모듈.이름`으로 씁니다."),
        code('''
            import math
            print(math.sqrt(16))
            print(math.pi)
            print(math.floor(3.7), math.ceil(3.2))
        ''', lines(math.sqrt(16), math.pi, f"{math.floor(3.7)} {math.ceil(3.2)}")),
        text("`from 모듈 import 이름`은 이름만 가져오고, `import 모듈 as 별명`은 짧은 별명을 붙입니다. `collections.Counter`는 개수 세기를 한 줄로 해 줍니다."),
        code('''
            from collections import Counter
            import statistics as st

            c = Counter("banana")
            print(c.most_common(2))
            print(st.mean([1, 2, 3, 4]))
        ''', lines(Counter("banana").most_common(2), statistics.mean([1, 2, 3, 4]))),
        text("`random`은 무작위 값을 만듭니다. `random.seed(숫자)`로 시작값을 고정하면 매번 같은 결과가 나와 테스트하기 좋습니다."),
        code('''
            import random
            random.seed(42)
            print(random.randint(1, 6))
            print(random.choice(["가위", "바위", "보"]))
        ''', lines(*rand_out)),
        tip("내 파일 이름을 `random.py`, `math.py`처럼 표준 모듈과 같게 지으면 표준 모듈 대신 내 파일이 불러와져 이상한 오류가 납니다. 파일 이름이 겹치지 않게 주의하세요."),
    ]},
    fill_intro="`math` 모듈로 두 점 사이 거리를 구하세요.",
    coding_intro="`collections.Counter`로 가장 많이 나온 단어를 찾습니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`import math` → `math.sqrt()`, `from collections import Counter` → `Counter()`.",
        "`import statistics as st`처럼 별명을 붙일 수 있다.",
        "`Counter(목록).most_common(n)`: 많이 나온 순 상위 n개.",
        "`random.seed()`로 무작위 결과를 고정할 수 있다."],
        "quiz": [
            quiz("d27_summary_q1", "`from math import sqrt` 후 올바른 호출은?", ["`math.sqrt(9)`", "`sqrt(9)`", "`math(sqrt(9))`", "`import sqrt(9)`"], 1,
                 "이름을 직접 가져왔으므로 모듈 이름 없이 씁니다."),
            quiz("d27_summary_q2", "`Counter(\"aab\").most_common(1)`의 결과는?", ["`[('a', 2)]`", "`[('b', 1)]`", "`{'a': 2}`", "`'a'`"], 0,
                 "(값, 개수) 튜플의 리스트입니다.")]},
    exercises=[
        ex("d27_fill_1", "fill_blank", "두 점 사이 거리",
           "두 점 (x1, y1), (x2, y2) 사이의 거리를 **반환**하세요. `math` 모듈의 제곱근 함수를 쓰세요.\n\n예: `distance(0, 0, 3, 4)` → `5.0`",
           ["module", "operator"], 1,
           '''
            import ____

            def distance(x1, y1, x2, y2):
                return math.____((x2 - x1) ** 2 + (y2 - y1) ** 2)
           ''',
           [t("t1", args=[0, 0, 3, 4], ret=5.0, desc="3-4-5"), t("h1", args=[1, 1, 1, 1], ret=0.0),
            t("h2", args=[-1, 2, 2, -2], ret=math.dist((-1, 2), (2, -2)), compare={"mode": "float", "tol": 1e-9}),
            t("h3", args=[0, 0, 1, 1], ret=math.sqrt(2), compare={"mode": "float", "tol": 1e-9})],
           ["수학 함수가 모여 있는 표준 모듈의 이름을 쓰세요.", "제곱근(square root)을 구하는 함수 이름은 네 글자입니다."],
           '''
            import math

            def distance(x1, y1, x2, y2):
                return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
           ''', mode="function", name="distance"),
        ex("d27_code_1", "coding", "자주 나온 단어",
           "문장과 개수 `n`을 받아, 소문자로 바꾼 단어들 중 **가장 많이 나온 n개**를 `[단어, 횟수]` 리스트로 반환하세요. "
           "횟수가 같으면 먼저 등장한 단어가 앞에 옵니다. `collections.Counter`를 사용하세요.\n\n"
           "예: `top_words(\"the cat and the hat and the bat\", 2)` → `[[\"the\", 3], [\"and\", 2]]`",
           ["module", "dict", "string_parsing"], 2,
           '''
            def top_words(text, n):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s, n], ret=ref_top_words(s, n), desc=d) for s, n, tid, d in word_texts],
           ["`collections` 모듈에서 `Counter`만 가져오는 `from … import …` 형태를 쓰세요.",
            "`text.lower().split()`으로 단어 목록을 만든 뒤 `Counter`에 넣습니다.",
            "`most_common(n)`이 원하는 순서의 (단어, 횟수) 목록을 줍니다. 튜플은 채점 시 리스트와 같게 비교됩니다."],
           '''
            from collections import Counter

            def top_words(text, n):
                counts = Counter(text.lower().split())
                return counts.most_common(n)
           ''', mode="function", name="top_words", checks={"required_syntax": ["import"], "max_lines": 8}),
    ])

# ====================================================================== Day 28 (cumulative review)
page_cases = [((list(range(1, 11)), 1), {}, "t1", "1쪽"), ((list(range(1, 11)), 4), {}, "t2", "마지막 쪽"),
              ((list(range(1, 11)), 2), {"size": 5}, "h1", ""), ((["a", "b"], 3), {}, "h2", ""), (([], 1), {}, "h3", "")]
rank_rows = [[("민준", 85), ("서연", 92), ("지호", 85), ("하나", 70)], [("a", 50)], [("c", 10), ("b", 10), ("a", 10)],
             [("d", 1), ("c", 2), ("b", 3), ("a", 3), ("e", 2)]]
flat_cases = [([1, [2, [3, 4]], 5], "t1", "중첩"), ([], "t2", "빈 리스트"), ([[[]]], "h1", ""), ([["a", ["b"]], "c", [["d"]]], "h2", "")]


def rows_stdin(rows):
    return lines(len(rows), *[f"{n} {s}" for n, s in rows])


day28 = lesson(
    28, "4주차 누적 복습", W, ["default_args", "variadic_args", "scope", "lambda", "recursion", "module", "sorting"],
    ["함수 기법(기본값, 가변 인자, lambda, 재귀)과 모듈을 조합할 수 있다.", "공동 순위 같은 정렬 문제를 해결할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 22 | 기본값·키워드 인자 | `def f(a, b=1)`, `f(b=2, a=1)` |\n"
        "| 23 | 가변 인자 | `*args` 튜플, `**kwargs` 딕셔너리, `f(*리스트)` |\n"
        "| 24 | 변수 범위 | 지역 vs 전역, 반환값으로 주고받기 |\n"
        "| 25 | lambda·정렬 | `key=lambda p: (-p[1], p[0])` |\n"
        "| 26 | 재귀 | 종료 조건 + 더 작은 문제 |\n"
        "| 27 | 모듈 | `math`, `random`, `Counter`, `statistics` |"),
        "quiz": [
            quiz("d28_review_q1", "`def f(*a, sep=\"-\"): return sep.join(a)`일 때 `f(\"x\", \"y\")`는?", ["`x y`", "`x-y`", "`xy`", "오류"], 1,
                 "`a`는 `(\"x\", \"y\")`이고 기본 구분자는 `-`입니다."),
            quiz("d28_review_q2", "`max([\"aa\", \"b\", \"ccc\"], key=len)`의 결과는?", ["`\"aa\"`", "`\"b\"`", "`\"ccc\"`", "3"], 2,
                 "길이가 가장 긴 원소를 돌려줍니다.")]},
    concept={"title": "공동 순위 매기기", "blocks": [
        text("시험 성적처럼 **동점자는 같은 순위**(1, 2, 2, 4…)를 주려면, 정렬한 뒤 \"앞 사람과 점수가 다를 때만 순위를 현재 위치로 바꾸는\" 방법을 씁니다."),
        code('''
            rows = [("민준", 85), ("서연", 92), ("지호", 85)]
            ordered = sorted(rows, key=lambda r: (-r[1], r[0]))
            rank = 0
            prev = None
            for i, (name, score) in enumerate(ordered, start=1):
                if score != prev:
                    rank = i
                    prev = score
                print(rank, name, score)
        ''', lines("1 서연 92", "2 민준 85", "2 지호 85")),
        tip("`enumerate(목록, start=1)`은 번호를 1부터 셉니다(Day 13). 위 코드는 정렬(lambda), 반복, 조건을 조합한 예입니다."),
    ]},
    fill_intro="기본값 매개변수와 슬라이싱으로 페이지를 나눠 보세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제(재귀)는 **도전 문제**(선택)입니다.",
    summary={"title": "4주차 마무리", "points": [
        "기본값·키워드 인자로 함수를 유연하게, `*args`로 개수 제한 없이.",
        "데이터는 매개변수와 반환값으로 주고받는다.",
        "정렬 기준은 `key=lambda`, 여러 기준은 튜플.",
        "다음 주에는 예외 처리와 파일 입출력, 그리고 미니 프로젝트를 한다."],
        "quiz": [
            quiz("d28_summary_q1", "점수 [90, 80, 80, 70]의 공동 순위는?", ["1, 2, 3, 4", "1, 2, 2, 3", "1, 2, 2, 4", "1, 1, 2, 3"], 2,
                 "동점은 같은 순위를 받고, 다음 순위는 사람 수만큼 건너뜁니다."),
            quiz("d28_summary_q2", "`import random as r` 후 올바른 호출은?", ["`random.randint(1, 3)`", "`r.randint(1, 3)`", "`randint(1, 3)`", "`r(1, 3)`"], 1,
                 "별명으로 불러왔으니 `r.`을 씁니다.")]},
    is_review=True,
    exercises=[
        ex("d28_fill_1", "fill_blank", "페이지 나누기",
           "목록에서 `page`번째 쪽(1부터 시작)에 해당하는 항목들을 반환하세요. 한 쪽의 크기는 `size`이고 기본값은 3입니다.\n\n"
           "예: `paginate([1, 2, …, 10], 1)` → `[1, 2, 3]`, `paginate([1, 2, …, 10], 4)` → `[10]`",
           ["default_args", "list"], 2,
           '''
            def paginate(items, page, size____):
                start = (page - 1) * size
                return items[start:start ____ size]
           ''',
           [t(tid, args=list(a), kwargs=kw or None, ret=a[0][(a[1] - 1) * kw.get("size", 3):(a[1] - 1) * kw.get("size", 3) + kw.get("size", 3)], desc=d)
            for a, kw, tid, d in page_cases],
           ["매개변수에 기본값 3을 주는 문법을 떠올려 보세요.", "끝 위치는 시작 위치에서 한 쪽 크기만큼 더한 곳입니다."],
           '''
            def paginate(items, page, size=3):
                start = (page - 1) * size
                return items[start:start + size]
           ''', mode="function", name="paginate"),
        ex("d28_code_1", "coding", "공동 순위표",
           "첫째 줄에 학생 수 `n`, 다음 `n`줄에 `이름 점수`가 주어집니다. 점수 높은 순(동점이면 이름 사전 순)으로 정렬해 "
           "`순위. 이름 점수` 형식으로 출력하세요. **동점자는 같은 순위**이고 다음 순위는 그만큼 건너뜁니다.\n\n"
           "**입력 예시**\n```\n" + rows_stdin(rank_rows[0]) + "```\n**출력 예시**\n```\n" + ref_ranking(rank_rows[0]) + "```",
           ["lambda", "sorting", "enumerate_zip", "fstring"], 3,
           '''
            n = int(input())
            rows = []
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=rows_stdin(rank_rows[0]), out=ref_ranking(rank_rows[0]), desc="동점 포함")]
           + [t(f"h{i}", stdin=rows_stdin(r), out=ref_ranking(r)) for i, r in enumerate(rank_rows[1:], start=1)],
           ["각 줄을 `(이름, 정수 점수)` 튜플로 만들어 리스트에 모으세요.",
            "정렬 key는 Day 25에서 배운 `(-점수, 이름)` 튜플입니다.",
            "개념 설명의 공동 순위 코드처럼 앞 사람과 점수가 다를 때만 순위를 현재 번호로 바꿉니다."],
           '''
            n = int(input())
            rows = []
            for _ in range(n):
                name, score = input().split()
                rows.append((name, int(score)))
            ordered = sorted(rows, key=lambda r: (-r[1], r[0]))
            rank = 0
            prev = None
            for i, (name, score) in enumerate(ordered, start=1):
                if score != prev:
                    rank = i
                    prev = score
                print(f"{rank}. {name} {score}")
           ''', checks={"required_syntax": ["lambda", "for"]}),
        ex("d28_code_2", "coding", "[도전] 리스트 펼치기",
           "리스트가 몇 겹으로 중첩되어 있든 모든 원소를 순서대로 한 줄로 펼친 리스트를 **재귀**로 반환하세요.\n\n"
           "예: `flatten([1, [2, [3, 4]], 5])` → `[1, 2, 3, 4, 5]`\n\n원소가 리스트인지는 `isinstance(x, list)`로 확인할 수 있습니다.",
           ["recursion", "list"], 3,
           '''
            def flatten(items):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[x], ret=ref_flatten(x), desc=d) for x, tid, d in flat_cases],
           ["결과 리스트를 만들고 원소를 하나씩 확인하세요.",
            "원소가 리스트이면 그 원소를 다시 `flatten` 한 결과를 결과 리스트에 이어 붙입니다(`extend`).",
            "리스트가 아니면 그대로 `append` 합니다."],
           '''
            def flatten(items):
                result = []
                for x in items:
                    if isinstance(x, list):
                        result.extend(flatten(x))
                    else:
                        result.append(x)
                return result
           ''', mode="function", name="flatten", checks={"required_syntax": ["def", "for"]}, required=False),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day22, day23, day24, day25, day26, day27, day28])
