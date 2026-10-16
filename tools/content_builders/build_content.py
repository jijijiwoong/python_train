"""Scratch builder that writes lab_app/content JSON (the JSON files are the source of truth).
Expected outputs are computed with independent Python expressions, not by running solutions."""
import json
import shutil
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(sys.argv[1])
OUT = ROOT / "lab_app" / "content"


def c(s: str) -> str:
    return dedent(s).lstrip("\n")


def quiz(qid, q, choices, ans, exp):
    return {"id": qid, "question_md": q, "choices": choices, "answer_index": ans, "explanation_md": exp}


def text(md):
    return {"kind": "text", "md": md}


def tip(md):
    return {"kind": "tip", "md": md}


def code(src, out=None):
    b = {"kind": "code", "code": c(src), "runnable": out is not None}
    if out is not None:
        b["expected_output"] = out
    return b


def t(tid, stdin=None, out=None, args=None, ret=..., raises=None, desc="", compare=None):
    d = {"id": tid, "hidden": tid.startswith("h"), "description": desc}
    if stdin is not None:
        d["stdin"] = stdin
    if args is not None:
        d["call"] = {"args": args}
    expect = {}
    if out is not None:
        expect["stdout"] = out
    if ret is not ...:
        expect["return"] = ret
    if raises:
        expect["raises"] = raises
    d["expect"] = expect
    if compare:
        d["compare"] = compare
    return d


def lines(*xs):
    return "".join(f"{x}\n" for x in xs)


def lesson(day, title, concepts, objectives, review, concept, fill_intro, coding_intro, summary, exercises, is_review=False):
    fills = [e["id"] for e in exercises if e["kind"] == "fill_blank"]
    codes = [e["id"] for e in exercises if e["kind"] == "coding"]
    return {
        "schema_version": 1, "day": day, "title": title, "stage": "basics", "week": 1, "is_review": is_review,
        "objectives": objectives, "concepts": concepts,
        "sections": [
            {"type": "review", "minutes": 2, **review},
            {"type": "concept", "minutes": 4, **concept},
            {"type": "fill_blank", "minutes": 3, "title": "빈칸 채우기", "intro_md": fill_intro, "exercise_ids": fills},
            {"type": "coding", "minutes": 4, "title": "직접 작성하기", "intro_md": coding_intro, "exercise_ids": codes},
            {"type": "summary", "minutes": 2, **summary},
        ],
        "exercises": exercises,
    }


def ex(id_, kind, title, prompt, concepts, difficulty, starter, tests, hints, solution, mode="program",
       name=None, checks=None, required=True):
    e = {"id": id_, "kind": kind, "title": title, "prompt_md": prompt, "concepts": concepts,
         "difficulty": difficulty, "required": required, "starter_code": c(starter),
         "entry": {"mode": mode, **({"name": name} if name else {})}, "tests": tests, "hints": hints,
         "solution": c(solution)}
    if checks:
        e["checks"] = checks
    return e


