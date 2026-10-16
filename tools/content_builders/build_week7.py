"""Week 7 (Day 43-49): 컴프리헨션, 이터레이터, 제너레이터, 클로저, 데코레이터."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import code, ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402

W, ST = 7, "advanced_data"


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


# ---------------------------------------------------------------- references

def ref_transpose(m):
    return [list(r) for r in zip(*m)] if m else []


def ref_invert(d):
    out = {}
    for k, v in d.items():
        out.setdefault(v, []).append(k)
    return {v: sorted(ks) for v, ks in out.items()}


def ref_fib_iter(limit):
    out, a, b = [], 0, 1
    while a <= limit:
        out.append(a)
        a, b = b, a + b
    return out


def ref_chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def ref_accumulate(start, xs):
    out, total = [], start
    for x in xs:
        total += x
        out.append(total)
    return out


def ref_validate(args):
    if any(a < 0 for a in args):
        raise ValueError
    return sum(args)


def ref_pipeline(rows, min_score):
    parsed = []
    for r in rows:
        parts = r.split(":")
        if len(parts) != 2 or not parts[1].strip().isdigit():
            continue
        parsed.append((parts[0].strip(), int(parts[1])))
    passed = sorted({n.upper() for n, s in parsed if s >= min_score})
    return {"count": len(parsed), "passed": passed, "average": round(sum(s for _, s in parsed) / len(parsed), 1) if parsed else 0}


def fib_memo_calls(n):
    return n + 1  # each fib(k) for k=0..n computed once with memoization


# ====================================================================== Day 43
tr_cases = [([[1, 2, 3], [4, 5, 6]], "t1", "2×3"), ([[1]], "h1", ""), ([[1, 2], [3, 4], [5, 6]], "h2", ""), ([], "h3", "")]
day43 = L(
    43, "리스트 컴프리헨션", W, ["comprehension", "list"],
    ["for문과 append로 만들던 리스트를 한 줄 컴프리헨션으로 쓸 수 있다.", "조건(if)과 중첩 for가 있는 컴프리헨션을 읽고 쓸 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "6주차에는 클래스로 데이터와 동작을 묶었습니다. 이번 주는 **더 파이썬다운 코드**를 배웁니다. "
        "첫 번째는 리스트를 만드는 가장 흔한 패턴(빈 리스트 → for → append)을 한 줄로 줄이는 **컴프리헨션**입니다."),
        "quiz": [quiz("d43_review_q1", "`@dataclass`가 자동으로 만들어 주는 메서드가 **아닌** 것은?", ["`__init__`", "`__repr__`", "`__eq__`", "`__add__`"], 3, "")]},
    concept={"title": "리스트를 한 줄로 만들기", "blocks": [
        text("`[식 for 변수 in 반복가능 if 조건]` 형태입니다. 왼쪽부터 \"무엇을 담을지 → 어디서 꺼낼지 → 어떤 것만\" 순서로 읽습니다."),
        code('''
            squares = []
            for x in range(5):
                squares.append(x * x)
            print(squares)

            print([x * x for x in range(5)])
            print([x for x in range(10) if x % 2 == 0])
            words = ["apple", "kiwi", "banana"]
            print([w.upper() for w in words if len(w) > 4])
        ''', lines([0, 1, 4, 9, 16], [0, 1, 4, 9, 16], [0, 2, 4, 6, 8], ["APPLE", "BANANA"])),
        text("for를 두 번 쓰면 중첩 반복입니다. 앞의 for가 바깥 반복이에요."),
        code('''
            grid = [[1, 2], [3, 4], [5, 6]]
            print([x for row in grid for x in row])
            print([[x * 10 for x in row] for row in grid])
            print([(i, j) for i in range(2) for j in range(2)])
        ''', lines([1, 2, 3, 4, 5, 6], [[10, 20], [30, 40], [50, 60]], [(0, 0), (0, 1), (1, 0), (1, 1)])),
        tip("컴프리헨션이 한 줄에 다 안 들어올 만큼 복잡해지면 평범한 for문이 더 읽기 좋습니다. **짧고 명확할 때** 쓰세요."),
    ]},
    fill_intro="조건이 있는 컴프리헨션을 완성하세요.",
    coding_intro="`for` 문(statement) 없이 컴프리헨션만으로 행렬을 뒤집으세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`[식 for x in 목록]`: 변환.",
        "`[식 for x in 목록 if 조건]`: 거르기 + 변환.",
        "`[x for row in grid for x in row]`: 중첩 펼치기.",
        "복잡하면 일반 for문이 낫다."],
        "quiz": [
            quiz("d43_summary_q1", "`[n * 2 for n in [1, 2, 3] if n != 2]`의 결과는?", ["`[2, 4, 6]`", "`[2, 6]`", "`[1, 3]`", "`[4]`"], 1, ""),
            quiz("d43_summary_q2", "`[c for c in \"abc\"]`의 결과는?", ["`\"abc\"`", "`['abc']`", "`['a', 'b', 'c']`", "오류"], 2, "")]},
    exercises=[
        ex("d43_fill_1", "fill_blank", "긴 단어만 대문자로",
           "단어 리스트에서 **3글자 이상**인 단어만 대문자로 바꾼 리스트를 반환하세요.\n\n예: `[\"hi\", \"cat\", \"apple\"]` → `[\"CAT\", \"APPLE\"]`",
           ["comprehension"], 1,
           '''
            def long_upper(words):
                return [w.upper() ____ w in words ____ len(w) >= 3]
           ''',
           [t("t1", args=[["hi", "cat", "apple"]], ret=["CAT", "APPLE"], desc="기본"), t("h1", args=[[]], ret=[]), t("h2", args=[["a", "bb"]], ret=[])],
           ["컴프리헨션에서 반복을 나타내는 키워드입니다.", "조건을 붙이는 키워드입니다."],
           '''
            def long_upper(words):
                return [w.upper() for w in words if len(w) >= 3]
           ''', mode="function", name="long_upper"),
        ex("d43_code_1", "coding", "행렬 전치",
           "2차원 리스트(행렬)의 행과 열을 바꾼 **전치 행렬**을 반환하세요. 빈 리스트면 빈 리스트를 반환합니다.\n\n"
           "- `for` 문은 쓸 수 없고 컴프리헨션을 사용합니다.\n\n예: `[[1, 2, 3], [4, 5, 6]]` → `[[1, 4], [2, 5], [3, 6]]`",
           ["comprehension", "nested_list"], 2,
           '''
            def transpose(matrix):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[m], ret=ref_transpose(m), desc=d) for m, tid, d in tr_cases],
           ["결과의 c번째 행은 원래 각 행의 c번째 값들입니다.", "바깥 컴프리헨션은 열 번호 `c`를, 안쪽은 각 행 `row`에서 `row[c]`를 꺼냅니다.",
            "열 개수는 `len(matrix[0])`입니다. 빈 행렬은 먼저 처리하세요."],
           '''
            def transpose(matrix):
                if not matrix:
                    return []
                return [[row[c] for row in matrix] for c in range(len(matrix[0]))]
           ''', mode="function", name="transpose", checks={"required_syntax": ["list_comp"], "forbidden_syntax": ["for"]}),
    ])

# ====================================================================== Day 44
inv_cases = [({"민준": "A", "서연": "B", "지호": "A"}, "t1", "기본"), ({}, "h1", ""), ({"z": "x", "a": "x", "m": "y"}, "h2", "")]
day44 = L(
    44, "딕셔너리·집합 컴프리헨션과 조건부 표현식", W, ["comprehension", "conditional_expr", "dict", "set"],
    ["딕셔너리·집합 컴프리헨션을 쓸 수 있다.", "`값1 if 조건 else 값2` 조건부 표현식을 쓸 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `[식 for x in 목록 if 조건]`으로 리스트를 만들었습니다.",
            "quiz": [quiz("d44_review_q1", "`[x for x in range(6) if x % 3 == 0]`의 결과는?", ["`[0, 3]`", "`[3]`", "`[0, 3, 6]`", "`[1, 2, 4, 5]`"], 0, "")]},
    concept={"title": "다른 모음도 한 줄로", "blocks": [
        text("중괄호에 `키: 값`을 쓰면 **딕셔너리 컴프리헨션**, 값만 쓰면 **집합 컴프리헨션**입니다."),
        code('''
            words = ["apple", "kiwi", "banana"]
            print({w: len(w) for w in words})
            scores = {"민준": 85, "서연": 55, "지호": 72}
            print({k: v for k, v in scores.items() if v >= 60})
            print(sorted({n % 3 for n in range(10)}))
        ''', lines({"apple": 5, "kiwi": 4, "banana": 6}, {"민준": 85, "지호": 72}, [0, 1, 2])),
        text("**조건부 표현식** `A if 조건 else B`는 조건이 참이면 A, 거짓이면 B가 되는 **값**입니다. if문과 달리 식 안에 넣을 수 있습니다."),
        code('''
            score = 72
            print("합격" if score >= 60 else "불합격")
            scores = {"민준": 85, "서연": 55}
            print({k: ("합격" if v >= 60 else "불합격") for k, v in scores.items()})
        ''', lines("합격", {"민준": "합격", "서연": "불합격"})),
        tip("`{}`만 쓰면 빈 **딕셔너리**입니다. 빈 집합은 `set()`(Day 18)."),
    ]},
    fill_intro="이름별 합격 여부 딕셔너리를 한 줄로 만드세요.",
    coding_intro="딕셔너리를 뒤집어 값별로 키를 모으세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`{k: v for ...}` 딕셔너리, `{x for ...}` 집합 컴프리헨션.",
        "`A if 조건 else B`는 값이 되는 조건식.",
        "컴프리헨션 안에도 조건부 표현식을 쓸 수 있다.",
        "빈 집합은 `set()`."],
        "quiz": [
            quiz("d44_summary_q1", "`{x: x * x for x in range(3)}`의 결과는?", ["`{0: 0, 1: 1, 2: 4}`", "`[0, 1, 4]`", "`{0, 1, 4}`", "오류"], 0, ""),
            quiz("d44_summary_q2", "`\"짝\" if 7 % 2 == 0 else \"홀\"`의 값은?", ["`\"짝\"`", "`\"홀\"`", "`True`", "오류"], 1, "")]},
    exercises=[
        ex("d44_fill_1", "fill_blank", "합격 여부 표",
           "이름 → 점수 딕셔너리를 받아 이름 → `\"pass\"`/`\"fail\"`(60점 이상이 pass) 딕셔너리를 반환하세요.",
           ["comprehension", "conditional_expr"], 1,
           '''
            def pass_fail(scores):
                return {name: ("pass" if s >= 60 ____ "fail") for name, s in scores.____()}
           ''',
           [t("t1", args=[{"a": 60, "b": 59}], ret={"a": "pass", "b": "fail"}, desc="경계값"), t("h1", args=[{}], ret={}), t("h2", args=[{"x": 100}], ret={"x": "pass"})],
           ["조건부 표현식의 \"아니면\" 부분 키워드입니다.", "(키, 값) 쌍으로 순회하는 딕셔너리 메서드입니다."],
           '''
            def pass_fail(scores):
                return {name: ("pass" if s >= 60 else "fail") for name, s in scores.items()}
           ''', mode="function", name="pass_fail"),
        ex("d44_code_1", "coding", "딕셔너리 뒤집기",
           "키 → 값 딕셔너리를 받아 **값 → 그 값을 가진 키들의 정렬된 리스트** 딕셔너리를 반환하세요. 딕셔너리 컴프리헨션을 사용하세요.\n\n"
           "예: `{\"민준\": \"A\", \"서연\": \"B\", \"지호\": \"A\"}` → `{\"A\": [\"민준\", \"지호\"], \"B\": [\"서연\"]}`",
           ["comprehension", "dict", "set"], 2,
           '''
            def invert(d):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[d_], ret=ref_invert(d_), desc=ds) for d_, tid, ds in inv_cases],
           ["결과의 키는 원래 값들입니다. 중복 없는 값 목록은 `set(d.values())`로 얻을 수 있어요.",
            "각 값 `v`에 대해 `[k for k in d if d[k] == v]`를 정렬하면 됩니다."],
           '''
            def invert(d):
                return {v: sorted([k for k in d if d[k] == v]) for v in set(d.values())}
           ''', mode="function", name="invert", checks={"required_syntax": ["dict_comp"]}),
    ])

# ====================================================================== Day 45
fib_limits = [(10, "t1", "10 이하"), (0, "t2", "0"), (1, "h1", ""), (100, "h2", "")]
day45 = L(
    45, "이터레이터", W, ["iterator", "class", "dunder"],
    ["iter()와 next()로 반복의 원리를 설명할 수 있다.", "__iter__와 __next__로 직접 반복 가능한 객체를 만들 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 딕셔너리·집합 컴프리헨션과 조건부 표현식을 배웠습니다.",
            "quiz": [quiz("d45_review_q1", "빈 집합을 만드는 방법은?", ["`{}`", "`set()`", "`{,}`", "`[]`"], 1, "")]},
    concept={"title": "for문은 어떻게 동작할까", "blocks": [
        text("`for x in 목록:`은 내부에서 `iter(목록)`으로 **이터레이터**를 얻고, `next()`로 값을 하나씩 꺼내다가 `StopIteration` 예외가 나면 멈춥니다."),
        code('''
            it = iter([10, 20])
            print(next(it))
            print(next(it))
            try:
                next(it)
            except StopIteration:
                print("끝")
        ''', lines(10, 20, "끝")),
        text("클래스에 `__iter__`(이터레이터 자신을 돌려줌)와 `__next__`(다음 값 또는 `StopIteration`)를 만들면 직접 for문에 쓸 수 있습니다."),
        code('''
            class Countdown:
                def __init__(self, start):
                    self.current = start

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.current <= 0:
                        raise StopIteration
                    value = self.current
                    self.current -= 1
                    return value

            print(list(Countdown(3)))
            for n in Countdown(2):
                print(n)
        ''', lines([3, 2, 1], 2, 1)),
        tip("이터레이터는 **한 번 다 쓰면 끝**입니다. 같은 이터레이터로 두 번째 for문을 돌리면 아무것도 나오지 않아요. 리스트는 for를 돌 때마다 새 이터레이터를 만들기 때문에 여러 번 돌 수 있습니다."),
    ]},
    fill_intro="카운트다운 이터레이터의 빈칸을 채우세요.",
    coding_intro="피보나치 수를 차례로 내놓는 이터레이터 클래스를 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`iter(x)`로 이터레이터, `next(it)`로 다음 값.",
        "값이 없으면 `StopIteration` → for문이 멈춤.",
        "`__iter__`는 `self`, `__next__`는 다음 값 반환.",
        "이터레이터는 한 번 쓰면 소진된다."],
        "quiz": [
            quiz("d45_summary_q1", "`__next__`에서 더 줄 값이 없을 때 해야 할 일은?", ["`return None`", "`raise StopIteration`", "`break`", "`return False`"], 1, ""),
            quiz("d45_summary_q2", "`it = iter([1])` 후 `next(it)`를 두 번 부르면 두 번째는?", ["1", "`None`", "`StopIteration` 예외", "0"], 2, "")]},
    exercises=[
        ex("d45_fill_1", "fill_blank", "카운트다운",
           "`Countdown(n)`이 n부터 1까지 내려가며 값을 내놓도록 빈칸을 채우세요.",
           ["iterator"], 1,
           '''
            class Countdown:
                def __init__(self, start):
                    self.current = start

                def __iter__(self):
                    return ____

                def __next__(self):
                    if self.current <= 0:
                        raise ____
                    value = self.current
                    self.current -= 1
                    return value


            def check(n):
                return list(Countdown(n))
           ''',
           [t("t1", args=[3], ret=[3, 2, 1], desc="3"), t("h1", args=[0], ret=[]), t("h2", args=[1], ret=[1])],
           ["이터레이터는 자기 자신을 돌려줍니다.", "반복이 끝났음을 알리는 예외 이름입니다."],
           '''
            class Countdown:
                def __init__(self, start):
                    self.current = start

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.current <= 0:
                        raise StopIteration
                    value = self.current
                    self.current -= 1
                    return value


            def check(n):
                return list(Countdown(n))
           ''', mode="function", name="check"),
        ex("d45_code_1", "coding", "피보나치 이터레이터",
           "`FibUpTo(limit)` 이터레이터 클래스를 만드세요. 0, 1, 1, 2, 3, 5, … 피보나치 수를 **limit 이하**까지 차례로 내놓습니다.\n\n"
           "예: `list(FibUpTo(10))` → `[0, 1, 1, 2, 3, 5, 8]`. `check`는 채점용입니다.",
           ["iterator", "class"], 2,
           '''
            # 여기에 FibUpTo 클래스를 작성하세요


            def check(limit):
                return list(FibUpTo(limit))
           ''',
           [t(tid, args=[n], ret=ref_fib_iter(n), desc=d) for n, tid, d in fib_limits],
           ["`__init__`에서 limit과 현재 두 수(`a=0`, `b=1`)를 저장하세요.",
            "`__next__`에서 `a`가 limit을 넘으면 `StopIteration`, 아니면 `a`를 돌려주기 전에 `a, b = b, a + b`로 다음 상태를 준비합니다."],
           '''
            class FibUpTo:
                def __init__(self, limit):
                    self.limit = limit
                    self.a = 0
                    self.b = 1

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.a > self.limit:
                        raise StopIteration
                    value = self.a
                    self.a, self.b = self.b, self.a + self.b
                    return value


            def check(limit):
                return list(FibUpTo(limit))
           ''', mode="function", name="check", checks={"required_syntax": ["class"]}),
    ])

# ====================================================================== Day 46
chunk_cases = [(([1, 2, 3, 4, 5], 2), "t1", "크기 2"), (([], 3), "t2", "빈 목록"), ((list("abcdef"), 3), "h1", ""), (([1], 5), "h2", "")]
day46 = L(
    46, "제너레이터", W, ["generator", "iterator", "function"],
    ["yield로 값을 하나씩 만들어 내는 제너레이터 함수를 쓸 수 있다.", "제너레이터 표현식과 지연 계산의 장점을 설명할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `__iter__`/`__next__`로 이터레이터 클래스를 만들었습니다. 오늘은 같은 일을 훨씬 짧게 하는 방법입니다.",
            "quiz": [quiz("d46_review_q1", "for문이 멈추는 신호가 되는 예외는?", ["`ValueError`", "`StopIteration`", "`IndexError`", "`KeyError`"], 1, "")]},
    concept={"title": "값을 필요할 때 하나씩", "blocks": [
        text("함수 안에 `yield`가 있으면 **제너레이터 함수**가 됩니다. 호출하면 바로 실행되지 않고 제너레이터를 돌려주며, `next()`가 올 때마다 다음 `yield`까지 실행하고 멈춥니다."),
        code('''
            def count_up(n):
                i = 1
                while i <= n:
                    yield i
                    i += 1

            gen = count_up(3)
            print(next(gen))
            print(list(gen))
            print(sum(count_up(100)))
        ''', lines(1, [2, 3], 5050)),
        text("괄호로 쓰는 **제너레이터 표현식**은 리스트를 만들지 않고 값을 하나씩 계산합니다. 큰 데이터에서 메모리를 아낄 수 있습니다."),
        code('''
            print(sum(x * x for x in range(10)))

            def naturals():
                n = 1
                while True:
                    yield n
                    n += 1

            for n in naturals():
                if n > 3:
                    break
                print(n)
        ''', lines(285, 1, 2, 3)),
        tip("제너레이터는 끝없는 수열도 표현할 수 있습니다(값을 미리 다 만들지 않으니까요). 다만 `list(naturals())`처럼 전부 꺼내려 하면 영원히 끝나지 않습니다."),
    ]},
    fill_intro="짝수만 내놓는 제너레이터를 완성하세요.",
    coding_intro="목록을 일정 크기로 잘라 내놓는 제너레이터를 만드세요. `yield`를 사용하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`yield`가 있는 함수 = 제너레이터 함수.",
        "`next()`마다 다음 `yield`까지 실행하고 멈춘다.",
        "`(식 for x in ...)` 제너레이터 표현식은 리스트를 만들지 않는다.",
        "끝없는 수열도 표현 가능(꺼내는 쪽에서 멈춰야 함)."],
        "quiz": [
            quiz("d46_summary_q1", "`def g(): yield 1; yield 2` 일 때 `list(g())`는?", ["`[1]`", "`[1, 2]`", "`2`", "제너레이터 객체"], 1, ""),
            quiz("d46_summary_q2", "`sum(x for x in range(4))`의 결과는?", ["4", "6", "10", "오류"], 1, "0+1+2+3 = 6")]},
    exercises=[
        ex("d46_fill_1", "fill_blank", "짝수 제너레이터",
           "0 이상 n 미만의 짝수를 차례로 내놓는 제너레이터를 완성하세요.",
           ["generator"], 1,
           '''
            def evens(n):
                for i in range(n):
                    if i % 2 == 0:
                        ____ i


            def check(n):
                return ____(evens(n))
           ''',
           [t("t1", args=[7], ret=[0, 2, 4, 6], desc="7"), t("h1", args=[0], ret=[]), t("h2", args=[1], ret=[0])],
           ["값을 하나 내놓고 멈추는 키워드입니다.", "제너레이터의 값을 모두 리스트로 모으는 내장 함수입니다."],
           '''
            def evens(n):
                for i in range(n):
                    if i % 2 == 0:
                        yield i


            def check(n):
                return list(evens(n))
           ''', mode="function", name="check"),
        ex("d46_code_1", "coding", "묶음 나누기",
           "리스트와 크기 `size`를 받아, 앞에서부터 `size`개씩 자른 리스트를 하나씩 **yield** 하는 제너레이터 `chunks(items, size)`를 작성하세요. 마지막 묶음은 더 짧을 수 있습니다.\n\n"
           "예: `list(chunks([1, 2, 3, 4, 5], 2))` → `[[1, 2], [3, 4], [5]]`",
           ["generator", "list"], 2,
           '''
            def chunks(items, size):
                # 여기에 코드를 작성하세요
                pass


            def check(items, size):
                return list(chunks(items, size))
           ''',
           [t(tid, args=list(a), ret=ref_chunks(*a), desc=d) for a, tid, d in chunk_cases],
           ["시작 위치를 `range(0, len(items), size)`로 건너뛰며 만드세요.", "각 시작 위치 `i`에서 `items[i:i + size]`를 yield 합니다."],
           '''
            def chunks(items, size):
                for i in range(0, len(items), size):
                    yield items[i:i + size]


            def check(items, size):
                return list(chunks(items, size))
           ''', mode="function", name="check", checks={"required_syntax": ["yield"]}),
    ])

# ====================================================================== Day 47
acc_cases = [((0, [1, 2, 3]), "t1", "0에서 시작"), ((10, []), "t2", "호출 없음"), ((-5, [5, 5]), "h1", ""), ((1.5, [0.5]), "h2", "")]
day47 = L(
    47, "일급 함수와 클로저", W, ["closure", "function", "scope"],
    ["함수를 변수에 담고 인자로 넘기고 반환할 수 있다.", "클로저와 nonlocal로 상태를 기억하는 함수를 만들 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `yield`로 값을 하나씩 만드는 제너레이터를 배웠습니다.",
            "quiz": [quiz("d47_review_q1", "제너레이터 함수를 호출하면 바로 일어나는 일은?", ["함수 본문이 끝까지 실행된다", "제너레이터 객체가 반환되고 아직 실행되지 않는다", "첫 값이 반환된다", "오류"], 1, "")]},
    concept={"title": "함수도 값이다", "blocks": [
        text("파이썬에서 함수는 숫자·문자열처럼 **값**입니다. 변수에 담고, 리스트·딕셔너리에 넣고, 다른 함수에 넘기거나 돌려줄 수 있습니다(`sorted(key=len)`도 그 예)."),
        code('''
            def shout(s):
                return s.upper() + "!"

            def whisper(s):
                return s.lower() + "..."

            styles = {"큰소리": shout, "작은소리": whisper}
            for name, f in styles.items():
                print(name, f("Hello"))

            def apply_twice(f, x):
                return f(f(x))

            print(apply_twice(lambda n: n * 3, 2))
        ''', lines("큰소리 HELLO!", "작은소리 hello...", 18)),
        text("함수 안에서 만든 함수는 바깥 함수의 변수를 기억합니다. 이것을 **클로저**라고 합니다. 기억한 변수를 바꾸려면 `nonlocal`을 씁니다."),
        code('''
            def make_multiplier(n):
                def multiply(x):
                    return x * n
                return multiply

            double = make_multiplier(2)
            print(double(5), make_multiplier(10)(3))

            def make_counter():
                count = 0
                def increase():
                    nonlocal count
                    count += 1
                    return count
                return increase

            c = make_counter()
            print(c(), c(), c())
        ''', lines("10 30", "1 2 3")),
        tip("`nonlocal` 없이 `count += 1`을 하면 Day 24에서 본 `UnboundLocalError`가 납니다. 바깥 함수의 변수임을 알려 주는 것이 `nonlocal`입니다."),
    ]},
    fill_intro="숫자를 기억하는 곱셈 함수를 만드는 함수를 완성하세요.",
    coding_intro="누적 합을 기억하는 클로저를 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "함수는 값: 변수·자료구조에 담고, 인자로 넘기고, 반환할 수 있다.",
        "안쪽 함수가 바깥 변수를 기억하면 클로저.",
        "기억한 변수를 바꿀 때는 `nonlocal`.",
        "클로저는 작은 상태를 가진 함수를 만들 때 유용하다."],
        "quiz": [
            quiz("d47_summary_q1", "`f = len` 후 `f(\"abc\")`는?", ["`len`", "3", "오류", "`\"abc\"`"], 1, "함수를 다른 이름에 담았을 뿐입니다."),
            quiz("d47_summary_q2", "클로저 안에서 바깥 변수를 바꾸려면 필요한 키워드는?", ["`global`", "`nonlocal`", "`static`", "`self`"], 1, "")]},
    exercises=[
        ex("d47_fill_1", "fill_blank", "곱셈 함수 공장",
           "`make_multiplier(n)`이 \"x에 n을 곱하는 함수\"를 반환하도록 완성하세요.",
           ["closure"], 1,
           '''
            def make_multiplier(n):
                def multiply(x):
                    return x * ____
                return ____


            def check(n, values):
                f = make_multiplier(n)
                return [f(v) for v in values]
           ''',
           [t("t1", args=[3, [1, 2]], ret=[3, 6], desc="3배"), t("h1", args=[0, [5]], ret=[0]), t("h2", args=[-1, [1, -2]], ret=[-1, 2])],
           ["안쪽 함수는 바깥 함수의 매개변수를 그대로 쓸 수 있습니다.", "함수를 호출하지 않고 함수 자체를 돌려줍니다(괄호 없이)."],
           '''
            def make_multiplier(n):
                def multiply(x):
                    return x * n
                return multiply


            def check(n, values):
                f = make_multiplier(n)
                return [f(v) for v in values]
           ''', mode="function", name="check"),
        ex("d47_code_1", "coding", "누적 합 기억하기",
           "`make_accumulator(start)`는 함수 `add(x)`를 반환합니다. `add`는 호출될 때마다 지금까지의 합(start + 지금까지 더한 값)을 반환합니다.\n\n"
           "예: `add = make_accumulator(0)` → `add(1)` 1, `add(2)` 3, `add(3)` 6",
           ["closure", "scope"], 2,
           '''
            def make_accumulator(start):
                # 여기에 코드를 작성하세요
                pass


            def check(start, values):
                add = make_accumulator(start)
                return [add(v) for v in values]
           ''',
           [t(tid, args=list(a), ret=ref_accumulate(*a), desc=d, compare={"mode": "float", "tol": 1e-9}) for a, tid, d in acc_cases],
           ["바깥 함수에 합계 변수를 두고, 안쪽 함수 `add(x)`를 정의해 반환합니다.", "안쪽 함수에서 합계를 바꾸려면 `nonlocal`이 필요합니다."],
           '''
            def make_accumulator(start):
                total = start

                def add(x):
                    nonlocal total
                    total += x
                    return total

                return add


            def check(start, values):
                add = make_accumulator(start)
                return [add(v) for v in values]
           ''', mode="function", name="check"),
    ])

# ====================================================================== Day 48
val_cases = [([1, 2, 3], "t1", "양수"), ([0], "t2", "0"), ([2, -1], "h1", ""), ([], "h2", "")]
day48 = L(
    48, "데코레이터", W, ["decorator", "closure", "variadic_args"],
    ["함수를 감싸 기능을 덧붙이는 데코레이터를 만들 수 있다.", "@ 문법과 functools.wraps를 이해한다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 함수를 값으로 다루고, 클로저로 상태를 기억하게 했습니다.",
            "quiz": [quiz("d48_review_q1", "`def outer(): def inner(): ... return inner`에서 `outer()`가 돌려주는 것은?", ["`None`", "`inner` 함수", "`inner()`의 결과", "오류"], 1, "")]},
    concept={"title": "함수에 기능 덧붙이기", "blocks": [
        text("**데코레이터**는 함수를 받아 기능을 덧붙인 새 함수를 돌려주는 함수입니다. `@데코레이터`를 함수 정의 위에 쓰면 `함수 = 데코레이터(함수)`와 같습니다. "
             "6주차의 `@property`, `@dataclass`도 데코레이터예요."),
        code('''
            def announce(func):
                def wrapper(*args, **kwargs):
                    print(f"{func.__name__} 호출")
                    result = func(*args, **kwargs)
                    print(f"결과: {result}")
                    return result
                return wrapper

            @announce
            def add(a, b):
                return a + b

            add(2, 3)
        ''', lines("add 호출", "결과: 5")),
        text("`*args, **kwargs`(Day 23)로 받으면 어떤 인자를 가진 함수도 감쌀 수 있습니다. `functools.wraps`를 쓰면 감싼 뒤에도 원래 함수 이름이 유지됩니다."),
        code('''
            from functools import wraps

            def count_calls(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    wrapper.calls += 1
                    return func(*args, **kwargs)
                wrapper.calls = 0
                return wrapper

            @count_calls
            def hello():
                return "hi"

            hello()
            hello()
            print(hello.calls, hello.__name__)
        ''', lines("2 hello")),
        tip("데코레이터 안의 `wrapper`가 원래 함수의 결과를 `return` 하지 않으면, 감싼 함수는 항상 `None`을 돌려주게 됩니다. 흔한 실수예요."),
    ]},
    fill_intro="결과를 대문자로 바꾸는 데코레이터를 완성하세요.",
    coding_intro="인자를 검사하는 데코레이터를 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "데코레이터 = 함수를 받아 감싼 함수를 돌려주는 함수.",
        "`@deco` ↔ `f = deco(f)`.",
        "`wrapper(*args, **kwargs)`로 어떤 함수든 감싼다.",
        "`return func(...)`을 잊지 말고, `@wraps(func)`로 이름 유지."],
        "quiz": [
            quiz("d48_summary_q1", "`@d` 아래 `def f(): ...`는 무엇과 같은가?", ["`d = f(d)`", "`f = d(f)`", "`f = d`", "`d(f())`"], 1, ""),
            quiz("d48_summary_q2", "wrapper가 `func(*args)`만 부르고 return하지 않으면 감싼 함수의 반환값은?", ["원래 결과", "`None`", "`wrapper`", "오류"], 1, "")]},
    exercises=[
        ex("d48_fill_1", "fill_blank", "대문자 데코레이터",
           "감싼 함수의 문자열 결과를 대문자로 바꾸는 데코레이터 `shout`을 완성하세요.",
           ["decorator"], 1,
           '''
            def shout(func):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs).upper()
                return ____


            ____shout
            def greet(name):
                return f"hello, {name}"


            def check(name):
                return greet(name)
           ''',
           [t("t1", args=["kim"], ret="HELLO, KIM", desc="기본"), t("h1", args=[""], ret="HELLO, ")],
           ["데코레이터는 안쪽 함수 자체를 돌려줍니다.", "데코레이터를 적용하는 기호입니다."],
           '''
            def shout(func):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs).upper()
                return wrapper


            @shout
            def greet(name):
                return f"hello, {name}"


            def check(name):
                return greet(name)
           ''', mode="function", name="check"),
        ex("d48_code_1", "coding", "양수 검사 데코레이터",
           "데코레이터 `positive_only`를 작성하세요. 감싼 함수에 넘어온 **위치 인자 중 하나라도 음수**이면 `ValueError`를 발생시키고, 아니면 원래 함수의 결과를 반환합니다.\n\n"
           "`total`과 `check`는 채점용입니다. 예: `check([1, 2, 3])` → `6`",
           ["decorator", "variadic_args", "exception"], 2,
           '''
            # 여기에 positive_only 데코레이터를 작성하세요


            @positive_only
            def total(*numbers):
                return sum(numbers)


            def check(values):
                return total(*values)
           ''',
           [t(tid, args=[v], ret=ref_validate(v), desc=d) for v, tid, d in val_cases if min(v, default=0) >= 0 and tid[0] == "t"]
           + [t("t3", args=[[-1]], raises="ValueError", desc="음수")]
           + [t("h1", args=[[2, -1]], raises="ValueError"), t("h2", args=[[]], ret=0)],
           ["데코레이터 함수 안에, 어떤 인자든 받을 수 있는(`*args`, `**kwargs`) 안쪽 함수를 정의하세요.",
            "`args`를 돌며 음수가 있으면 예외를 발생시키고, 마지막에는 받은 인자 그대로 원래 함수를 호출한 결과를 돌려줍니다.",
            "바깥 함수는 `wrapper`를 반환합니다."],
           '''
            def positive_only(func):
                def wrapper(*args, **kwargs):
                    for a in args:
                        if a < 0:
                            raise ValueError("음수는 허용되지 않습니다")
                    return func(*args, **kwargs)
                return wrapper


            @positive_only
            def total(*numbers):
                return sum(numbers)


            def check(values):
                return total(*values)
           ''', mode="function", name="check", checks={"required_syntax": ["def"]}),
    ])

# ====================================================================== Day 49 (review)
pipe_cases = [((["민준: 85", "서연:92", "잘못된줄", "지호: 58", "민준:70"], 60), "t1", "기본"), (([], 60), "h1", ""),
              ((["a:100", "b:x", "c:0"], 50), "h2", "")]
memo_ns = [(10, "t1", "n=10"), (30, "h1", ""), (0, "h2", "")]


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


day49 = L(
    49, "7주차 누적 복습", W, ["comprehension", "generator", "closure", "decorator", "iterator", "conditional_expr"],
    ["컴프리헨션·제너레이터·데코레이터를 조합해 데이터 처리 파이프라인을 만들 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 43 | 리스트 컴프리헨션 | `[식 for x in 목록 if 조건]` |\n"
        "| 44 | 딕셔너리·집합, 조건식 | `{k: v for ...}`, `A if 조건 else B` |\n"
        "| 45 | 이터레이터 | `iter`, `next`, `StopIteration` |\n"
        "| 46 | 제너레이터 | `yield`, `(식 for x in ...)` |\n"
        "| 47 | 클로저 | 함수는 값, `nonlocal` |\n"
        "| 48 | 데코레이터 | `@deco`, `wrapper(*args, **kwargs)` |"),
        "quiz": [
            quiz("d49_review_q1", "큰 파일을 한 줄씩 처리하며 메모리를 아끼기에 알맞은 것은?", ["리스트 컴프리헨션", "제너레이터", "딕셔너리", "튜플"], 1, ""),
            quiz("d49_review_q2", "함수 실행 결과를 저장해 두었다가 같은 인자면 바로 돌려주는 기능을 여러 함수에 붙이려면?", ["상속", "데코레이터", "property", "컴프리헨션"], 1, "")]},
    concept={"title": "파이프라인과 메모이제이션", "blocks": [
        text("**파이프라인**은 데이터가 여러 단계를 차례로 통과하는 구조입니다. 제너레이터로 단계를 이으면 중간 리스트를 만들지 않고도 처리할 수 있습니다."),
        code('''
            def read_numbers(lines):
                for line in lines:
                    if line.strip().isdigit():
                        yield int(line)

            def squares(nums):
                for n in nums:
                    yield n * n

            data = ["1", "x", "2", "3"]
            print(sum(squares(read_numbers(data))))
        ''', lines(14)),
        text("**메모이제이션**은 계산 결과를 딕셔너리에 저장해 같은 계산을 반복하지 않는 기법입니다. 데코레이터로 만들면 어떤 함수에도 붙일 수 있습니다. 표준 라이브러리 `functools.lru_cache`도 같은 일을 합니다."),
        tip("재귀 피보나치(Day 26)는 같은 값을 엄청나게 많이 다시 계산합니다. 메모이제이션을 붙이면 n=30도 즉시 끝납니다."),
    ]},
    fill_intro="제너레이터 표현식과 조건식으로 점수를 정리하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "7주차 마무리", "points": [
        "컴프리헨션으로 짧게, 제너레이터로 가볍게.",
        "함수는 값 → 클로저와 데코레이터로 기능을 조립한다.",
        "메모이제이션 = 결과 캐시.",
        "다음 주: NumPy로 숫자 데이터를 빠르게 다룬다."],
        "quiz": [
            quiz("d49_summary_q1", "`functools.lru_cache`의 역할은?", ["로그 출력", "결과 캐싱(메모이제이션)", "정렬", "예외 처리"], 1, ""),
            quiz("d49_summary_q2", "`max(len(w) for w in [\"a\", \"abc\"])`의 결과는?", ["1", "3", "`\"abc\"`", "오류"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d49_fill_1", "fill_blank", "통과/미통과 개수",
           "점수 리스트를 받아 `[통과 개수, 미통과 개수]`를 반환하세요(기준 이상이면 통과). 제너레이터 표현식을 `sum()`에 넘기세요.",
           ["generator", "conditional_expr"], 1,
           '''
            def count_pass(scores, cut):
                passed = sum(1 ____ s in scores if s >= cut)
                return [passed, ____(scores) - passed]
           ''',
           [t("t1", args=[[50, 60, 70], 60], ret=[2, 1], desc="기본"), t("h1", args=[[], 10], ret=[0, 0]), t("h2", args=[[1, 2], 3], ret=[0, 2])],
           ["제너레이터 표현식의 반복 키워드입니다.", "전체 개수를 세는 내장 함수입니다."],
           '''
            def count_pass(scores, cut):
                passed = sum(1 for s in scores if s >= cut)
                return [passed, len(scores) - passed]
           ''', mode="function", name="count_pass"),
        ex("d49_code_1", "coding", "점수 파이프라인",
           "`\"이름:점수\"` 문자열 목록과 기준 점수를 받아 딕셔너리를 반환하세요.\n\n"
           "1. 형식이 맞지 않거나(`:`로 나눈 조각이 2개가 아님) 점수가 숫자가 아닌 줄은 버립니다. 이름·점수 앞뒤 공백은 무시합니다.\n"
           "2. `count`: 남은 기록 수, `average`: 평균(소수 첫째 자리 반올림, 기록이 없으면 0)\n"
           "3. `passed`: 기준 이상인 기록의 이름을 대문자로, 중복 없이 사전 순으로\n\n"
           "예: `([\"민준: 85\", \"서연:92\", \"잘못된줄\", \"지호: 58\", \"민준:70\"], 60)` → `{\"count\": 4, \"passed\": [\"민준\", \"서연\"], \"average\": 76.2}`",
           ["comprehension", "generator", "string_parsing"], 3,
           '''
            def summarize(rows, min_score):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_pipeline(*a), desc=d, compare={"mode": "float", "tol": 1e-9}) for a, tid, d in pipe_cases],
           ["각 줄을 `split(\":\")`로 나누고, 조각 수와 `strip().isdigit()`로 걸러 `(이름, 정수 점수)` 목록을 만드세요.",
            "통과 이름은 집합 컴프리헨션 `{n.upper() for n, s in ... if s >= min_score}`을 정렬하면 됩니다.",
            "평균은 `round(합계 / 개수, 1)`이고, 기록이 없을 때를 따로 처리합니다."],
           '''
            def summarize(rows, min_score):
                parsed = []
                for row in rows:
                    parts = row.split(":")
                    if len(parts) == 2 and parts[1].strip().isdigit():
                        parsed.append((parts[0].strip(), int(parts[1])))
                passed = sorted({name.upper() for name, score in parsed if score >= min_score})
                average = round(sum(s for _, s in parsed) / len(parsed), 1) if parsed else 0
                return {"count": len(parsed), "passed": passed, "average": average}
           ''', mode="function", name="summarize"),
        ex("d49_code_2", "coding", "[도전] 메모이제이션 데코레이터",
           "데코레이터 `memoize`를 작성하세요. 같은 인자로 다시 호출되면 함수를 실행하지 않고 저장해 둔 결과를 돌려줍니다. "
           "감싼 함수에 `calls` 속성(실제로 원래 함수가 실행된 횟수)을 두세요.\n\n"
           "`check(n)`은 채점용이며 `[fib(n), 실제 실행 횟수]`를 반환합니다. 예: `check(10)` → `[55, 11]`",
           ["decorator", "closure", "recursion", "dict"], 3,
           '''
            # 여기에 memoize 데코레이터를 작성하세요


            @memoize
            def fib(n):
                if n <= 1:
                    return n
                return fib(n - 1) + fib(n - 2)


            def check(n):
                return [fib(n), fib.calls]
           ''',
           [t(tid, args=[n], ret=[fib(n), fib_memo_calls(n)], desc=d) for n, tid, d in memo_ns],
           ["`memoize` 안에 결과를 저장할 딕셔너리를 만들고, `wrapper(*args)`에서 `args`가 딕셔너리에 있으면 저장된 값을 반환합니다.",
            "없으면 `wrapper.calls += 1` 후 원래 함수를 실행해 저장하고 반환합니다.",
            "`wrapper.calls = 0`을 `return wrapper` 전에 설정하세요."],
           '''
            def memoize(func):
                cache = {}

                def wrapper(*args):
                    if args not in cache:
                        wrapper.calls += 1
                        cache[args] = func(*args)
                    return cache[args]

                wrapper.calls = 0
                return wrapper


            @memoize
            def fib(n):
                if n <= 1:
                    return n
                return fib(n - 1) + fib(n - 2)


            def check(n):
                return [fib(n), fib.calls]
           ''', mode="function", name="check", required=False),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day43, day44, day45, day46, day47, day48, day49])
