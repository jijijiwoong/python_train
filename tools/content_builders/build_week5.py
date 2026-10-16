"""Week 5 (Day 29-35): 예외 처리, 파일 입출력, 미니 프로젝트. Expected values come from independent reference code below."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import code, ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402

W = 5


# ---------------------------------------------------------------- reference implementations

def ref_sum_valid(rows):
    total = bad = 0
    for r in rows:
        try:
            total += int(r)
        except ValueError:
            bad += 1
    return lines(f"합계: {total}", f"잘못된 입력: {bad}개")


def ref_transfer(accounts, sender, receiver, amount):
    accounts = dict(accounts)
    if sender not in accounts or receiver not in accounts:
        raise KeyError
    if amount <= 0 or accounts[sender] < amount:
        raise ValueError
    accounts[sender] -= amount
    accounts[receiver] += amount
    return accounts


def ref_diary(entries):
    body = [f"{i}. {e}" for i, e in enumerate(entries, start=1)]
    return lines(*body, f"총 {len(entries)}줄 저장")


def ref_subjects(rows):
    groups, skipped = {}, 0
    for row in rows:
        parts = row.split(",")
        try:
            if len(parts) != 3:
                raise ValueError
            name, subject, score = parts
            score = int(score)
        except ValueError:
            skipped += 1
            continue
        groups.setdefault(subject, []).append(score)
    out = [f"{s}: 평균 {sum(v) / len(v):.1f}점 ({len(v)}명)" for s, v in sorted(groups.items())]
    return lines(*out, f"건너뛴 줄: {skipped}")


def ref_clean(text_):
    return "".join(ch if ch.isalnum() else " " for ch in text_.lower())


def ref_wordfreq(text_lines, k):
    words = ref_clean(" ".join(text_lines)).split()
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    return lines(f"총 단어 수: {len(words)}", f"서로 다른 단어: {len(counts)}",
                 *[f"{i}. {w} ({n})" for i, (w, n) in enumerate(top, start=1)])


def ref_ledger(cmds):
    balance, spent, out = 0, {}, []
    for line in cmds:
        if line.strip() == "잔액":
            out.append(f"잔액: {balance:,}원")
            continue
        parts = line.split()
        try:
            if len(parts) != 3:
                raise ValueError
            kind, cat, amount = parts[0], parts[1], int(parts[2])
            if kind not in ("수입", "지출") or amount <= 0:
                raise ValueError
        except ValueError:
            out.append(f"잘못된 입력: {line}")
            continue
        if kind == "수입":
            balance += amount
        else:
            balance -= amount
            spent[cat] = spent.get(cat, 0) + amount
    out.append("지출 내역")
    if not spent:
        out.append("- 없음")
    for cat, amt in sorted(spent.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"- {cat}: {amt:,}원")
    return lines(*out)


def ref_library(books, cmds):
    books = books.split(",")
    available = {b: True for b in books}
    out = []
    for line in cmds:
        cmd, _, title = line.partition(" ")
        if cmd == "대출":
            if title not in available:
                out.append(f"없는 책: {title}")
            elif not available[title]:
                out.append(f"이미 대출 중: {title}")
            else:
                available[title] = False
                out.append(f"대출 완료: {title}")
        elif cmd == "반납":
            if available.get(title, True):
                out.append(f"대출 기록 없음: {title}")
            else:
                available[title] = True
                out.append(f"반납 완료: {title}")
        elif cmd == "목록":
            free = sorted(b for b, ok in available.items() if ok)
            out.append("대출 가능: " + (", ".join(free) if free else "없음"))
        else:
            out.append(f"알 수 없는 명령: {line}")
    return lines(*out)


def ref_total_size(tree):
    return sum(ref_total_size(v) if isinstance(v, dict) else v for v in tree.values())


# ====================================================================== Day 29
valid_cases = [["10", "abc", "-3", "4.5", "7"], ["1"], ["x", "y"], []]


def n_stdin(rows):
    return lines(len(rows), *rows)


day29 = lesson(
    29, "예외 처리 try/except", W, ["try_except", "exception", "type_conversion"],
    ["try/except로 오류가 나도 프로그램이 멈추지 않게 할 수 있다.", "else, finally, as e의 쓰임을 설명할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "4주차에는 함수를 깊이 다뤘습니다. 지금까지는 `raise ValueError`로 오류를 **발생**시키기만 했는데, "
        "이번 주는 발생한 오류를 **잡아서 처리**하는 법부터 시작합니다."),
        "quiz": [quiz("d29_review_q1", "`int(\"3.5\")`를 실행하면?", ["3", "3.5", "4", "`ValueError`"], 3,
                      "`int()`는 소수점이 있는 문자열을 바로 바꾸지 못합니다. `int(float(\"3.5\"))`처럼 두 단계로 바꿔야 합니다.")]},
    concept={"title": "오류를 잡아서 처리하기", "blocks": [
        text("`try:` 블록에서 오류(예외)가 나면 그 즉시 실행을 멈추고, 종류가 맞는 `except` 블록으로 건너뜁니다. 오류가 처리되면 프로그램은 계속 실행됩니다."),
        code('''
            try:
                n = int("abc")
                print("이 줄은 실행되지 않습니다")
            except ValueError:
                print("숫자가 아닙니다")
            print("프로그램 계속")
        ''', lines("숫자가 아닙니다", "프로그램 계속")),
        text("`else`는 오류가 **없을 때**, `finally`는 오류가 있든 없든 **항상** 실행됩니다. `except 오류 as e`로 오류 메시지를 받을 수 있습니다."),
        code('''
            def safe_divide(a, b):
                try:
                    result = a / b
                except ZeroDivisionError:
                    return None
                else:
                    return round(result, 2)
                finally:
                    print("계산 시도:", a, b)

            print(safe_divide(10, 3))
            print(safe_divide(1, 0))
        ''', lines("계산 시도: 10 3", round(10 / 3, 2), "계산 시도: 1 0", None)),
        code('''
            try:
                [1, 2][5]
            except IndexError as e:
                print("오류:", e)
        ''', lines("오류: list index out of range")),
        tip("`except:`처럼 종류를 쓰지 않거나 `except Exception:`으로 모든 오류를 한꺼번에 잡으면 오타 같은 진짜 버그까지 숨겨집니다. "
            "**예상되는 오류만** 골라서 잡으세요."),
    ]},
    fill_intro="변환에 실패하면 기본값을 돌려주는 함수를 완성하세요.",
    coding_intro="잘못된 입력이 섞여 있어도 끝까지 처리합니다. `try`를 사용하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`try:` → 오류 발생 시 `except 종류:`로 이동, 이후 프로그램 계속.",
        "`else`: 오류가 없을 때, `finally`: 항상 실행.",
        "`except ValueError as e`: 오류 메시지 사용.",
        "예상되는 오류 종류만 잡는다."],
        "quiz": [
            quiz("d29_summary_q1", "다음 코드의 출력은?\n```python\ntry:\n    print(1)\n    x = 1 / 0\n    print(2)\nexcept ZeroDivisionError:\n    print(3)\n```",
                 ["1 2 3", "1 3", "3", "1"], 1, "오류가 난 줄 이후의 `try` 블록은 건너뛰고 `except`로 이동합니다."),
            quiz("d29_summary_q2", "오류가 있든 없든 항상 실행되는 블록은?", ["`else`", "`except`", "`finally`", "`try`"], 2,
                 "`finally`는 정리 작업(파일 닫기 등)에 씁니다.")]},
    exercises=[
        ex("d29_fill_1", "fill_blank", "안전한 정수 변환",
           "문자열을 정수로 바꿔 **반환**하세요. 바꿀 수 없으면 `default`(기본값 0)를 반환합니다.\n\n"
           "예: `to_int(\"42\")` → `42`, `to_int(\"abc\")` → `0`, `to_int(\"abc\", default=-1)` → `-1`",
           ["try_except", "type_conversion"], 1,
           '''
            def to_int(text, default=0):
                ____:
                    return int(text)
                except ____:
                    return default
           ''',
           [t("t1", args=["42"], ret=42, desc="숫자"), t("t2", args=["abc"], ret=0, desc="문자"),
            t("h1", args=["abc"], kwargs={"default": -1}, ret=-1), t("h2", args=[" 7 "], ret=7), t("h3", args=["3.5"], ret=0)],
           ["오류가 날 수도 있는 코드를 감싸는 키워드를 쓰세요.", "`int(\"abc\")`가 내는 오류의 종류를 떠올려 보세요."],
           '''
            def to_int(text, default=0):
                try:
                    return int(text)
                except ValueError:
                    return default
           ''', mode="function", name="to_int"),
        ex("d29_code_1", "coding", "올바른 숫자만 더하기",
           "첫째 줄에 줄 수 `n`, 다음 `n`줄에 값이 하나씩 주어집니다. **정수로 바꿀 수 있는 값만** 더하고, 바꿀 수 없는 줄의 수를 셉니다.\n\n"
           "**입력 예시**\n```\n" + n_stdin(valid_cases[0]) + "```\n**출력 예시**\n```\n" + ref_sum_valid(valid_cases[0]) + "```\n"
           "(`4.5`는 정수가 아니므로 잘못된 입력입니다.)",
           ["try_except", "accumulation", "fstring"], 2,
           '''
            n = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=n_stdin(valid_cases[0]), out=ref_sum_valid(valid_cases[0]), desc="섞인 입력")]
           + [t(f"h{i}", stdin=n_stdin(v), out=ref_sum_valid(v)) for i, v in enumerate(valid_cases[1:], start=1)],
           ["합계와 잘못된 입력 수를 담을 변수 두 개를 0으로 준비하세요.",
            "반복문 안에서 `int(input())`을 `try`로 감싸고, 실패하면 잘못된 입력 수를 1 늘립니다.",
            "출력은 f-string 두 줄입니다."],
           '''
            n = int(input())
            total = 0
            bad = 0
            for _ in range(n):
                try:
                    total += int(input())
                except ValueError:
                    bad += 1
            print(f"합계: {total}")
            print(f"잘못된 입력: {bad}개")
           ''', checks={"required_syntax": ["try", "for"], "max_lines": 12}),
    ])

# ====================================================================== Day 30
acc = {"민준": 10000, "서연": 5000}
transfer_cases = [((acc, "민준", "서연", 3000), "t1", "정상 이체"), ((acc, "서연", "민준", 5000), "h1", "")]
day30 = lesson(
    30, "예외 발생시키기와 전달", W, ["custom_exception", "try_except", "exception", "dict"],
    ["raise로 의미 있는 메시지와 함께 예외를 발생시킬 수 있다.", "함수에서 발생한 예외를 호출한 쪽에서 처리할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `try/except`로 오류를 잡아 프로그램이 멈추지 않게 했습니다.",
            "quiz": [quiz("d30_review_q1", "`except ValueError as e:`에서 `e`에 담기는 것은?", ["오류 줄 번호", "오류 객체(메시지 포함)", "`True`", "변수 이름"], 1,
                          "`print(e)`로 메시지를 볼 수 있습니다.")]},
    concept={"title": "문제를 알리고, 위에서 처리하기", "blocks": [
        text("함수가 처리할 수 없는 상황에서는 `raise`로 예외를 발생시켜 **호출한 쪽**에 알립니다. 예외는 `try`를 만날 때까지 호출한 함수들을 거슬러 올라갑니다."),
        code('''
            def withdraw(balance, amount):
                if amount > balance:
                    raise ValueError("잔액이 부족합니다")
                return balance - amount

            try:
                withdraw(1000, 5000)
            except ValueError as e:
                print("실패:", e)
            print(withdraw(1000, 300))
        ''', lines("실패: 잔액이 부족합니다", 700)),
        text("직접 예외 종류를 만들 수도 있습니다. `class 이름(Exception): pass` 두 줄이면 됩니다. class 문법은 6주차에 자세히 배웁니다."),
        code('''
            class InvalidAgeError(Exception):
                pass

            def check_age(age):
                if age < 0:
                    raise InvalidAgeError(f"나이는 음수일 수 없습니다: {age}")
                return age

            try:
                check_age(-3)
            except InvalidAgeError as e:
                print(e)
        ''', lines("나이는 음수일 수 없습니다: -3")),
        text("예외를 잡은 뒤 더 알기 쉬운 메시지로 **다시 발생**시킬 수도 있습니다."),
        code('''
            def parse_age(text):
                try:
                    return int(text)
                except ValueError:
                    raise ValueError(f"'{text}'는 나이가 아닙니다")

            for t in ["20", "스물"]:
                try:
                    print(parse_age(t))
                except ValueError as e:
                    print("오류:", e)
        ''', lines(20, "오류: '스물'는 나이가 아닙니다")),
        tip("오류를 잡아서 아무것도 하지 않고 넘기면(`except: pass`) 문제가 숨겨집니다. 처리할 수 없다면 그냥 위로 올려 보내는 것이 낫습니다."),
    ]},
    fill_intro="범위를 벗어난 값에 예외를 발생시키세요.",
    coding_intro="여러 종류의 예외를 상황에 맞게 발생시킵니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`raise 예외종류(\"메시지\")`로 문제를 알린다.",
        "예외는 `try`를 만날 때까지 호출한 쪽으로 올라간다.",
        "`class MyError(Exception): pass`로 새 예외 종류를 만든다.",
        "처리할 수 없는 예외는 숨기지 말고 위로 보낸다."],
        "quiz": [
            quiz("d30_summary_q1", "없는 키를 찾을 때 발생시키기에 가장 알맞은 예외는?", ["`ValueError`", "`KeyError`", "`IndexError`", "`TypeError`"], 1,
                 "딕셔너리 키 관련 문제는 `KeyError`가 자연스럽습니다."),
            quiz("d30_summary_q2", "함수 안에서 `raise`된 예외를 그 함수가 잡지 않으면?", ["무시된다", "호출한 쪽으로 전달된다", "`None`이 반환된다", "자동으로 다시 실행된다"], 1,
                 "호출한 쪽의 `try`가 잡거나, 끝까지 아무도 안 잡으면 프로그램이 멈춥니다.")]},
    exercises=[
        ex("d30_fill_1", "fill_blank", "점수 검사",
           "점수가 0 이상 100 이하이면 그대로 **반환**하고, 아니면 `ValueError`를 발생시키세요.",
           ["custom_exception", "condition"], 1,
           '''
            def check_score(score):
                if not 0 <= score <= 100:
                    ____ ____("점수는 0~100 사이여야 합니다")
                return score
           ''',
           [t("t1", args=[50], ret=50, desc="정상"), t("t2", args=[101], raises="ValueError", desc="100 초과"),
            t("h1", args=[0], ret=0), t("h2", args=[-1], raises="ValueError"), t("h3", args=[100], ret=100)],
           ["예외를 발생시키는 키워드를 쓰세요.", "값의 범위가 잘못되었을 때 쓰는 예외 종류입니다."],
           '''
            def check_score(score):
                if not 0 <= score <= 100:
                    raise ValueError("점수는 0~100 사이여야 합니다")
                return score
           ''', mode="function", name="check_score"),
        ex("d30_code_1", "coding", "계좌 이체",
           "계좌 딕셔너리(이름 → 잔액)에서 `sender`가 `receiver`에게 `amount`원을 보낸 뒤 딕셔너리를 **반환**하세요.\n\n"
           "- 보내는 사람이나 받는 사람이 없으면 `KeyError`\n- 금액이 0 이하이거나 잔액보다 많으면 `ValueError`\n\n"
           "예: `transfer({\"민준\": 10000, \"서연\": 5000}, \"민준\", \"서연\", 3000)` → `{\"민준\": 7000, \"서연\": 8000}`",
           ["custom_exception", "dict", "exception"], 2,
           '''
            def transfer(accounts, sender, receiver, amount):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[dict(a[0]), *a[1:]], ret=ref_transfer(*a), desc=d) for a, tid, d in transfer_cases if tid[0] == "t"]
           + [t("t2", args=[dict(acc), "민준", "하나", 1000], raises="KeyError", desc="없는 계좌"),
              t("t3", args=[dict(acc), "서연", "민준", 9000], raises="ValueError", desc="잔액 부족")]
           + [t(tid, args=[dict(a[0]), *a[1:]], ret=ref_transfer(*a)) for a, tid, d in transfer_cases if tid[0] == "h"]
           + [t("h2", args=[dict(acc), "없음", "민준", 1], raises="KeyError"), t("h3", args=[dict(acc), "민준", "서연", 0], raises="ValueError")],
           ["두 사람이 모두 딕셔너리에 있는지 `in`으로 먼저 확인하세요.",
            "금액 검사(0 이하, 잔액 초과)는 그다음입니다. 조건에 맞는 예외 종류를 고르세요.",
            "모든 검사를 통과한 뒤에만 잔액을 바꿉니다."],
           '''
            def transfer(accounts, sender, receiver, amount):
                if sender not in accounts or receiver not in accounts:
                    raise KeyError("없는 계좌입니다")
                if amount <= 0 or accounts[sender] < amount:
                    raise ValueError("이체할 수 없는 금액입니다")
                accounts[sender] -= amount
                accounts[receiver] += amount
                return accounts
           ''', mode="function", name="transfer", checks={"required_syntax": ["def", "if"], "max_lines": 10}),
    ])

# ====================================================================== Day 31
diary_cases = [["오늘은 파이썬 공부", "예외 처리를 배웠다"], ["한 줄"], ["가", "나", "다", "라"]]
day31 = lesson(
    31, "파일 읽고 쓰기", W, ["file_io", "try_except", "for_loop"],
    ["open()과 with로 텍스트 파일을 쓰고 읽을 수 있다.", "쓰기(w)·추가(a)·읽기(r) 모드와 인코딩을 구분할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `raise`로 문제를 알리고 호출한 쪽에서 처리했습니다.",
            "quiz": [quiz("d31_review_q1", "새 예외 종류를 만드는 코드는?", ["`def MyError(): pass`", "`class MyError(Exception): pass`", "`raise MyError`", "`MyError = Exception()`"], 1,
                          "`Exception`을 바탕으로 하는 class를 만듭니다.")]},
    concept={"title": "프로그램이 끝나도 남는 데이터", "blocks": [
        text("`open(파일이름, 모드, encoding=\"utf-8\")`으로 파일을 엽니다. `with` 문을 쓰면 블록이 끝날 때 파일이 **자동으로 닫힙니다**. "
             "모드: `\"w\"` 새로 쓰기(기존 내용 삭제), `\"a\"` 끝에 추가, `\"r\"`(생략 가능) 읽기."),
        code('''
            with open("memo.txt", "w", encoding="utf-8") as f:
                f.write("첫 줄\\n")
                f.write("둘째 줄\\n")

            with open("memo.txt", encoding="utf-8") as f:
                content = f.read()
            print(content)
        ''', lines("첫 줄", "둘째 줄", "")),
        text("파일 객체를 `for`로 돌리면 한 줄씩 읽습니다. 각 줄 끝에는 줄바꿈 `\\n`이 붙어 있으니 `strip()`으로 정리하세요."),
        code('''
            with open("log.txt", "w", encoding="utf-8") as f:
                f.write("시작\\n")
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write("추가\\n")
            with open("log.txt", encoding="utf-8") as f:
                for i, line in enumerate(f, start=1):
                    print(i, line.strip())
        ''', lines("1 시작", "2 추가")),
        code('''
            try:
                open("없는파일.txt", encoding="utf-8")
            except FileNotFoundError:
                print("파일이 없습니다")
        ''', lines("파일이 없습니다")),
        tip("Windows에서 `encoding`을 빼면 한글이 깨지거나 오류가 날 수 있습니다. 항상 `encoding=\"utf-8\"`을 쓰세요. "
            "`write()`는 줄바꿈을 자동으로 넣지 않습니다. 이 앱에서 실행한 코드는 매번 새 임시 폴더에서 돌기 때문에 만든 파일은 실행이 끝나면 지워집니다."),
    ]},
    fill_intro="파일에 쓰고 다시 읽어 줄 수를 세는 함수를 완성하세요.",
    coding_intro="입력한 내용을 파일에 저장한 뒤, **파일에서 다시 읽어** 출력합니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`with open(이름, 모드, encoding=\"utf-8\") as f:`, 블록이 끝나면 자동으로 닫힘.",
        "`\"w\"` 덮어쓰기, `\"a\"` 이어쓰기, `\"r\"` 읽기.",
        "`f.write()`는 줄바꿈을 직접 넣어야 하고, `f.read()`·`for line in f`로 읽는다.",
        "없는 파일을 열면 `FileNotFoundError`."],
        "quiz": [
            quiz("d31_summary_q1", "기존 내용을 지우지 않고 끝에 덧붙이는 모드는?", ["`\"w\"`", "`\"r\"`", "`\"a\"`", "`\"x\"`"], 2, "append의 a입니다."),
            quiz("d31_summary_q2", "`with` 문을 쓰는 가장 큰 이유는?", ["속도가 빨라서", "파일을 자동으로 닫아 줘서", "인코딩이 필요 없어서", "파일이 없으면 만들어 줘서"], 1,
                 "오류가 나도 블록을 벗어나면 파일이 닫힙니다.")]},
    exercises=[
        ex("d31_fill_1", "fill_blank", "저장하고 줄 수 세기",
           "문자열 리스트 `lines`를 한 줄씩 `path` 파일에 **새로 쓴 뒤**, 그 파일을 다시 열어 줄 수를 **반환**하세요.\n\n"
           "예: `save_and_count(\"a.txt\", [\"x\", \"y\"])` → `2`",
           ["file_io"], 1,
           '''
            def save_and_count(path, lines):
                with open(path, "____", encoding="utf-8") as f:
                    for line in lines:
                        f.write(line + "\\n")
                with ____(path, encoding="utf-8") as f:
                    return len(f.readlines())
           ''',
           [t("t1", args=["a.txt", ["x", "y"]], ret=2, desc="두 줄"), t("h1", args=["b.txt", []], ret=0),
            t("h2", args=["c.txt", ["한 줄"]], ret=1), t("h3", args=["a.txt", ["1", "2", "3"]], ret=3)],
           ["기존 내용을 지우고 새로 쓰는 모드 글자를 쓰세요.", "파일을 여는 내장 함수 이름입니다."],
           '''
            def save_and_count(path, lines):
                with open(path, "w", encoding="utf-8") as f:
                    for line in lines:
                        f.write(line + "\\n")
                with open(path, encoding="utf-8") as f:
                    return len(f.readlines())
           ''', mode="function", name="save_and_count"),
        ex("d31_code_1", "coding", "일기장 파일",
           "첫째 줄에 줄 수 `n`, 다음 `n`줄에 일기 내용이 주어집니다.\n\n"
           "1. 각 줄을 `번호. 내용` 형식으로 `diary.txt`에 저장합니다(번호는 1부터).\n"
           "2. 파일을 **다시 열어** 저장된 줄을 그대로 출력합니다.\n3. 마지막에 `총 n줄 저장`을 출력합니다.\n\n"
           "**입력 예시**\n```\n" + n_stdin(diary_cases[0]) + "```\n**출력 예시**\n```\n" + ref_diary(diary_cases[0]) + "```",
           ["file_io", "for_loop", "fstring"], 2,
           '''
            n = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=n_stdin(diary_cases[0]), out=ref_diary(diary_cases[0]), desc="두 줄")]
           + [t(f"h{i}", stdin=n_stdin(d), out=ref_diary(d)) for i, d in enumerate(diary_cases[1:], start=1)],
           ["쓰기 모드 `\"w\"`로 연 `with` 블록 안에서 `n`번 `input()`을 읽어 씁니다. 줄바꿈 `\\n`을 잊지 마세요.",
            "번호는 반복 변수에 1을 더하거나 `range(1, n + 1)`로 만들 수 있습니다.",
            "읽을 때는 `for line in f:`로 돌며 `line.strip()`을 출력합니다."],
           '''
            n = int(input())
            with open("diary.txt", "w", encoding="utf-8") as f:
                for i in range(1, n + 1):
                    f.write(f"{i}. {input()}\\n")
            with open("diary.txt", encoding="utf-8") as f:
                for line in f:
                    print(line.strip())
            print(f"총 {n}줄 저장")
           ''', checks={"required_syntax": ["with", "for"], "max_lines": 10}),
    ])

# ====================================================================== Day 32
csv_cases = [["민준,국어,90", "서연,수학,85", "지호,국어,70", "하나,수학,abc", "잘못된줄"],
             ["a,영어,100"], ["a,x,1", "b,x,2", "c,y,3", "d,y,,", "e,y,4"], []]


def csv_stdin(rows):
    return lines(len(rows), "이름,과목,점수", *rows)


day32 = lesson(
    32, "텍스트 데이터 처리", W, ["text_processing", "string_parsing", "dict", "try_except"],
    ["쉼표로 구분된 데이터(CSV)를 읽어 리스트·딕셔너리로 바꿀 수 있다.", "잘못된 행을 건너뛰며 집계할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `with open(...)`으로 파일을 쓰고 읽었습니다.",
            "quiz": [quiz("d32_review_q1", "파일에서 읽은 각 줄 끝의 `\\n`을 없애는 메서드는?", ["`split()`", "`strip()`", "`join()`", "`lower()`"], 1,
                          "`strip()`은 앞뒤 공백과 줄바꿈을 지웁니다.")]},
    concept={"title": "표 형태의 텍스트", "blocks": [
        text("**CSV**는 한 줄이 한 행이고 값이 쉼표로 구분된 텍스트 형식입니다. 엑셀에서도 열 수 있어 데이터 분석의 출발점이 됩니다. "
             "첫 줄은 보통 열 이름(헤더)입니다."),
        code('''
            data = """이름,국어,수학
            민준,90,80
            서연,85,95"""
            rows = data.split("\\n")
            header = rows[0].split(",")
            print(header)
            for row in rows[1:]:
                name, kor, mat = row.split(",")
                print(name, int(kor) + int(mat))
        ''', lines(["이름", "국어", "수학"], "민준 170", "서연 180")),
        text("헤더와 값을 `zip()`으로 짝지으면 행 하나를 딕셔너리로 만들 수 있습니다. 표준 모듈 `csv`는 따옴표 안의 쉼표 같은 까다로운 경우까지 처리해 줍니다."),
        code('''
            import csv

            with open("scores.csv", "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["이름", "점수"])
                writer.writerow(["민준", 90])

            with open("scores.csv", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    print(row)
        ''', lines({"이름": "민준", "점수": "90"})),
        tip("파일이나 입력에서 읽은 값은 **모두 문자열**입니다. 계산하려면 `int()`/`float()`로 바꾸고, 바꿀 수 없는 행은 `try/except`로 건너뛰세요. "
            "실제 데이터에는 빈 칸, 오타, 열 개수가 다른 행이 흔합니다."),
    ]},
    fill_intro="헤더와 한 행을 짝지어 딕셔너리로 만드세요.",
    coding_intro="과목별 평균을 구하고, 잘못된 행은 건너뛴 뒤 개수를 보고합니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "CSV 한 줄 → `line.split(\",\")` → 값 리스트.",
        "`dict(zip(헤더, 값들))`로 행을 딕셔너리로.",
        "읽은 값은 문자열 → 숫자 변환 + `try/except`로 잘못된 행 처리.",
        "`csv` 모듈의 `reader`/`DictReader`/`writer`를 쓰면 더 안전하다."],
        "quiz": [
            quiz("d32_summary_q1", "`dict(zip([\"a\", \"b\"], [1, 2]))`의 결과는?", ["`{'a': 1, 'b': 2}`", "`[('a', 1), ('b', 2)]`", "`{'a': 'b'}`", "오류"], 0,
                 "`zip`이 짝지은 (키, 값)들로 딕셔너리를 만듭니다."),
            quiz("d32_summary_q2", "`\"민준,90\".split(\",\")[1]`의 자료형은?", ["`int`", "`float`", "`str`", "`list`"], 2,
                 "나눈 결과는 문자열 리스트입니다. 숫자로 쓰려면 변환해야 합니다.")]},
    exercises=[
        ex("d32_fill_1", "fill_blank", "행을 딕셔너리로",
           "열 이름 리스트 `header`와 CSV 한 줄 `line`을 받아 `{열 이름: 값}` 딕셔너리를 **반환**하세요.\n\n"
           "예: `to_record([\"이름\", \"나이\"], \"민준,20\")` → `{\"이름\": \"민준\", \"나이\": \"20\"}`",
           ["text_processing", "string_parsing", "enumerate_zip"], 1,
           '''
            def to_record(header, line):
                values = line.____(",")
                return dict(____(header, values))
           ''',
           [t("t1", args=[["이름", "나이"], "민준,20"], ret={"이름": "민준", "나이": "20"}, desc="기본"),
            t("h1", args=[["a"], "x"], ret={"a": "x"}), t("h2", args=[["k", "v", "w"], "1,,3"], ret={"k": "1", "v": "", "w": "3"})],
           ["문자열을 구분자로 나누는 메서드입니다.", "두 리스트를 같은 위치끼리 짝지어 주는 내장 함수입니다 (Day 13)."],
           '''
            def to_record(header, line):
                values = line.split(",")
                return dict(zip(header, values))
           ''', mode="function", name="to_record"),
        ex("d32_code_1", "coding", "과목별 평균",
           "첫째 줄에 데이터 행 수 `n`, 둘째 줄에 헤더 `이름,과목,점수`, 그다음 `n`줄에 데이터가 주어집니다.\n\n"
           "- 과목별 평균을 과목 이름 사전 순으로 `과목: 평균 85.0점 (2명)` 형식으로 출력합니다.\n"
           "- 값이 3개가 아니거나 점수가 정수가 아닌 행은 건너뛰고, 마지막에 `건너뛴 줄: k`를 출력합니다.\n\n"
           "**입력 예시**\n```\n" + csv_stdin(csv_cases[0]) + "```\n**출력 예시**\n```\n" + ref_subjects(csv_cases[0]) + "```",
           ["text_processing", "dict", "try_except", "formatting"], 3,
           '''
            n = int(input())
            header = input()
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=csv_stdin(csv_cases[0]), out=ref_subjects(csv_cases[0]), desc="잘못된 행 포함")]
           + [t(f"h{i}", stdin=csv_stdin(r), out=ref_subjects(r)) for i, r in enumerate(csv_cases[1:], start=1)],
           ["과목 → 점수 리스트 딕셔너리(Day 17의 그룹화)와 건너뛴 줄 수를 준비하세요.",
            "`split(\",\")` 결과의 길이 검사와 `int()` 변환을 `try` 안에 두고, 길이가 3이 아니면 직접 `raise ValueError`를 하면 처리가 한곳으로 모입니다.",
            "출력할 때는 `sorted(딕셔너리)`로 과목을 정렬하고 평균을 `:.1f`로 맞춥니다."],
           '''
            n = int(input())
            header = input()
            groups = {}
            skipped = 0
            for _ in range(n):
                parts = input().split(",")
                try:
                    if len(parts) != 3:
                        raise ValueError("열 개수 오류")
                    name, subject, score = parts
                    score = int(score)
                except ValueError:
                    skipped += 1
                    continue
                if subject not in groups:
                    groups[subject] = []
                groups[subject].append(score)
            for subject in sorted(groups):
                scores = groups[subject]
                print(f"{subject}: 평균 {sum(scores) / len(scores):.1f}점 ({len(scores)}명)")
            print(f"건너뛴 줄: {skipped}")
           ''', checks={"required_syntax": ["try", "for"]}),
    ])

# ====================================================================== Day 33 (mini project 1)
wf_cases = [(["The cat sat on the mat.", "The dog sat, too!"], 3), (["Hello"], 5), (["b a, B A! c"], 2), (["파이썬, 파이썬! 자바"], 1)]


def wf_stdin(text_lines, k):
    return lines(f"{len(text_lines)} {k}", *text_lines)


day33 = lesson(
    33, "미니 프로젝트 1: 단어 빈도 분석", W, ["text_processing", "dict", "lambda", "string_method", "function"],
    ["문제를 입력 → 정리 → 세기 → 정렬 → 출력 단계로 나눠 구현할 수 있다.", "지금까지 배운 문자열·딕셔너리·정렬을 하나의 프로그램으로 조합할 수 있다."],
    review={"title": "프로젝트 준비", "content_md": (
        "오늘과 내일은 **미니 프로젝트**입니다. 새 문법보다 지금까지 배운 것을 조합하는 연습을 합니다.\n\n"
        "오늘 만들 것: 여러 줄의 영어·한글 문장을 받아 **가장 많이 쓰인 단어 순위**를 보여 주는 분석기."),
        "quiz": [quiz("d33_review_q1", "횟수 내림차순, 같으면 단어 오름차순으로 (단어, 횟수)를 정렬하는 key는?",
                      ["`lambda kv: kv[1]`", "`lambda kv: (-kv[1], kv[0])`", "`lambda kv: (kv[0], -kv[1])`", "`len`"], 1,
                      "Day 25에서 배운 여러 기준 정렬입니다.")]},
    concept={"title": "단계별로 나눠 만들기", "blocks": [
        text("큰 문제는 작은 함수로 나누면 쉬워집니다.\n\n"
             "1. **정리**: 소문자로 바꾸고 문장부호를 공백으로 바꾼다 → `clean(text)`\n"
             "2. **나누기**: `split()`으로 단어 목록\n"
             "3. **세기**: 딕셔너리 개수 세기 패턴\n"
             "4. **정렬**: 횟수 내림차순, 단어 오름차순\n"
             "5. **출력**: 상위 k개를 f-string으로"),
        code('''
            def clean(text):
                result = ""
                for ch in text.lower():
                    if ch.isalnum():
                        result += ch
                    else:
                        result += " "
                return result

            words = clean("Hi, hi! Bye.").split()
            print(words)
        ''', lines(["hi", "hi", "bye"])),
        tip("문장부호를 지우지 않고 **공백으로 바꾸는** 이유: `\"cat,dog\"`처럼 붙어 있는 단어를 나눌 수 있기 때문입니다. `split()`은 여러 칸 공백을 알아서 처리합니다."),
    ]},
    fill_intro="1단계 `clean()` 함수를 완성하세요.",
    coding_intro="전체 분석기를 완성합니다. 함수를 나눠 작성해 보세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "큰 문제는 단계(함수)로 나눈다: 정리 → 나누기 → 세기 → 정렬 → 출력.",
        "문장부호는 공백으로 바꾼 뒤 `split()`.",
        "정렬 기준은 `(-횟수, 단어)`.",
        "각 함수를 따로 실행해 보며 확인하면 디버깅이 쉽다."],
        "quiz": [
            quiz("d33_summary_q1", "`\"a.b\"`를 `clean()`(문장부호→공백) 후 `split()`하면?", ["`['a.b']`", "`['a', 'b']`", "`['ab']`", "`['a', '.', 'b']`"], 1,
                 "`.`이 공백이 되어 두 단어로 나뉩니다."),
            quiz("d33_summary_q2", "단어 목록 `[\"a\", \"b\", \"a\"]`의 서로 다른 단어 수를 구하는 가장 간단한 방법은?",
                 ["`len(words)`", "`len(set(words))`", "`words.count()`", "`max(words)`"], 1, "집합으로 중복을 없앤 뒤 개수를 셉니다.")]},
    exercises=[
        ex("d33_fill_1", "fill_blank", "텍스트 정리",
           "문자열을 소문자로 바꾸고, 글자나 숫자가 아닌 문자(문장부호·공백 등)는 모두 공백 한 칸으로 바꾼 결과를 **반환**하세요.\n\n"
           "예: `clean(\"Hello, World!\")` → `\"hello  world \"`",
           ["text_processing", "string_method"], 1,
           '''
            def clean(text):
                result = ""
                for ch in text.lower():
                    if ch.____():
                        result += ch
                    else:
                        result += ____
                return result
           ''',
           [t("t1", args=["Hello, World!"], ret=ref_clean("Hello, World!"), desc="문장부호"),
            t("h1", args=[""], ret=""), t("h2", args=["파이썬3.14!"], ret=ref_clean("파이썬3.14!")), t("h3", args=["A-B_C"], ret=ref_clean("A-B_C"))],
           ["글자이거나 숫자인지 한 번에 검사하는 문자열 메서드가 있습니다 (alpha + numeric).", "그 밖의 문자는 무엇으로 바꾸기로 했나요?"],
           '''
            def clean(text):
                result = ""
                for ch in text.lower():
                    if ch.isalnum():
                        result += ch
                    else:
                        result += " "
                return result
           ''', mode="function", name="clean"),
        ex("d33_code_1", "coding", "단어 빈도 분석기",
           "첫째 줄에 `m k`(문장 줄 수, 출력할 순위 수), 다음 `m`줄에 문장이 주어집니다.\n\n"
           "1. 모든 줄을 소문자로 바꾸고 글자·숫자가 아닌 문자를 공백으로 바꾼 뒤 단어로 나눕니다.\n"
           "2. `총 단어 수: X`, `서로 다른 단어: Y`를 출력합니다.\n"
           "3. 횟수가 많은 순(같으면 단어 사전 순)으로 상위 `k`개를 `순위. 단어 (횟수)` 형식으로 출력합니다. 단어 종류가 `k`개보다 적으면 있는 만큼만 출력합니다.\n\n"
           "**입력 예시**\n```\n" + wf_stdin(*wf_cases[0]) + "```\n**출력 예시**\n```\n" + ref_wordfreq(*wf_cases[0]) + "```",
           ["text_processing", "dict", "lambda", "fstring"], 3,
           '''
            def clean(text):
                # 빈칸 채우기에서 만든 함수를 활용하세요
                pass


            m, k = input().split()
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=wf_stdin(*wf_cases[0]), out=ref_wordfreq(*wf_cases[0]), desc="두 문장")]
           + [t(f"h{i}", stdin=wf_stdin(*c_), out=ref_wordfreq(*c_)) for i, c_ in enumerate(wf_cases[1:], start=1)],
           ["`m`, `k`를 정수로 바꾼 뒤, `m`줄을 읽어 `clean()`한 결과를 `split()`해서 하나의 단어 리스트에 모으세요(`extend`).",
            "단어별 개수는 `counts.get(w, 0) + 1` 패턴으로 셉니다.",
            "`sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]`처럼 정렬 후 앞에서 k개를 자르고, `enumerate(..., start=1)`로 순위를 붙입니다."],
           '''
            def clean(text):
                result = ""
                for ch in text.lower():
                    if ch.isalnum():
                        result += ch
                    else:
                        result += " "
                return result


            m, k = input().split()
            words = []
            for _ in range(int(m)):
                words.extend(clean(input()).split())
            counts = {}
            for w in words:
                counts[w] = counts.get(w, 0) + 1
            print(f"총 단어 수: {len(words)}")
            print(f"서로 다른 단어: {len(counts)}")
            ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            for i, (word, count) in enumerate(ranked[:int(k)], start=1):
                print(f"{i}. {word} ({count})")
           ''', checks={"required_syntax": ["def", "for", "lambda"]}),
    ])

# ====================================================================== Day 34 (mini project 2)
ledger_cases = [["수입 급여 3000000", "지출 식비 12000", "지출 교통 1250", "지출 식비 8000", "잔액", "지출 식비 -500", "외식 30000"],
                ["잔액"], ["수입 용돈 abc", "지출 책 15000", "지출 카페 4500", "지출 책 15000", "잔액"],
                ["지출 a 10", "지출 b 10", "잔액"]]
day34 = lesson(
    34, "미니 프로젝트 2: 가계부", W, ["function", "try_except", "dict", "formatting", "string_parsing"],
    ["명령어를 해석해 상태(잔액, 항목별 합계)를 갱신하는 프로그램을 만들 수 있다.", "잘못된 입력을 예외 처리로 걸러낼 수 있다."],
    review={"title": "프로젝트 준비", "content_md": (
        "오늘은 **명령어로 동작하는 가계부**를 만듭니다. 입력 한 줄이 명령 하나입니다.\n\n"
        "| 명령 | 동작 |\n|---|---|\n"
        "| `수입 항목 금액` | 잔액 증가 |\n| `지출 항목 금액` | 잔액 감소, 항목별 지출 합계 기록 |\n"
        "| `잔액` | 현재 잔액 출력 |\n| 그 밖 | `잘못된 입력: …` 출력 |"),
        "quiz": [quiz("d34_review_q1", "`\"지출 식비 12000\".split()`의 결과는?", ["`['지출 식비 12000']`", "`['지출', '식비', '12000']`", "`['지출', '식비', 12000]`", "오류"], 1,
                      "공백으로 나눈 **문자열** 세 개입니다. 금액은 `int()`로 바꿔야 합니다.")]},
    concept={"title": "명령 처리 구조", "blocks": [
        text("명령어 프로그램은 보통 **해석(parse) → 실행 → 출력**의 반복입니다. 해석 단계에서 형식이 틀리면 예외를 발생시키고, 반복문에서 그 예외를 잡아 안내 문구를 출력하면 구조가 깔끔해집니다."),
        code('''
            def parse(line):
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError("형식 오류")
                return parts[0], int(parts[1])

            for line in ["더하기 5", "빼기", "더하기 x"]:
                try:
                    cmd, n = parse(line)
                    print("실행:", cmd, n)
                except ValueError:
                    print("잘못된 입력:", line)
        ''', lines("실행: 더하기 5", "잘못된 입력: 빼기", "잘못된 입력: 더하기 x")),
        tip("`int(\"x\")`도 `ValueError`를 내므로, 형식 오류와 숫자 오류를 `except ValueError` 하나로 함께 처리할 수 있습니다."),
    ]},
    fill_intro="명령 한 줄을 해석하는 `parse_command()`를 완성하세요.",
    coding_intro="가계부 전체를 완성합니다. `parse_command()`를 재사용하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "명령 프로그램 = 해석 → 실행 → 출력의 반복.",
        "해석 함수는 잘못된 형식에 예외를 발생시키고, 반복문에서 잡는다.",
        "상태(잔액, 항목별 합계)는 변수와 딕셔너리로 관리한다.",
        "출력 서식은 `{x:,}`로 통일한다."],
        "quiz": [
            quiz("d34_summary_q1", "`except ValueError`로 함께 잡을 수 있는 것은?", ["`int(\"x\")` 실패", "없는 키 접근", "0으로 나누기", "없는 파일 열기"], 0,
                 "나머지는 각각 `KeyError`, `ZeroDivisionError`, `FileNotFoundError`입니다."),
            quiz("d34_summary_q2", "항목별 지출 합계를 저장하기 알맞은 자료형은?", ["리스트", "집합", "딕셔너리", "튜플"], 2, "항목 이름 → 합계.")]},
    exercises=[
        ex("d34_fill_1", "fill_blank", "명령 해석",
           "`\"종류 항목 금액\"` 한 줄을 해석해 `(종류, 항목, 금액)` 튜플을 **반환**하세요. 금액은 정수입니다.\n\n"
           "- 단어가 3개가 아니거나, 종류가 `수입`/`지출`이 아니거나, 금액이 0 이하이면 `ValueError`\n"
           "- 금액이 정수가 아니면 `int()`가 `ValueError`를 냅니다.",
           ["string_parsing", "try_except", "tuple"], 1,
           '''
            def parse_command(line):
                parts = line.split()
                if len(parts) != 3:
                    ____ ValueError("형식이 올바르지 않습니다")
                kind, category, amount = parts
                amount = ____(amount)
                if kind not in ("수입", "지출") or amount <= 0:
                    raise ValueError("잘못된 값입니다")
                return kind, category, amount
           ''',
           [t("t1", args=["지출 식비 12000"], ret=["지출", "식비", 12000], desc="정상"),
            t("t2", args=["잔액"], raises="ValueError", desc="단어 수"),
            t("h1", args=["수입 용돈 abc"], raises="ValueError"), t("h2", args=["지출 식비 -5"], raises="ValueError"),
            t("h3", args=["환불 식비 100"], raises="ValueError"), t("h4", args=["수입 급여 1"], ret=["수입", "급여", 1])],
           ["예외를 발생시키는 키워드입니다.", "금액 문자열을 정수로 바꾸는 내장 함수입니다."],
           '''
            def parse_command(line):
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError("형식이 올바르지 않습니다")
                kind, category, amount = parts
                amount = int(amount)
                if kind not in ("수입", "지출") or amount <= 0:
                    raise ValueError("잘못된 값입니다")
                return kind, category, amount
           ''', mode="function", name="parse_command"),
        ex("d34_code_1", "coding", "가계부",
           "첫째 줄에 명령 수 `n`, 다음 `n`줄에 명령이 주어집니다. 잔액은 0원에서 시작합니다(지출로 음수가 되어도 됩니다).\n\n"
           "- `잔액` → `잔액: 2,978,750원`\n- 해석할 수 없는 줄 → `잘못된 입력: (그 줄)`\n"
           "- 모든 명령 처리 후 `지출 내역`을 출력하고, 항목별 지출 합계를 많은 순(같으면 항목 이름 순)으로 `- 항목: 금액원` 형식으로 출력합니다. 지출이 없으면 `- 없음`.\n\n"
           "**입력 예시**\n```\n" + n_stdin(ledger_cases[0]) + "```\n**출력 예시**\n```\n" + ref_ledger(ledger_cases[0]) + "```",
           ["function", "try_except", "dict", "formatting", "lambda"], 3,
           '''
            def parse_command(line):
                # 빈칸 채우기에서 만든 함수를 활용하세요
                pass


            n = int(input())
            balance = 0
            spent = {}
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=n_stdin(ledger_cases[0]), out=ref_ledger(ledger_cases[0]), desc="여러 명령")]
           + [t(f"h{i}", stdin=n_stdin(c_), out=ref_ledger(c_)) for i, c_ in enumerate(ledger_cases[1:], start=1)],
           ["반복문에서 먼저 `잔액` 명령인지 확인하고, 아니면 `parse_command()`를 `try`로 감싸 호출하세요.",
            "지출이면 잔액을 줄이고 `spent[항목] = spent.get(항목, 0) + 금액`으로 기록합니다.",
            "마지막 지출 내역은 `sorted(spent.items(), key=lambda kv: (-kv[1], kv[0]))`로 정렬합니다."],
           '''
            def parse_command(line):
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError("형식이 올바르지 않습니다")
                kind, category, amount = parts
                amount = int(amount)
                if kind not in ("수입", "지출") or amount <= 0:
                    raise ValueError("잘못된 값입니다")
                return kind, category, amount


            n = int(input())
            balance = 0
            spent = {}
            for _ in range(n):
                line = input()
                if line.strip() == "잔액":
                    print(f"잔액: {balance:,}원")
                    continue
                try:
                    kind, category, amount = parse_command(line)
                except ValueError:
                    print(f"잘못된 입력: {line}")
                    continue
                if kind == "수입":
                    balance += amount
                else:
                    balance -= amount
                    spent[category] = spent.get(category, 0) + amount
            print("지출 내역")
            if not spent:
                print("- 없음")
            for category, amount in sorted(spent.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"- {category}: {amount:,}원")
           ''', checks={"required_syntax": ["def", "try", "for"]}),
    ])

# ====================================================================== Day 35 (stage 1 final review)
lib_cases = [("파이썬,자료구조,알고리즘", ["대출 파이썬", "대출 파이썬", "목록", "반납 자료구조", "대출 C언어", "반납 파이썬", "반납", "목록"]),
             ("책", ["목록", "대출 책", "목록"]), ("a,b", ["삭제 a", "대출 b", "반납 b", "반납 b"])]
avg_cases = [(["1", "2", "x"], "t1", "문자 섞임"), ([], "t2", "빈 목록"), (["a"], "h1", ""), (["3.5", "-1.5"], "h2", ""), (["10"], "h3", "")]
tree_cases = [({"a.txt": 10, "docs": {"b.txt": 5, "img": {"c.png": 20}}}, "t1", "3단계 폴더"), ({}, "t2", "빈 폴더"),
              ({"x": {"y": {"z": {}}}}, "h1", ""), ({"f1": 1, "f2": 2, "d": {"f3": 3}}, "h2", "")]


def lib_stdin(books, cmds):
    return lines(books, len(cmds), *cmds)


def ref_safe_avg(values):
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except ValueError:
            pass
    return sum(nums) / len(nums) if nums else 0


day35 = lesson(
    35, "1단계 마무리 누적 복습", W, ["try_except", "file_io", "dict", "function", "recursion", "text_processing", "string_parsing"],
    ["1단계(Python 기초) 전체 문법을 조합해 작은 프로그램을 완성할 수 있다.", "다음 단계(객체지향·데이터 분석)를 위한 기초를 점검할 수 있다."],
    review={"title": "1단계 5주 돌아보기", "content_md": (
        "| 주차 | 주제 | 핵심 |\n|---|---|---|\n"
        "| 1 | 첫걸음 | 변수·자료형, 입출력, 조건문, 반복문, 함수 |\n"
        "| 2 | 리스트와 튜플 | 인덱싱·슬라이싱, 메서드, 정렬, `enumerate`/`zip` |\n"
        "| 3 | 딕셔너리·집합·문자열 | 개수 세기, 그룹화, 집합 연산, `split`/`join`, 서식 |\n"
        "| 4 | 함수 심화·모듈 | 기본값, `*args`, 범위, `lambda`, 재귀, `import` |\n"
        "| 5 | 예외·파일·프로젝트 | `try/except`, `raise`, `with open`, CSV, 미니 프로젝트 |\n\n"
        "1단계를 마치면 \"입력을 읽고, 자료구조로 정리하고, 결과를 출력하는\" 프로그램을 혼자 만들 수 있습니다."),
        "quiz": [
            quiz("d35_review_q1", "이름별 점수를 저장하고, 점수 높은 순으로 출력하려면 필요한 조합은?",
                 ["리스트 + `while`", "딕셔너리 + `sorted(..., key=lambda)`", "집합 + `max`", "튜플 + `split`"], 1,
                 "이름 → 점수는 딕셔너리, 순서는 `key`를 준 정렬로."),
            quiz("d35_review_q2", "파일을 안전하게 열고 자동으로 닫는 문법은?", ["`try`", "`with`", "`def`", "`import`"], 1, "`with open(...) as f:`")]},
    concept={"title": "데이터를 파일에 저장하기: json", "blocks": [
        text("딕셔너리·리스트를 그대로 파일에 저장하고 다시 불러올 때는 표준 모듈 `json`을 씁니다. 2단계에서 다룰 데이터 분석에서도 자주 쓰는 형식입니다."),
        code('''
            import json

            contacts = {"민준": "010-1111-2222", "서연": "010-3333-4444"}
            with open("contacts.json", "w", encoding="utf-8") as f:
                json.dump(contacts, f, ensure_ascii=False)

            with open("contacts.json", encoding="utf-8") as f:
                loaded = json.load(f)
            print(loaded["서연"])
            print(len(loaded))
        ''', lines("010-3333-4444", 2)),
        tip("1단계에서 가장 많이 쓴 패턴: **개수 세기**(`get(x, 0) + 1`), **그룹화**(키별 리스트), **여러 기준 정렬**(`key=lambda`), **입력 검증**(`try/except` + `raise`). "
            "2단계에서는 이것들을 class로 묶고(객체지향), NumPy·pandas로 대량의 데이터를 다룹니다."),
    ]},
    fill_intro="숫자로 바꿀 수 있는 값만 골라 평균을 냅니다.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제(재귀 + 딕셔너리)는 **도전 문제**(선택)입니다.",
    summary={"title": "1단계 마무리", "points": [
        "자료형 선택: 순서는 리스트, 이름으로 찾기는 딕셔너리, 중복 제거는 집합.",
        "함수로 나누고, 잘못된 입력은 예외로 처리한다.",
        "데이터는 `with open`과 `json`/CSV로 파일에 남길 수 있다.",
        "다음 단계: 클래스와 객체지향, 그리고 NumPy·pandas 데이터 분석."],
        "quiz": [
            quiz("d35_summary_q1", "`json.load(f)`의 역할은?", ["딕셔너리를 파일에 저장", "파일의 JSON을 파이썬 값으로 읽기", "파일 삭제", "문자열을 숫자로 변환"], 1,
                 "`dump`는 저장, `load`는 불러오기입니다."),
            quiz("d35_summary_q2", "다음 중 1단계에서 배우지 **않은** 것은?", ["`try/except`", "`lambda`", "class 상속", "재귀"], 2,
                 "class와 객체지향은 2단계 6주차에서 배웁니다.")]},
    is_review=True,
    exercises=[
        ex("d35_fill_1", "fill_blank", "안전한 평균",
           "문자열 리스트에서 **실수로 바꿀 수 있는 값만** 골라 평균을 **반환**하세요. 바꿀 수 있는 값이 없으면 `0`을 반환합니다.\n\n"
           "예: `safe_average([\"1\", \"2\", \"x\"])` → `1.5`",
           ["try_except", "accumulation"], 1,
           '''
            def safe_average(values):
                total = 0
                count = 0
                for v in values:
                    ____:
                        total += float(v)
                        count += 1
                    except ____:
                        pass
                if count == 0:
                    return 0
                return total / count
           ''',
           [t(tid, args=[v], ret=ref_safe_avg(v), desc=d) for v, tid, d in avg_cases],
           ["변환이 실패할 수 있는 코드를 감싸는 키워드입니다.", "`float(\"x\")`가 내는 오류의 종류를 쓰세요."],
           '''
            def safe_average(values):
                total = 0
                count = 0
                for v in values:
                    try:
                        total += float(v)
                        count += 1
                    except ValueError:
                        pass
                if count == 0:
                    return 0
                return total / count
           ''', mode="function", name="safe_average"),
        ex("d35_code_1", "coding", "도서 대출 관리",
           "첫째 줄에 도서 목록(쉼표로 구분), 둘째 줄에 명령 수 `n`, 다음 `n`줄에 명령이 주어집니다. 처음에는 모든 책이 대출 가능합니다.\n\n"
           "| 명령 | 출력 |\n|---|---|\n"
           "| `대출 책이름` | `대출 완료: 책이름` / 목록에 없으면 `없는 책: 책이름` / 이미 빌려 갔으면 `이미 대출 중: 책이름` |\n"
           "| `반납 책이름` | `반납 완료: 책이름` / 빌려 간 책이 아니면 `대출 기록 없음: 책이름` |\n"
           "| `목록` | `대출 가능: 책1, 책2` (사전 순) / 하나도 없으면 `대출 가능: 없음` |\n"
           "| 그 밖 | `알 수 없는 명령: (그 줄)` |\n\n"
           "**입력 예시**\n```\n" + lib_stdin(*lib_cases[0]) + "```\n**출력 예시**\n```\n" + ref_library(*lib_cases[0]) + "```\n"
           "(`반납`처럼 책 이름 없이 온 명령은 빈 이름의 책으로 처리됩니다.)",
           ["dict", "string_parsing", "function", "condition"], 3,
           '''
            books = input().split(",")
            n = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=lib_stdin(*lib_cases[0]), out=ref_library(*lib_cases[0]), desc="여러 명령")]
           + [t(f"h{i}", stdin=lib_stdin(*c_), out=ref_library(*c_)) for i, c_ in enumerate(lib_cases[1:], start=1)],
           ["책 이름 → 대출 가능 여부(`True`/`False`) 딕셔너리로 상태를 관리하세요.",
            "문자열의 `partition(\" \")` 메서드는 첫 공백을 기준으로 (앞부분, 공백, 뒷부분) 세 조각을 돌려줍니다. 공백이 없으면 뒷부분은 빈 문자열이에요.",
            "`반납`의 \"빌려 간 책이 아님\"은 목록에 없거나 이미 대출 가능한 경우입니다. `get(title, True)`로 두 경우를 한 번에 확인할 수 있어요."],
           '''
            books = input().split(",")
            n = int(input())
            available = {}
            for book in books:
                available[book] = True
            for _ in range(n):
                line = input()
                cmd, _, title = line.partition(" ")
                if cmd == "대출":
                    if title not in available:
                        print(f"없는 책: {title}")
                    elif not available[title]:
                        print(f"이미 대출 중: {title}")
                    else:
                        available[title] = False
                        print(f"대출 완료: {title}")
                elif cmd == "반납":
                    if available.get(title, True):
                        print(f"대출 기록 없음: {title}")
                    else:
                        available[title] = True
                        print(f"반납 완료: {title}")
                elif cmd == "목록":
                    free = []
                    for book in sorted(available):
                        if available[book]:
                            free.append(book)
                    if free:
                        print("대출 가능: " + ", ".join(free))
                    else:
                        print("대출 가능: 없음")
                else:
                    print(f"알 수 없는 명령: {line}")
           ''', checks={"required_syntax": ["for", "if"]}),
        ex("d35_code_2", "coding", "[도전] 폴더 용량 계산",
           "폴더 구조가 딕셔너리로 주어집니다. 값이 정수이면 파일 크기, 딕셔너리이면 하위 폴더입니다. 전체 파일 크기의 합을 **재귀**로 반환하세요.\n\n"
           "예: `total_size({\"a.txt\": 10, \"docs\": {\"b.txt\": 5, \"img\": {\"c.png\": 20}}})` → `35`",
           ["recursion", "dict", "dict_iteration"], 3,
           '''
            def total_size(folder):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[x], ret=ref_total_size(x), desc=d) for x, tid, d in tree_cases],
           ["`folder.values()`를 하나씩 확인하세요.",
            "값이 딕셔너리이면(`isinstance(값, dict)`) 그 하위 폴더의 `total_size`를 더하고, 아니면 값을 그대로 더합니다.",
            "빈 폴더의 합은 0입니다. 종료 조건을 따로 쓰지 않아도 반복이 0번 돌면 0이 됩니다."],
           '''
            def total_size(folder):
                total = 0
                for value in folder.values():
                    if isinstance(value, dict):
                        total += total_size(value)
                    else:
                        total += value
                return total
           ''', mode="function", name="total_size", checks={"required_syntax": ["def", "for"]}, required=False),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day29, day30, day31, day32, day33, day34, day35])