# ====================================================================== Day 1
day1 = lesson(
    1, "print와 변수, 기본 자료형", ["print", "variable", "data_type"],
    ["print()로 원하는 내용을 화면에 출력할 수 있다.", "변수에 값을 저장하고 꺼내 쓸 수 있다.",
     "int, float, str, bool 네 가지 기본 자료형을 구분할 수 있다."],
    review={"title": "시작하기 전에", "content_md": (
        "Python Learning Lab에 오신 것을 환영합니다! 매일 15분씩 **복습 → 개념 → 빈칸 채우기 → 직접 작성 → 정리** 순서로 공부합니다.\n\n"
        "- 코드는 오른쪽 위 **실행** 버튼으로 몇 번이든 돌려 볼 수 있습니다.\n"
        "- **채점**을 누르면 공개 테스트와 숨김 테스트로 정답을 확인합니다.\n"
        "- 막히면 힌트를 한 단계씩 열어 보세요. 정답은 한 번 이상 제출한 뒤에 볼 수 있습니다.\n\n"
        "필수 문제를 모두 통과하고 정리 퀴즈를 제출하면 오늘 수업이 완료됩니다."),
        "quiz": [quiz("d01_review_q1", "이 앱에서 수업이 **완료**되는 조건은?",
                      ["개념 설명을 끝까지 읽으면", "필수 문제를 모두 통과하고 정리 퀴즈를 제출하면",
                       "정답 보기를 누르면", "15분이 지나면"], 1,
                      "문제를 직접 풀어 통과해야 완료됩니다. 읽기만 하거나 시간이 지나는 것으로는 완료되지 않습니다.")]},
    concept={"title": "출력, 변수, 자료형", "blocks": [
        text("`print()`는 괄호 안의 값을 화면에 보여 주는 **함수**입니다. 문자열(글자)은 따옴표로 감싸고, 숫자는 그대로 씁니다. "
             "쉼표로 여러 값을 넘기면 사이에 공백 한 칸을 넣어 출력합니다."),
        code('''
            print("Hello, Python!")
            print(3 + 4)
            print("답:", 3 + 4)
        ''', lines("Hello, Python!", 7, "답: 7")),
        text("**변수**는 값에 붙이는 이름표입니다. `이름 = 값` 형태로 저장하고, 이름을 쓰면 저장된 값을 꺼냅니다. "
             "`type()`으로 값의 **자료형**을 확인할 수 있습니다."),
        code('''
            language = "파이썬"
            year = 1991
            version = 3.14
            is_fun = True
            print(language, year)
            print(type(year))
            print(type(version))
            print(type(language))
            print(type(is_fun))
        ''', lines("파이썬 1991", "<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>")),
        tip("`=`는 \"같다\"가 아니라 \"오른쪽 값을 왼쪽 이름에 **저장**한다\"는 뜻입니다. "
            "변수 이름은 영문자·숫자·밑줄(`_`)로 만들고 숫자로 시작할 수 없습니다. `True`/`False`는 첫 글자가 대문자입니다."),
        code('''
            count = 1
            count = count + 1
            print(count)
        ''', lines(2)),
    ]},
    fill_intro="빈칸 `____`을 채워 코드를 완성하세요. 빈칸이 하나라도 남아 있으면 채점되지 않습니다.",
    coding_intro="주어진 변수를 이용해 계산하고 결과를 출력해 봅시다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`print(값1, 값2)`는 값을 공백으로 이어 출력하고 줄을 바꾼다.",
        "`변수 = 값`으로 저장하고, 같은 이름에 다시 저장하면 값이 바뀐다.",
        "기본 자료형: 정수 `int`, 실수 `float`, 문자열 `str`, 참/거짓 `bool`.",
        "`type(값)`으로 자료형을 확인할 수 있다."],
        "quiz": [
            quiz("d01_summary_q1", '`type("123")`의 결과는?',
                 ["<class 'int'>", "<class 'str'>", "<class 'float'>", "오류"], 1,
                 "따옴표로 감싼 값은 숫자처럼 보여도 **문자열(str)**입니다."),
            quiz("d01_summary_q2", "`x = 5` 다음 줄에 `x = x * 2`를 실행하면 `x`의 값은?",
                 ["5", "10", "x * 2", "오류"], 1, "오른쪽 `x * 2`를 먼저 계산(10)한 뒤 그 값을 다시 `x`에 저장합니다.")]},
    exercises=[
        ex("d01_fill_1", "fill_blank", "변수 출력하기",
           "변수 `language`에 문자열 `Python`을 저장하고, `language`와 `version`을 한 줄씩 출력하세요.\n\n"
           "**출력 예시**\n```\nPython\n3.14\n```",
           ["variable", "print", "data_type"], 1,
           '''
            language = ____
            version = 3.14
            print(language)
            print(____)
           ''',
           [t("t1", out=lines("Python", 3.14), desc="두 줄 출력")],
           ["문자열은 따옴표(\" 또는 ')로 감싸야 합니다.", "두 번째 빈칸에는 이미 만들어 둔 변수의 이름을 쓰면 됩니다."],
           '''
            language = "Python"
            version = 3.14
            print(language)
            print(version)
           '''),
        ex("d01_code_1", "coding", "총액 계산하기",
           "커피 한 잔 가격 `price`와 잔 수 `count`가 주어집니다. 총액을 변수 `total`에 계산해 저장한 뒤 "
           "아래처럼 두 줄을 출력하세요. 둘째 줄은 `total`의 자료형입니다.\n\n"
           "**출력 예시**\n```\n총액: 13500\n<class 'int'>\n```",
           ["variable", "operator", "print", "data_type"], 1,
           '''
            price = 4500
            count = 3
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", out=lines(f"총액: {4500 * 3}", "<class 'int'>"), desc="총액과 자료형")],
           ["곱셈 연산자는 `*`입니다. 계산 결과를 새 변수에 저장해 보세요.",
            "`print(\"총액:\", 변수)`처럼 쉼표로 이어 쓰면 사이에 공백이 하나 들어갑니다.",
            "자료형은 `type()` 결과를 그대로 출력하면 됩니다."],
           '''
            price = 4500
            count = 3
            total = price * count
            print("총액:", total)
            print(type(total))
           '''),
    ])

# ====================================================================== Day 2
day2 = lesson(
    2, "연산자와 입력, 형 변환", ["operator", "input", "type_conversion"],
    ["산술·비교 연산자로 값을 계산할 수 있다.", "input()으로 값을 입력받을 수 있다.",
     "int(), float(), str()로 자료형을 바꿀 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": (
        "어제는 `print()`로 출력하고, 변수에 값을 저장했습니다. 값에는 `int`, `float`, `str`, `bool` 같은 **자료형**이 있었습니다."),
        "quiz": [quiz("d02_review_q1", "`print(\"나이:\", 20)`의 출력은?",
                      ["나이:20", "나이: 20", "\"나이:\" 20", "오류"], 1,
                      "쉼표로 여러 값을 출력하면 사이에 공백 한 칸이 들어갑니다.")]},
    concept={"title": "연산자와 입력", "blocks": [
        text("Python의 산술 연산자입니다. `/`는 항상 실수(float)를, `//`는 **몫**을, `%`는 **나머지**를 돌려줍니다."),
        code('''
            print(7 + 3)
            print(7 - 3)
            print(7 * 3)
            print(7 / 3)
            print(7 // 3)
            print(7 % 3)
            print(2 ** 10)
        ''', lines(7 + 3, 7 - 3, 7 * 3, 7 / 3, 7 // 3, 7 % 3, 2 ** 10)),
        text("비교 연산자(`==`, `!=`, `>`, `<`, `>=`, `<=`)의 결과는 `True` 또는 `False`입니다."),
        code('''
            print(3 > 2)
            print(3 == 3.0)
            print("a" != "a")
        ''', lines(True, True, False)),
        text("`input()`은 사용자가 입력한 한 줄을 **문자열**로 돌려줍니다. 숫자로 계산하려면 `int()`나 `float()`로 바꿔야 합니다."),
        code('''
            age = int(input("나이를 입력하세요: "))
            print("내년 나이:", age + 1)
        '''),
        code('''
            text = "42"
            number = int(text)
            print(number + 8)
            print(float("3.5") * 2)
            print(str(100) + "점")
            print(text + text)
        ''', lines(50, 7.0, "100점", "4242")),
        tip("`input()` 결과를 변환하지 않고 더하면 `\"3\" + \"4\"` → `\"34\"`처럼 글자가 이어 붙습니다. "
            "채점할 때 `input(\"안내 문구\")`의 안내 문구는 출력으로 보지 않으니 자유롭게 써도 됩니다."),
    ]},
    fill_intro="입력받은 두 수를 계산하는 코드를 완성하세요. 채점은 여러 입력값으로 진행됩니다.",
    coding_intro="몫(`//`)과 나머지(`%`)를 활용해 봅시다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`/`는 실수 나눗셈, `//`는 몫, `%`는 나머지, `**`는 거듭제곱.",
        "비교 연산의 결과는 `bool`(`True`/`False`)이다.",
        "`input()`은 항상 문자열을 돌려준다 → 계산하려면 `int()`/`float()`로 변환.",
        "`str()`로 숫자를 문자열로 바꾸면 다른 문자열과 `+`로 이어 붙일 수 있다."],
        "quiz": [
            quiz("d02_summary_q1", "`17 // 5`와 `17 % 5`의 결과를 차례로 쓰면?",
                 ["3, 2", "3.4, 2", "2, 3", "3, 0"], 0, "17 = 5 × 3 + 2 이므로 몫은 3, 나머지는 2입니다."),
            quiz("d02_summary_q2", "`input()`으로 `5`를 입력받아 `x`에 저장했습니다. `x + x`의 결과는?",
                 ["10", "\"55\"", "오류", "5"], 1, "`input()`은 문자열 `\"5\"`를 돌려주므로 `+`는 글자를 이어 붙입니다.")]},
    exercises=[
        ex("d02_fill_1", "fill_blank", "두 수의 합",
           "정수 두 개를 한 줄에 하나씩 입력받아 합을 출력하세요.\n\n**입력 예시**\n```\n3\n5\n```\n**출력 예시**\n```\n8\n```",
           ["input", "type_conversion", "operator"], 1,
           '''
            a = ____(input())
            b = int(input())
            print(a ____ b)
           ''',
           [t("t1", stdin="3\n5\n", out=lines(3 + 5), desc="3과 5"),
            t("h1", stdin="10\n-4\n", out=lines(10 - 4)), t("h2", stdin="0\n0\n", out=lines(0))],
           ["`input()`의 결과는 문자열입니다. 둘째 줄 `b`는 어떻게 바꾸고 있나요?",
            "합을 구하는 연산자를 두 변수 사이에 넣으세요."],
           '''
            a = int(input())
            b = int(input())
            print(a + b)
           '''),
        ex("d02_code_1", "coding", "분을 시간과 분으로",
           "총 시간(분)을 정수로 입력받아 **몇 시간 몇 분**인지 구하세요. 첫째 줄에 시간, 둘째 줄에 남은 분을 출력합니다.\n\n"
           "**입력 예시**\n```\n125\n```\n**출력 예시**\n```\n2\n5\n```",
           ["input", "type_conversion", "operator"], 2,
           '''
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin="125\n", out=lines(125 // 60, 125 % 60), desc="125분"),
            t("t2", stdin="60\n", out=lines(1, 0), desc="60분"),
            t("h1", stdin="59\n", out=lines(0, 59)), t("h2", stdin="0\n", out=lines(0, 0)),
            t("h3", stdin="1441\n", out=lines(1441 // 60, 1441 % 60))],
           ["입력값은 문자열이므로 먼저 정수로 바꿔야 합니다.",
            "1시간은 60분입니다. 시간은 \"60으로 나눈 몫\", 남은 분은 \"60으로 나눈 나머지\"입니다.",
            "몫과 나머지 연산자를 각각 써서 `print()`를 두 번 호출하세요."],
           '''
            minutes = int(input())
            print(minutes // 60)
            print(minutes % 60)
           '''),
    ])

# ====================================================================== Day 3
day3 = lesson(
    3, "문자열 다루기", ["string", "string_method", "fstring"],
    ["인덱싱과 슬라이싱으로 문자열의 일부를 꺼낼 수 있다.", "strip, upper, replace 등 문자열 메서드를 쓸 수 있다.",
     "f-string으로 변수와 문장을 함께 출력할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": (
        "어제는 연산자와 `input()`, 형 변환을 배웠습니다. `input()`은 항상 **문자열**을 돌려준다는 점이 중요했죠. "
        "오늘은 그 문자열을 자유롭게 다루는 방법을 배웁니다."),
        "quiz": [quiz("d03_review_q1", "`int(\"7\") + 3`의 결과는?", ["73", "10", "\"10\"", "오류"], 1,
                      "`int(\"7\")`은 정수 7이 되므로 7 + 3 = 10입니다.")]},
    concept={"title": "문자열 인덱싱·슬라이싱·메서드·f-string", "blocks": [
        text("문자열의 각 글자에는 **0부터** 번호(인덱스)가 붙습니다. 음수 인덱스는 뒤에서부터 셉니다. "
             "`[시작:끝]`으로 일부를 잘라낼 수 있고, **끝 위치는 포함하지 않습니다**."),
        code('''
            word = "Python"
            print(word[0])
            print(word[-1])
            print(word[0:3])
            print(word[2:])
            print(len(word))
        ''', lines("Python"[0], "Python"[-1], "Python"[0:3], "Python"[2:], len("Python"))),
        text("문자열에는 유용한 **메서드**(문자열 뒤에 `.`을 찍고 부르는 함수)가 있습니다."),
        code('''
            s = "  Hello World  "
            print(s.strip())
            print(s.strip().upper())
            print(s.strip().lower())
            print("a,b,c".replace(",", "-"))
            print("banana".count("a"))
        ''', lines("Hello World", "HELLO WORLD", "hello world", "a-b-c", 3)),
        text("**f-string**은 문자열 앞에 `f`를 붙이고 `{}` 안에 변수나 식을 넣는 방법입니다. `{값:.1f}`처럼 소수점 자릿수도 정할 수 있습니다."),
        code('''
            name = "파이썬"
            score = 92.456
            print(f"{name}의 점수는 {score}점")
            print(f"반올림: {score:.1f}")
            print(f"2 + 3 = {2 + 3}")
        ''', lines("파이썬의 점수는 92.456점", f"반올림: {92.456:.1f}", "2 + 3 = 5")),
        tip("문자열은 **바꿀 수 없습니다**. `word[0] = \"J\"`는 오류가 납니다. 메서드는 원본을 바꾸지 않고 **새 문자열**을 돌려주므로 결과를 변수에 다시 저장해야 합니다."),
    ]},
    fill_intro="인덱스와 `len()`을 이용해 문자열 정보를 출력하세요.",
    coding_intro="입력값을 다듬고 f-string으로 문장을 만들어 봅시다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "인덱스는 0부터, `-1`은 마지막 글자.",
        "슬라이싱 `s[a:b]`는 a부터 b **직전**까지.",
        "`strip()` 앞뒤 공백 제거, `upper()`/`lower()` 대소문자, `replace(a, b)` 바꾸기.",
        "f-string: `f\"{변수}\"`, 소수점은 `{x:.2f}`."],
        "quiz": [
            quiz("d03_summary_q1", "`\"Python\"[1:4]`의 결과는?", ["Pyt", "yth", "ytho", "Pyth"], 1,
                 "인덱스 1(y)부터 4 직전인 3(h)까지입니다."),
            quiz("d03_summary_q2", "`f\"{3.14159:.2f}\"`의 결과는?", ["3.1", "3.14", "3.14159", "3"], 1,
                 "`.2f`는 소수점 아래 두 자리까지 반올림해 표시합니다.")]},
    exercises=[
        ex("d03_fill_1", "fill_blank", "첫 글자, 마지막 글자, 길이",
           "단어 하나를 입력받아 **첫 글자**, **마지막 글자**, **글자 수**를 한 줄씩 출력하세요.\n\n"
           "**입력 예시**\n```\nPython\n```\n**출력 예시**\n```\nP\nn\n6\n```",
           ["string"], 1,
           '''
            word = input()
            print(word[____])
            print(word[____])
            print(____(word))
           ''',
           [t("t1", stdin="Python\n", out=lines("P", "n", 6), desc="Python"),
            t("h1", stdin="a\n", out=lines("a", "a", 1)), t("h2", stdin="안녕하세요\n", out=lines("안", "요", 5))],
           ["인덱스는 0부터 시작하고, 뒤에서부터 셀 때는 음수를 씁니다.",
            "길이를 알려 주는 내장 함수 이름은 세 글자입니다."],
           '''
            word = input()
            print(word[0])
            print(word[-1])
            print(len(word))
           '''),
        ex("d03_code_1", "coding", "내년 나이 안내문",
           "첫째 줄에 이름, 둘째 줄에 나이(정수)를 입력받습니다. 이름 앞뒤에 공백이 섞여 있을 수 있으니 제거한 뒤, "
           "**f-string**으로 아래 형식의 문장을 출력하세요.\n\n"
           "**입력 예시**\n```\n  철수 \n20\n```\n**출력 예시**\n```\n철수님, 내년에 21살이 됩니다\n```",
           ["string_method", "fstring", "type_conversion"], 2,
           '''
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin="  철수 \n20\n", out=lines("철수님, 내년에 21살이 됩니다"), desc="공백 포함 이름"),
            t("h1", stdin="Alice\n9\n", out=lines("Alice님, 내년에 10살이 됩니다")),
            t("h2", stdin="민\n0\n", out=lines("민님, 내년에 1살이 됩니다"))],
           ["앞뒤 공백을 없애는 문자열 메서드를 떠올려 보세요.",
            "나이는 계산해야 하므로 정수로 변환합니다.",
            "`f\"{변수}님, ...\"`처럼 중괄호 안에 식(`나이 + 1`)을 바로 넣을 수 있습니다."],
           '''
            name = input().strip()
            age = int(input())
            print(f"{name}님, 내년에 {age + 1}살이 됩니다")
           ''',
           checks={"required_syntax": ["fstring"]}),
    ])

# ====================================================================== Day 4
def fee(age):
    if age < 8 or age >= 65:
        return "무료"
    if age <= 18:
        return "5000원"
    return "10000원"


day4 = lesson(
    4, "조건문", ["condition", "logical_operator"],
    ["if / elif / else로 상황에 따라 다른 코드를 실행할 수 있다.", "and, or, not으로 조건을 조합할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": (
        "어제는 문자열을 자르고(`s[a:b]`), 메서드로 바꾸고, f-string으로 출력했습니다."),
        "quiz": [quiz("d04_review_q1", "`\"  hi  \".strip().upper()`의 결과는?", ["  HI  ", "HI", "hi", "Hi"], 1,
                      "`strip()`으로 공백을 지운 뒤 `upper()`로 대문자로 바꿉니다.")]},
    concept={"title": "조건에 따라 다르게 실행하기", "blocks": [
        text("`if 조건:` 아래 **들여쓴** 코드는 조건이 `True`일 때만 실행됩니다. `elif`로 조건을 더 붙이고, `else`는 앞의 조건이 모두 거짓일 때 실행됩니다. "
             "위에서부터 차례로 검사해서 **처음 참인 블록 하나만** 실행합니다."),
        code('''
            temperature = 28
            if temperature >= 30:
                print("덥습니다")
            elif temperature >= 20:
                print("따뜻합니다")
            else:
                print("쌀쌀합니다")
        ''', lines("따뜻합니다")),
        text("`and`는 둘 다 참일 때, `or`는 하나라도 참일 때 참입니다. `not`은 참/거짓을 뒤집습니다."),
        code('''
            age = 25
            has_ticket = True
            print(age >= 19 and has_ticket)
            print(age < 13 or age >= 65)
            print(not has_ticket)
        ''', lines(True, False, False)),
        code('''
            n = 7
            if n % 2 == 0:
                print("짝수")
            else:
                print("홀수")
        ''', lines("홀수")),
        tip("조건 끝의 콜론(`:`)과 블록의 들여쓰기(공백 4칸)를 잊지 마세요. 값을 비교할 때는 `=`(저장)가 아니라 `==`(같다)를 씁니다."),
    ]},
    fill_intro="나머지 연산자와 조건문으로 짝수·홀수를 판별하세요.",
    coding_intro="여러 구간을 나누는 조건문을 직접 작성해 봅시다. 경계값을 꼼꼼히 확인하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`if` → `elif` → `else` 순서로 검사하고, 처음 참인 블록 하나만 실행된다.",
        "블록은 콜론(`:`) 다음 줄부터 들여쓰기로 구분한다.",
        "`==`는 비교, `=`는 저장.",
        "`and`(모두 참), `or`(하나라도 참), `not`(뒤집기)."],
        "quiz": [
            quiz("d04_summary_q1", "`x = 15`일 때 `x > 10 and x < 20`의 결과는?", ["True", "False", "15", "오류"], 0,
                 "15는 10보다 크고 20보다 작으므로 두 조건이 모두 참입니다."),
            quiz("d04_summary_q2", "`if score >= 90:` 다음 `elif score >= 80:`이 있을 때 `score = 95`이면 실행되는 블록은?",
                 ["두 블록 모두", "첫 번째 블록만", "두 번째 블록만", "아무것도"], 1,
                 "처음 참인 블록 하나만 실행되고 나머지 elif/else는 건너뜁니다.")]},
    exercises=[
        ex("d04_fill_1", "fill_blank", "짝수일까 홀수일까",
           "정수를 입력받아 짝수면 `짝수`, 홀수면 `홀수`를 출력하세요. (0은 짝수입니다)",
           ["condition", "operator"], 1,
           '''
            n = int(input())
            if n % 2 ____ 0:
                print("짝수")
            ____:
                print("홀수")
           ''',
           [t("t1", stdin="4\n", out=lines("짝수"), desc="4"), t("t2", stdin="7\n", out=lines("홀수"), desc="7"),
            t("h1", stdin="0\n", out=lines("짝수")), t("h2", stdin="-3\n", out=lines("홀수"))],
           ["2로 나눈 나머지가 0인지 \"같다\"로 비교해야 합니다. 저장(`=`)과 비교는 기호가 다릅니다.",
            "앞의 조건이 거짓일 때 실행되는 블록의 키워드를 쓰세요."],
           '''
            n = int(input())
            if n % 2 == 0:
                print("짝수")
            else:
                print("홀수")
           '''),
        ex("d04_code_1", "coding", "놀이공원 입장료",
           "나이(정수)를 입력받아 입장료를 출력하세요.\n\n"
           "| 나이 | 출력 |\n|---|---|\n| 8세 미만 또는 65세 이상 | `무료` |\n| 8세 이상 18세 이하 | `5000원` |\n| 19세 이상 64세 이하 | `10000원` |\n\n"
           "**입력 예시**\n```\n15\n```\n**출력 예시**\n```\n5000원\n```",
           ["condition", "logical_operator"], 2,
           '''
            age = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t(f"t{i}", stdin=f"{a}\n", out=lines(fee(a)), desc=f"{a}세") for i, a in enumerate((5, 15, 30), start=1)]
           + [t(f"h{i}", stdin=f"{a}\n", out=lines(fee(a))) for i, a in enumerate((7, 8, 18, 19, 64, 65), start=1)],
           ["무료인 경우를 먼저 처리하면 나머지 구간이 단순해집니다.",
            "\"8세 미만 **또는** 65세 이상\"은 `or`로 두 조건을 연결합니다.",
            "경계값(8, 18, 19, 65)이 어느 구간에 들어가는지 `<`와 `<=`를 구분해 확인하세요."],
           '''
            age = int(input())
            if age < 8 or age >= 65:
                print("무료")
            elif age <= 18:
                print("5000원")
            else:
                print("10000원")
           ''',
           checks={"required_syntax": ["if"]}),
    ])

# ====================================================================== Day 5
def times_table(n):
    return "".join(f"{n} x {i} = {n * i}\n" for i in range(1, 10))


def even_sum(n):
    total = 0
    k = 2
    while k <= n:
        total += k
        k += 2
    return total


day5 = lesson(
    5, "반복문", ["for_loop", "range", "while_loop", "accumulation"],
    ["for와 range()로 정해진 횟수만큼 반복할 수 있다.", "while로 조건이 참인 동안 반복할 수 있다.",
     "반복문으로 값을 누적하는 패턴을 쓸 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `if / elif / else`로 조건에 따라 다른 코드를 실행했습니다.",
            "quiz": [quiz("d05_review_q1", "`n = 10`일 때 `n % 3 == 1`의 결과는?", ["True", "False", "1", "3"], 0,
                          "10을 3으로 나눈 나머지는 1이므로 `1 == 1` → True입니다.")]},
    concept={"title": "같은 일을 여러 번", "blocks": [
        text("`for 변수 in range(...):`는 정해진 횟수만큼 반복합니다. `range(n)`은 0부터 n-1까지, "
             "`range(시작, 끝, 간격)`은 시작부터 끝 **직전**까지 간격만큼 건너뛰며 숫자를 만듭니다."),
        code('''
            for i in range(3):
                print(i)
            for i in range(1, 6, 2):
                print(i)
        ''', lines(*range(3), *range(1, 6, 2))),
        text("반복하면서 값을 쌓아 가는 **누적 패턴**입니다. 반복 전에 `0`으로 시작하고, 반복 안에서 더합니다. `total += n`은 `total = total + n`의 줄임말입니다."),
        code('''
            total = 0
            for n in range(1, 11):
                total += n
            print(total)
        ''', lines(sum(range(1, 11)))),
        text("`for`는 문자열의 글자를 하나씩 꺼낼 수도 있습니다."),
        code('''
            for ch in "abc":
                print(ch.upper())
        ''', lines("A", "B", "C")),
        text("`while 조건:`은 조건이 참인 **동안** 반복합니다. 반복 안에서 조건이 언젠가 거짓이 되도록 값을 바꿔야 합니다."),
        code('''
            count = 3
            while count > 0:
                print(count)
                count -= 1
            print("발사!")
        ''', lines(3, 2, 1, "발사!")),
        tip("`while` 조건이 계속 참이면 **무한 루프**가 됩니다. 이 앱에서는 5초가 지나면 자동으로 멈추고 \"시간 초과\"로 알려 줍니다."),
    ]},
    fill_intro="`range()`와 f-string으로 구구단을 출력하세요.",
    coding_intro="누적 패턴을 직접 작성해 봅시다. 이 문제에서는 `for`문을 사용하고, 합계 함수 `sum()`은 쓰지 않습니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`range(끝)`, `range(시작, 끝)`, `range(시작, 끝, 간격)` — 끝은 포함하지 않는다.",
        "누적 패턴: `total = 0` → 반복 안에서 `total += 값`.",
        "`for`는 횟수·대상이 정해져 있을 때, `while`은 조건이 참인 동안 반복할 때.",
        "`while`에서는 조건이 거짓이 되도록 값을 바꿔야 무한 루프를 피한다."],
        "quiz": [
            quiz("d05_summary_q1", "`list(range(2, 8, 3))`의 결과는?", ["[2, 5]", "[2, 5, 8]", "[2, 3, 4]", "[3, 6]"], 0,
                 "2부터 시작해 3씩 건너뛰고 8 직전에서 멈춥니다: 2, 5."),
            quiz("d05_summary_q2", "다음 중 무한 루프가 되는 코드는?",
                 ["`for i in range(5): print(i)`", "`n = 0` 후 `while n < 3: n += 1`",
                  "`n = 0` 후 `while n < 3: print(n)`", "`for ch in \"hi\": print(ch)`"], 2,
                 "`n`을 바꾸지 않으므로 `n < 3`이 영원히 참입니다.")]},
    exercises=[
        ex("d05_fill_1", "fill_blank", "구구단 출력",
           "정수 `n`을 입력받아 `n`단을 1부터 9까지 출력하세요.\n\n"
           "**입력 예시**\n```\n2\n```\n**출력 예시 (앞부분)**\n```\n2 x 1 = 2\n2 x 2 = 4\n...\n2 x 9 = 18\n```",
           ["for_loop", "range", "fstring"], 1,
           '''
            n = int(input())
            for i in range(1, ____):
                print(f"{n} x {i} = {____}")
           ''',
           [t("t1", stdin="2\n", out=times_table(2), desc="2단"),
            t("h1", stdin="9\n", out=times_table(9)), t("h2", stdin="1\n", out=times_table(1))],
           ["`range`의 끝 값은 포함되지 않습니다. 9까지 반복하려면 끝 값이 얼마여야 할까요?",
            "중괄호 안에는 변수뿐 아니라 계산식도 넣을 수 있습니다."],
           '''
            n = int(input())
            for i in range(1, 10):
                print(f"{n} x {i} = {n * i}")
           '''),
        ex("d05_code_1", "coding", "짝수의 합",
           "정수 `n`을 입력받아 **1부터 n까지의 짝수**를 모두 더한 값을 출력하세요. `n`이 2보다 작으면 0을 출력합니다.\n\n"
           "- `for`문을 사용하세요.\n- `sum()` 함수는 사용할 수 없습니다.\n\n"
           "**입력 예시**\n```\n10\n```\n**출력 예시**\n```\n30\n```",
           ["for_loop", "range", "accumulation"], 2,
           '''
            n = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin="10\n", out=lines(even_sum(10)), desc="n = 10"),
            t("t2", stdin="1\n", out=lines(even_sum(1)), desc="n = 1"),
            t("h1", stdin="2\n", out=lines(even_sum(2))), t("h2", stdin="7\n", out=lines(even_sum(7))),
            t("h3", stdin="100\n", out=lines(even_sum(100))), t("h4", stdin="0\n", out=lines(0))],
           ["반복 전에 합계를 담을 변수를 0으로 만들어 두세요.",
            "짝수만 고르려면 반복 안에서 조건문을 쓰거나, `range`의 간격을 이용할 수 있습니다.",
            "`range`의 끝 값은 포함되지 않으니 `n`까지 포함하려면 끝을 하나 늘려야 합니다."],
           '''
            n = int(input())
            total = 0
            for i in range(2, n + 1, 2):
                total += i
            print(total)
           ''',
           checks={"required_syntax": ["for"], "forbidden_calls": ["sum"]}),
    ])

# ====================================================================== Day 6 (from the validated design example)
day6 = json.loads((ROOT / "01_design" / "example_lesson.json").read_text(encoding="utf-8"))

# ====================================================================== Day 7
def count_multiples(n, k):
    return sum(1 for i in range(1, n + 1) if i % k == 0)


def report(scores):
    avg = sum(scores) / len(scores)
    return lines(f"평균: {avg:.1f}", f"최고: {max(scores)}", "합격" if avg >= 60 else "불합격")


def strength(pw):
    if pw == "":
        raise ValueError
    return "약함" if len(pw) < 8 else ("보통" if len(pw) < 12 else "강함")


score_cases = [[80, 90, 70], [59], [60, 60, 60, 60], [100, 0], [0, 0, 1]]
pw_cases = [("abc", "t1"), ("abcdefgh", "t2"), ("abcdefghijkl", "t3"), ("abcdefg", "h2"), ("abcdefghijk", "h3")]

day7 = lesson(
    7, "1주차 누적 복습", ["print", "variable", "input", "type_conversion", "string", "fstring", "condition",
                       "for_loop", "accumulation", "function", "return", "exception"],
    ["1주차에 배운 문법을 섞어 하나의 프로그램을 완성할 수 있다.", "문제를 입력 → 처리 → 출력 단계로 나눠 생각할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "이번 주에 배운 내용입니다.\n\n"
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 1 | 출력·변수·자료형 | `print()`, `=`, `int/float/str/bool` |\n"
        "| 2 | 연산자·입력·형 변환 | `// %`, `input()`은 문자열, `int()` |\n"
        "| 3 | 문자열 | `s[0]`, `s[a:b]`, `strip()`, `f\"{x}\"` |\n"
        "| 4 | 조건문 | `if / elif / else`, `and / or / not` |\n"
        "| 5 | 반복문 | `for`, `range()`, `while`, 누적 패턴 |\n"
        "| 6 | 함수 | `def`, `return`, `raise ValueError` |"),
        "quiz": [
            quiz("d07_review_q1", "`print(type(10 / 2))`의 결과는?", ["<class 'int'>", "<class 'float'>", "5", "5.0"], 1,
                 "`/` 나눗셈은 나누어떨어져도 항상 float를 돌려줍니다."),
            quiz("d07_review_q2", "함수가 값을 **돌려주려면** 무엇을 써야 하나요?", ["print", "return", "input", "def"], 1,
                 "`print`는 화면에 보여 주기만 하고, `return`이 호출한 곳으로 값을 돌려줍니다.")]},
    concept={"title": "배운 것을 조합하기", "blocks": [
        text("프로그램은 대부분 **입력 → 처리 → 출력** 세 단계로 나눌 수 있습니다. 아래 예제는 함수 안에서 반복문과 조건문을 함께 쓰고, f-string으로 결과를 출력합니다."),
        code('''
            def count_upper(text):
                count = 0
                for ch in text:
                    if ch.isupper():
                        count += 1
                return count

            word = "Hello Python World"
            print(f"{word}: 대문자 {count_upper(word)}개")
        ''', lines("Hello Python World: 대문자 3개")),
        text("반복문에서 **최댓값**을 찾을 때는 첫 값을 기준으로 두고, 더 큰 값이 나오면 바꿔 줍니다."),
        code('''
            best = 3
            for n in [7, 2, 9, 4]:
                if n > best:
                    best = n
            print(best)
        ''', lines(9)),
        tip("`[7, 2, 9, 4]`처럼 대괄호로 값을 묶은 것을 **리스트**라고 합니다. 2주차에 자세히 배웁니다. "
            "오늘 문제는 리스트 없이 `input()`과 반복문만으로 풀 수 있습니다."),
    ]},
    fill_intro="함수 안의 반복문과 조건문을 완성하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제(함수와 예외)는 **도전 문제**로 수업 완료에 필요하지 않습니다.",
    summary={"title": "1주차 마무리", "points": [
        "입력은 `input()` + 형 변환, 출력은 `print()`와 f-string.",
        "결정은 `if / elif / else`, 반복은 `for`/`while`, 누적은 `total += 값`.",
        "자주 쓰는 처리는 `def`로 함수를 만들고 `return`으로 결과를 돌려준다.",
        "다음 주에는 여러 값을 한꺼번에 다루는 **리스트와 튜플**을 배운다."],
        "quiz": [
            quiz("d07_summary_q1", "다음 코드의 출력은?\n```python\nt = 0\nfor i in range(1, 4):\n    if i % 2 == 1:\n        t += i\nprint(t)\n```",
                 ["6", "4", "3", "1"], 1, "1과 3만 홀수이므로 1 + 3 = 4입니다."),
            quiz("d07_summary_q2", "`f\"{7 / 2:.1f}\"`의 결과는?", ["3", "3.5", "3.50", "4"], 1,
                 "7 / 2 = 3.5이고 `.1f`는 소수점 아래 한 자리입니다.")]},
    is_review=True,
    exercises=[
        ex("d07_fill_1", "fill_blank", "배수의 개수",
           "1부터 `n`까지의 정수 중 `k`의 배수가 몇 개인지 **반환**하는 함수 `count_multiples(n, k)`를 완성하세요.\n\n"
           "예: `count_multiples(10, 3)` → `3` (3, 6, 9)",
           ["function", "return", "for_loop", "condition", "accumulation"], 2,
           '''
            def count_multiples(n, k):
                count = 0
                for i in range(1, n ____ 1):
                    if i % k == 0:
                        count ____ 1
                return count
           ''',
           [t("t1", args=[10, 3], ret=count_multiples(10, 3), desc="(10, 3)"),
            t("h1", args=[1, 1], ret=count_multiples(1, 1)), t("h2", args=[20, 5], ret=count_multiples(20, 5)),
            t("h3", args=[0, 2], ret=0), t("h4", args=[7, 7], ret=1)],
           ["`n`까지 포함하려면 `range`의 끝 값을 하나 늘려야 합니다.",
            "개수를 하나씩 늘릴 때 쓰는 복합 대입 연산자를 떠올려 보세요 (Day 5)."],
           '''
            def count_multiples(n, k):
                count = 0
                for i in range(1, n + 1):
                    if i % k == 0:
                        count += 1
                return count
           ''',
           mode="function", name="count_multiples"),
        ex("d07_code_1", "coding", "성적 리포트",
           "첫째 줄에 학생 수 `n`, 다음 `n`줄에 점수(0~100 정수)가 하나씩 주어집니다. 아래 세 줄을 출력하세요.\n\n"
           "1. `평균: 80.0` — 평균을 소수점 아래 한 자리까지\n2. `최고: 90` — 가장 높은 점수\n3. 평균이 60 이상이면 `합격`, 아니면 `불합격`\n\n"
           "**입력 예시**\n```\n3\n80\n90\n70\n```\n**출력 예시**\n```\n평균: 80.0\n최고: 90\n합격\n```",
           ["input", "for_loop", "accumulation", "condition", "fstring"], 3,
           '''
            n = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=lines(len(score_cases[0]), *score_cases[0]), out=report(score_cases[0]), desc="3명")]
           + [t(f"h{i}", stdin=lines(len(s), *s), out=report(s)) for i, s in enumerate(score_cases[1:], start=1)],
           ["합계와 최고 점수를 담을 변수를 반복 전에 준비하세요. 점수는 0 이상이므로 최고 점수는 -1로 시작해도 됩니다.",
            "`for _ in range(n):` 안에서 `input()`을 한 번씩 호출하면 점수를 차례로 읽을 수 있습니다.",
            "평균은 합계 ÷ 학생 수이고, 소수점 한 자리는 f-string의 `:.1f`로 맞춥니다."],
           '''
            n = int(input())
            total = 0
            best = -1
            for _ in range(n):
                score = int(input())
                total += score
                if score > best:
                    best = score
            average = total / n
            print(f"평균: {average:.1f}")
            print(f"최고: {best}")
            if average >= 60:
                print("합격")
            else:
                print("불합격")
           ''',
           checks={"required_syntax": ["for", "fstring"]}),
        ex("d07_code_2", "coding", "[도전] 비밀번호 강도",
           "문자열 `password`를 받아 강도를 **반환**하는 함수 `password_strength(password)`를 작성하세요.\n\n"
           "| 길이 | 반환값 |\n|---|---|\n| 8 미만 | `\"약함\"` |\n| 8 이상 12 미만 | `\"보통\"` |\n| 12 이상 | `\"강함\"` |\n\n"
           "빈 문자열이 들어오면 `ValueError`를 발생시키세요.",
           ["function", "return", "condition", "exception", "string"], 2,
           '''
            def password_strength(password):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[pw], ret=strength(pw), desc=f"길이 {len(pw)}") for pw, tid in pw_cases if tid.startswith("t")]
           + [t("t4", args=[""], raises="ValueError", desc="빈 문자열"), t("h1", args=[""], raises="ValueError")]
           + [t(tid, args=[pw], ret=strength(pw)) for pw, tid in pw_cases if tid.startswith("h")],
           ["먼저 빈 문자열인지 검사해 예외를 발생시키고, 그다음 길이를 비교하세요.",
            "길이는 `len()`으로 구합니다. 짧은 쪽부터 `if / elif / else`로 나누면 간단합니다.",
            "예외는 `raise ValueError(\"메시지\")` 형태로 발생시킵니다 (Day 6)."],
           '''
            def password_strength(password):
                if password == "":
                    raise ValueError("비밀번호가 비어 있습니다")
                if len(password) < 8:
                    return "약함"
                elif len(password) < 12:
                    return "보통"
                else:
                    return "강함"
           ''',
           mode="function", name="password_strength", checks={"required_syntax": ["def", "if"]}, required=False),
    ])

# ====================================================================== write
(OUT / "lessons").mkdir(parents=True, exist_ok=True)
shutil.copy(ROOT / "01_design" / "example_curriculum.json", OUT / "curriculum.json")
for d in (day1, day2, day3, day4, day5, day6, day7):
    path = OUT / "lessons" / f"day{d['day']:02d}.json"
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", path.relative_to(ROOT))
