"""Week 3 (Day 15-21): 딕셔너리, 집합, 문자열 심화. Expected values come from independent reference code below."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import c, code, ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402

W = 3

# ---------------------------------------------------------------- reference implementations (not the solutions)

def ref_top_seller(sales):
    return sorted(sales.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def ref_group(students):
    out = {}
    for s in students:
        out.setdefault(s["class"], []).append(s["name"])
    return out


def ref_unique(items):
    return list(dict.fromkeys(items))


def ref_parse(line):
    if not line.strip():
        return {}
    out = {}
    for part in line.split(","):
        k, sep, v = part.partition("=")
        if not sep:
            raise ValueError
        out[k.strip()] = v.strip()
    return out


def ref_receipt(rows):
    out, total = [], 0
    for name, price, qty in rows:
        out.append(f"{name} x{qty} = {price * qty:,}원")
        total += price * qty
    out.append(f"합계: {total:,}원")
    return lines(*out)


def ref_char_types(s):
    return {"letters": sum(ch.isalpha() for ch in s), "digits": sum(ch.isdigit() for ch in s),
            "others": sum(not ch.isalnum() for ch in s)}


def ref_tags(line):
    tags = sorted({w.lstrip("#").lower() for w in line.split() if w.lstrip("#")})
    return lines(f"태그 {len(tags)}개", ", ".join(tags))


def ref_anagrams(words):
    groups = {}
    for w in words:
        groups.setdefault("".join(sorted(w)), []).append(w)
    return [g for g in groups.values() if len(g) > 1]


# ====================================================================== Day 15
day15 = lesson(
    15, "딕셔너리 기초", W, ["dict", "function", "exception"],
    ["키와 값을 짝지어 저장하는 딕셔너리를 만들고 값을 꺼낼 수 있다.",
     "값을 추가·수정·삭제하고, in과 get()으로 없는 키를 안전하게 다룰 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "2주차에는 여러 값을 **순서대로** 담는 리스트와 튜플을 배웠습니다. 리스트는 `0, 1, 2…` 번호로 값을 찾습니다. "
        "오늘 배울 딕셔너리는 번호 대신 **이름**(키)으로 값을 찾습니다."),
        "quiz": [quiz("d15_review_q1", "`list(enumerate([\"a\", \"b\"]))`의 결과는?",
                      ["`['a', 'b']`", "`[(0, 'a'), (1, 'b')]`", "`[(1, 'a'), (2, 'b')]`", "`{0: 'a', 1: 'b'}`"], 1,
                      "`enumerate`는 0부터 시작하는 번호와 값을 튜플로 묶어 줍니다.")]},
    concept={"title": "이름표로 값 찾기", "blocks": [
        text("**딕셔너리**는 `{키: 값}` 쌍을 모아 둔 자료형입니다. `딕셔너리[키]`로 값을 꺼내고, 같은 방법으로 값을 넣거나 바꿉니다. "
             "없던 키에 저장하면 새로 추가되고, 있던 키에 저장하면 값이 바뀝니다."),
        code('''
            scores = {"국어": 90, "영어": 85}
            print(scores["국어"])
            scores["수학"] = 77
            scores["영어"] = 88
            print(scores)
            print(len(scores))
        ''', lines(90, {"국어": 90, "영어": 88, "수학": 77}, 3)),
        text("키가 있는지는 `in`으로 확인합니다. `get(키, 기본값)`은 키가 없을 때 오류 대신 기본값을 돌려줍니다. `del`로 항목을 지웁니다."),
        code('''
            stock = {"사과": 3, "배": 0}
            print("사과" in stock)
            print("귤" in stock)
            print(stock.get("귤", 0))
            del stock["배"]
            print(stock)
        ''', lines(True, False, 0, {"사과": 3})),
        tip("없는 키를 `stock[\"귤\"]`처럼 대괄호로 꺼내면 `KeyError`가 납니다. 키가 없을 수도 있다면 `in`으로 먼저 확인하거나 `get()`을 쓰세요. "
            "키는 중복될 수 없고, 문자열·숫자·튜플처럼 바뀌지 않는 값만 키가 될 수 있습니다."),
    ]},
    fill_intro="`get()`의 기본값을 활용해 보세요.",
    coding_intro="딕셔너리의 값을 바꾸고, 잘못된 입력에는 예외를 발생시킵니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`{키: 값}`으로 만들고 `d[키]`로 읽기·추가·수정, `del d[키]`로 삭제.",
        "`키 in d`로 존재 확인, `d.get(키, 기본값)`으로 안전하게 읽기.",
        "없는 키를 `d[키]`로 읽으면 `KeyError`.",
        "`len(d)`는 항목(키) 개수."],
        "quiz": [
            quiz("d15_summary_q1", "`d = {\"a\": 1}` 다음에 `d[\"a\"] = 5`를 실행하면 `d`는?",
                 ["`{'a': 1, 'a': 5}`", "`{'a': 5}`", "`{'a': 6}`", "오류"], 1, "같은 키에 저장하면 값이 바뀝니다. 키는 중복되지 않습니다."),
            quiz("d15_summary_q2", "`{\"x\": 1}.get(\"y\")`의 결과는?", ["0", "`None`", "`KeyError`", "`\"y\"`"], 1,
                 "기본값을 주지 않은 `get()`은 키가 없으면 `None`을 돌려줍니다.")]},
    exercises=[
        ex("d15_fill_1", "fill_blank", "메뉴 가격 찾기",
           "메뉴판 딕셔너리 `menu`에서 `item`의 가격을 **반환**하세요. 메뉴에 없으면 `-1`을 반환합니다.\n\n"
           "예: `price_of({\"라테\": 5000}, \"라테\")` → `5000`, `price_of({\"라테\": 5000}, \"녹차\")` → `-1`",
           ["dict"], 1,
           '''
            def price_of(menu, item):
                return menu.____(item, ____)
           ''',
           [t("t1", args=[{"아메리카노": 4500, "라테": 5000}, "라테"], ret=5000, desc="있는 메뉴"),
            t("t2", args=[{"아메리카노": 4500}, "녹차"], ret=-1, desc="없는 메뉴"),
            t("h1", args=[{}, "라테"], ret=-1), t("h2", args=[{"물": 0}, "물"], ret=0)],
           ["키가 없을 때 오류 대신 기본값을 돌려주는 메서드를 떠올려 보세요.",
            "두 번째 빈칸에는 메뉴에 없을 때 돌려줄 값을 씁니다."],
           '''
            def price_of(menu, item):
                return menu.get(item, -1)
           ''', mode="function", name="price_of"),
        ex("d15_code_1", "coding", "재고 추가하기",
           "재고 딕셔너리 `stock`(상품 이름 → 개수)에 `item`을 `count`개 더한 뒤 그 딕셔너리를 **반환**하세요.\n\n"
           "- 없는 상품이면 새로 추가합니다.\n- `count`가 0 이하이면 `ValueError`를 발생시킵니다.\n\n"
           "예: `add_stock({\"사과\": 3}, \"사과\", 2)` → `{\"사과\": 5}`",
           ["dict", "function", "exception"], 2,
           '''
            def add_stock(stock, item, count):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[{"사과": 3}, "사과", 2], ret={"사과": 5}, desc="있는 상품"),
            t("t2", args=[{}, "배", 4], ret={"배": 4}, desc="새 상품"),
            t("t3", args=[{"사과": 3}, "사과", 0], raises="ValueError", desc="0개"),
            t("h1", args=[{"사과": 3}, "귤", -2], raises="ValueError"),
            t("h2", args=[{"사과": 3, "배": 1}, "배", 10], ret={"사과": 3, "배": 11})],
           ["먼저 `count`가 올바른지 검사하세요.",
            "상품이 이미 있으면 기존 개수에 더하고, 없으면 0에서 시작한다고 생각하면 `get()` 하나로 처리할 수 있습니다.",
            "마지막에 바뀐 딕셔너리를 그대로 `return` 합니다."],
           '''
            def add_stock(stock, item, count):
                if count <= 0:
                    raise ValueError("count는 1 이상이어야 합니다")
                stock[item] = stock.get(item, 0) + count
                return stock
           ''', mode="function", name="add_stock", checks={"required_syntax": ["def", "if"], "max_lines": 10}),
    ])

# ====================================================================== Day 16
sales_cases = [({"김밥": 5, "라면": 9, "떡볶이": 7}, "t1", "가장 많이 팔린 메뉴"), ({"b": 3, "a": 3}, "t2", "동점"),
               ({"순대": 2}, "h1", ""), ({"다": 1, "가": 1, "나": 1}, "h2", ""), ({"x": 0, "y": 0}, "h3", "")]
day16 = lesson(
    16, "딕셔너리 순회와 개수 세기", W, ["dict", "dict_iteration", "accumulation", "for_loop"],
    ["for문과 keys(), values(), items()로 딕셔너리를 순회할 수 있다.", "딕셔너리로 개수를 세는 패턴을 쓸 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `{키: 값}` 딕셔너리를 만들고 `get()`으로 안전하게 값을 꺼냈습니다.",
            "quiz": [quiz("d16_review_q1", "`d = {}` 다음 `d[\"a\"] = d.get(\"a\", 0) + 1`을 두 번 실행하면 `d[\"a\"]`는?",
                          ["0", "1", "2", "오류"], 2, "처음엔 `get`이 0을 돌려줘 1이 되고, 두 번째엔 1 + 1 = 2가 됩니다.")]},
    concept={"title": "모든 항목 돌아보기", "blocks": [
        text("`for 키 in 딕셔너리:`는 **키**를 하나씩 꺼냅니다. 키와 값을 함께 쓰려면 `items()`를, 값만 필요하면 `values()`를 씁니다. "
             "딕셔너리는 넣은 순서를 기억합니다."),
        code('''
            prices = {"김밥": 3000, "라면": 4000}
            for name in prices:
                print(name)
            for name, price in prices.items():
                print(f"{name}: {price}원")
            print(list(prices.keys()))
            print(sum(prices.values()))
        ''', lines("김밥", "라면", "김밥: 3000원", "라면: 4000원", ["김밥", "라면"], 7000)),
        text("**개수 세기 패턴**: 처음 보는 키는 0에서 시작하고, 볼 때마다 1씩 더합니다."),
        code('''
            counts = {}
            for ch in "banana":
                counts[ch] = counts.get(ch, 0) + 1
            print(counts)
        ''', lines({"b": 1, "a": 3, "n": 2})),
        tip("`for`로 돌고 있는 딕셔너리에 항목을 추가하거나 지우면 `RuntimeError`가 납니다. 바꿀 내용은 따로 모아 두었다가 반복이 끝난 뒤 적용하세요."),
    ]},
    fill_intro="개수 세기 패턴을 완성하세요.",
    coding_intro="`items()`로 순회하며 가장 큰 값을 찾습니다. 동점 처리에 주의하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`for k in d` → 키, `for k, v in d.items()` → 키와 값, `d.values()` → 값.",
        "개수 세기: `counts[x] = counts.get(x, 0) + 1`.",
        "딕셔너리는 넣은 순서대로 순회한다.",
        "순회 중에는 딕셔너리에 항목을 추가·삭제하지 않는다."],
        "quiz": [
            quiz("d16_summary_q1", "`for x in {\"a\": 1, \"b\": 2}: print(x)`의 출력은?", ["1, 2", "a, b", "(a, 1), (b, 2)", "오류"], 1,
                 "딕셔너리를 그대로 순회하면 키가 나옵니다."),
            quiz("d16_summary_q2", "값의 합계를 구하는 코드는?", ["`sum(d)`", "`sum(d.keys())`", "`sum(d.values())`", "`len(d)`"], 2,
                 "`values()`가 값들을 모아 줍니다.")]},
    exercises=[
        ex("d16_fill_1", "fill_blank", "단어 개수 세기",
           "단어 리스트를 받아 단어별 등장 횟수를 담은 딕셔너리를 **반환**하세요.\n\n예: `count_words([\"a\", \"b\", \"a\"])` → `{\"a\": 2, \"b\": 1}`",
           ["dict", "accumulation"], 1,
           '''
            def count_words(words):
                counts = {}
                for w in words:
                    counts[w] = counts.____(w, 0) ____ 1
                return counts
           ''',
           [t("t1", args=[["a", "b", "a"]], ret={"a": 2, "b": 1}, desc="기본"),
            t("h1", args=[[]], ret={}), t("h2", args=[["파이썬"] * 3], ret={"파이썬": 3})],
           ["처음 보는 단어는 몇에서 시작해야 할까요?", "기존 개수에 1을 더하는 연산자를 쓰세요."],
           '''
            def count_words(words):
                counts = {}
                for w in words:
                    counts[w] = counts.get(w, 0) + 1
                return counts
           ''', mode="function", name="count_words"),
        ex("d16_code_1", "coding", "가장 많이 팔린 메뉴",
           "메뉴별 판매 수 딕셔너리 `sales`를 받아 **가장 많이 팔린 메뉴 이름**을 반환하세요.\n\n"
           "- 판매 수가 같으면 이름이 사전 순으로 앞서는 메뉴를 고릅니다 (예: `\"a\"`와 `\"b\"`가 동점이면 `\"a\"`).\n"
           "- 빈 딕셔너리면 `ValueError`를 발생시킵니다.\n- `for`문을 사용하세요.",
           ["dict_iteration", "condition", "exception"], 2,
           '''
            def top_seller(sales):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_top_seller(s), desc=desc) for s, tid, desc in sales_cases if tid.startswith("t")]
           + [t("t3", args=[{}], raises="ValueError", desc="빈 딕셔너리")]
           + [t(tid, args=[s], ret=ref_top_seller(s)) for s, tid, _ in sales_cases if tid.startswith("h")],
           ["빈 딕셔너리를 먼저 처리하세요. 그다음 첫 항목을 임시 1등으로 정해 두고 나머지와 비교합니다.",
            "더 많이 팔렸거나, 판매 수가 같으면서 이름이 더 앞서면 1등을 바꿉니다. 문자열도 `<`로 사전 순 비교가 됩니다.",
            "`list(sales.items())`로 바꾸면 첫 항목을 꺼내기 쉽습니다."],
           '''
            def top_seller(sales):
                if not sales:
                    raise ValueError("판매 기록이 없습니다")
                items = list(sales.items())
                best_name, best_count = items[0]
                for name, count in items[1:]:
                    if count > best_count or (count == best_count and name < best_name):
                        best_name, best_count = name, count
                return best_name
           ''', mode="function", name="top_seller", checks={"required_syntax": ["for", "if"], "max_lines": 12}),
    ])

# ====================================================================== Day 17
students_cases = [
    ([{"name": "민준", "class": "A"}, {"name": "서연", "class": "B"}, {"name": "지호", "class": "A"}], "t1", "두 반"),
    ([], "t2", "학생 없음"),
    ([{"name": "하나", "class": "C"}], "h1", ""),
    ([{"name": n, "class": k} for n, k in [("가", "B"), ("나", "A"), ("다", "B"), ("라", "B")]], "h2", ""),
]
day17 = lesson(
    17, "딕셔너리 활용: 중첩과 그룹화", W, ["dict", "nested_dict", "dict_iteration", "list"],
    ["딕셔너리 안의 딕셔너리, 딕셔너리를 담은 리스트를 다룰 수 있다.", "기준에 따라 값을 묶는 그룹화 패턴을 쓸 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `items()`로 딕셔너리를 순회하고 개수를 세는 패턴을 연습했습니다.",
            "quiz": [quiz("d17_review_q1", "`for k, v in d.items():`에서 `v`는?", ["키", "값", "(키, 값) 튜플", "인덱스"], 1,
                          "`items()`는 (키, 값) 쌍을 주고, 이를 `k, v`로 나눠 받습니다.")]},
    concept={"title": "구조가 있는 데이터", "blocks": [
        text("딕셔너리의 값으로 리스트나 다른 딕셔너리를 넣을 수 있습니다. 대괄호를 이어 붙여 안쪽 값에 접근합니다."),
        code('''
            student = {"name": "민준", "scores": {"국어": 90, "수학": 80}}
            print(student["scores"]["수학"])
            student["scores"]["영어"] = 70
            print(len(student["scores"]))
        ''', lines(80, 3)),
        text("실제 데이터는 **딕셔너리를 담은 리스트**인 경우가 많습니다. 표의 한 줄이 딕셔너리 하나라고 생각하면 됩니다."),
        code('''
            books = [
                {"title": "파이썬", "price": 20000},
                {"title": "자료구조", "price": 25000},
            ]
            total = 0
            for book in books:
                total += book["price"]
            print(total)
            print(books[1]["title"])
        ''', lines(45000, "자료구조")),
        text("**그룹화 패턴**: 기준값을 키로, 해당하는 항목들의 리스트를 값으로 모읍니다."),
        code('''
            words = ["apple", "avocado", "banana", "blueberry", "cherry"]
            groups = {}
            for w in words:
                first = w[0]
                if first not in groups:
                    groups[first] = []
                groups[first].append(w)
            print(groups)
        ''', lines({"a": ["apple", "avocado"], "b": ["banana", "blueberry"], "c": ["cherry"]})),
        tip("`groups[first].append(w)`처럼 딕셔너리 안의 리스트는 꺼내서 바로 바꿀 수 있습니다. 키가 없을 때 먼저 빈 리스트를 넣어 주는 것을 잊지 마세요."),
    ]},
    fill_intro="딕셔너리를 담은 리스트에서 값을 꺼내 평균을 구합니다.",
    coding_intro="그룹화 패턴으로 반별 명단을 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "중첩 접근: `data[\"scores\"][\"수학\"]`.",
        "표 형태 데이터는 딕셔너리의 리스트로 표현한다.",
        "그룹화: 키가 없으면 빈 리스트를 만들고, 있으면 `append`.",
        "딕셔너리 안의 리스트·딕셔너리는 꺼내서 바로 수정할 수 있다."],
        "quiz": [
            quiz("d17_summary_q1", "`d = {\"a\": [1, 2]}`에서 `d[\"a\"].append(3)` 후 `d`는?",
                 ["`{'a': [1, 2]}`", "`{'a': [1, 2, 3]}`", "`{'a': 3}`", "오류"], 1, "딕셔너리 안의 리스트 자체가 바뀝니다."),
            quiz("d17_summary_q2", "`books[0][\"title\"]`이 뜻하는 것은?",
                 ["첫 번째 책의 제목", "제목 목록 전체", "`title` 키의 개수", "오류"], 0,
                 "`books[0]`이 첫 번째 딕셔너리이고, 거기서 `\"title\"` 값을 꺼냅니다.")]},
    exercises=[
        ex("d17_fill_1", "fill_blank", "평균 점수",
           "`{\"name\": 이름, \"score\": 점수}` 딕셔너리들의 리스트를 받아 **평균 점수**를 반환하세요. (학생은 1명 이상)\n\n"
           "예: `[{\"name\": \"a\", \"score\": 80}, {\"name\": \"b\", \"score\": 90}]` → `85.0`",
           ["nested_dict", "accumulation"], 1,
           '''
            def average_score(students):
                total = 0
                for s in students:
                    total += s[____]
                return total / ____(students)
           ''',
           [t("t1", args=[[{"name": "a", "score": 80}, {"name": "b", "score": 90}]], ret=85.0, desc="두 명"),
            t("h1", args=[[{"name": "c", "score": 77}]], ret=77.0),
            t("h2", args=[[{"name": n, "score": s} for n, s in [("x", 70), ("y", 85), ("z", 91)]]],
              ret=(70 + 85 + 91) / 3, compare={"mode": "float", "tol": 1e-9})],
           ["각 학생 딕셔너리에서 점수가 저장된 키 이름은 무엇인가요?", "학생 수를 세는 내장 함수를 쓰세요."],
           '''
            def average_score(students):
                total = 0
                for s in students:
                    total += s["score"]
                return total / len(students)
           ''', mode="function", name="average_score"),
        ex("d17_code_1", "coding", "반별 명단",
           "학생 딕셔너리 리스트(`{\"name\": 이름, \"class\": 반}`)를 받아 **반 → 이름 리스트** 딕셔너리를 반환하세요. "
           "이름은 입력 순서를 유지합니다.\n\n"
           "예: `[{\"name\": \"민준\", \"class\": \"A\"}, {\"name\": \"서연\", \"class\": \"B\"}, {\"name\": \"지호\", \"class\": \"A\"}]`\n"
           "→ `{\"A\": [\"민준\", \"지호\"], \"B\": [\"서연\"]}`",
           ["nested_dict", "dict", "list"], 2,
           '''
            def group_by_class(students):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_group(s), desc=desc) for s, tid, desc in students_cases],
           ["결과 딕셔너리를 빈 `{}`로 시작하고 학생을 한 명씩 확인합니다.",
            "그 학생의 반이 아직 키로 없으면 빈 리스트를 먼저 넣으세요.",
            "그다음 해당 반의 리스트에 이름을 `append` 합니다."],
           '''
            def group_by_class(students):
                groups = {}
                for s in students:
                    key = s["class"]
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(s["name"])
                return groups
           ''', mode="function", name="group_by_class", checks={"required_syntax": ["for"], "max_lines": 12}),
    ])

# ====================================================================== Day 18
friend_cases = [(["민준", "서연", "지호"], ["지호", "하나", "민준"], "t1", "공통 2명"), (["a"], ["b"], "h1", ""),
                ([], ["a"], "h2", ""), (["c", "a", "b", "a"], ["b", "a", "a"], "h3", "")]
unique_cases = [([3, 1, 3, 2, 1], "t1", "숫자"), (["b", "a", "b"], "t2", "문자열"), ([], "h1", ""), ([7, 7, 7], "h2", ""),
                ([5, 4, 3, 2, 1, 5, 4], "h3", "")]
day18 = lesson(
    18, "집합", W, ["set", "list", "function"],
    ["집합으로 중복을 없애고 포함 여부를 빠르게 확인할 수 있다.", "합집합·교집합·차집합을 계산할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 딕셔너리 안에 리스트를 넣어 값을 그룹으로 묶었습니다.",
            "quiz": [quiz("d18_review_q1", "그룹화 패턴에서 키가 처음 나왔을 때 먼저 해야 할 일은?",
                          ["키를 지운다", "빈 리스트를 넣는다", "`append`를 두 번 한다", "아무것도 안 한다"], 1,
                          "빈 리스트가 있어야 그 뒤에 `append`할 수 있습니다.")]},
    concept={"title": "중복 없는 모음", "blocks": [
        text("**집합**(set)은 중복이 없고 순서가 없는 모음입니다. `set(리스트)`로 중복을 없앨 수 있고, `in` 검사가 매우 빠릅니다."),
        code('''
            nums = [3, 1, 3, 2, 1]
            unique = set(nums)
            print(len(unique))
            print(2 in unique)
            unique.add(5)
            unique.discard(1)
            print(sorted(unique))
        ''', lines(3, True, [2, 3, 5])),
        text("집합끼리는 `|`(합집합), `&`(교집합), `-`(차집합)으로 계산합니다."),
        code('''
            a = {"파이썬", "자바", "C"}
            b = {"파이썬", "고"}
            print(sorted(a | b))
            print(sorted(a & b))
            print(sorted(a - b))
        ''', lines(sorted({"파이썬", "자바", "C"} | {"파이썬", "고"}), ["파이썬"], sorted({"자바", "C"}))),
        tip("집합에는 순서가 없어서 `s[0]`처럼 인덱스로 꺼낼 수 없고, 그대로 출력하면 실행할 때마다 순서가 달라질 수 있습니다. "
            "결과를 보여 줄 때는 `sorted()`로 정렬하세요. 빈 집합은 `{}`가 아니라 `set()`입니다. `{}`는 빈 딕셔너리예요."),
    ]},
    fill_intro="집합 연산으로 두 사람의 공통 친구를 찾습니다.",
    coding_intro="집합을 \"이미 본 값\" 기록용으로 활용해 보세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`set(리스트)`로 중복 제거, `add()`·`discard()`로 추가·삭제.",
        "`a | b` 합집합, `a & b` 교집합, `a - b` 차집합.",
        "집합은 순서가 없다 → 출력할 때는 `sorted()`.",
        "빈 집합은 `set()`, `{}`는 빈 딕셔너리."],
        "quiz": [
            quiz("d18_summary_q1", "`len(set([1, 1, 2, 2, 2]))`의 결과는?", ["5", "3", "2", "1"], 2, "중복이 제거되어 `{1, 2}`만 남습니다."),
            quiz("d18_summary_q2", "`{1, 2, 3} - {2, 3, 4}`의 결과는?", ["`{1}`", "`{4}`", "`{1, 4}`", "`{2, 3}`"], 0,
                 "첫 번째 집합에만 있는 원소입니다.")]},
    exercises=[
        ex("d18_fill_1", "fill_blank", "공통 친구",
           "두 사람의 친구 목록(리스트)을 받아 **둘 다 친구인 사람**을 사전 순으로 정렬한 리스트로 반환하세요.\n\n"
           "예: `common_friends([\"민준\", \"서연\"], [\"서연\", \"하나\"])` → `[\"서연\"]`",
           ["set"], 1,
           '''
            def common_friends(a, b):
                return ____(set(a) ____ set(b))
           ''',
           [t(tid, args=[a, b], ret=sorted(set(a) & set(b)), desc=d) for a, b, tid, d in friend_cases],
           ["두 집합 모두에 있는 원소를 구하는 연산자는 무엇인가요?", "집합은 순서가 없으니 정렬된 리스트로 바꿔 주는 내장 함수가 필요합니다."],
           '''
            def common_friends(a, b):
                return sorted(set(a) & set(b))
           ''', mode="function", name="common_friends"),
        ex("d18_code_1", "coding", "순서를 지키며 중복 제거",
           "리스트에서 중복을 없애되 **처음 나온 순서를 유지**한 새 리스트를 반환하세요.\n\n"
           "예: `unique_in_order([3, 1, 3, 2, 1])` → `[3, 1, 2]`\n\n`set(items)`만 쓰면 순서가 사라집니다. 이미 본 값을 집합에 기록해 보세요.",
           ["set", "list", "for_loop"], 2,
           '''
            def unique_in_order(items):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_unique(s), desc=d) for s, tid, d in unique_cases],
           ["결과 리스트와 \"이미 본 값\"을 기록할 빈 집합을 준비하세요.",
            "값이 처음 나왔을 때만 결과에 추가하고, 집합에도 기록합니다."],
           '''
            def unique_in_order(items):
                seen = set()
                result = []
                for x in items:
                    if x not in seen:
                        seen.add(x)
                        result.append(x)
                return result
           ''', mode="function", name="unique_in_order", checks={"required_syntax": ["for"], "max_lines": 10}),
    ])

# ====================================================================== Day 19
def ref_initials(name):
    return "".join(w[0].upper() for w in name.split())


initial_cases = [("kim min jun", "t1", "세 단어"), ("python", "h1", ""), ("  lee   ha  na ", "h2", "공백 여러 개")]
parse_cases = [("name=민준, age=20", "t1", "두 항목"), ("", "t2", "빈 문자열"), ("city = 서울", "h1", "공백 포함"),
               ("a=1,b=2,c=3", "h2", "")]
day19 = lesson(
    19, "문자열 메서드 심화", W, ["string_parsing", "string_method", "dict"],
    ["split()과 join()으로 문자열을 나누고 합칠 수 있다.", "find, startswith, isdigit 등으로 문자열을 검사할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 집합으로 중복을 없애고 공통 원소를 찾았습니다.",
            "quiz": [quiz("d19_review_q1", "빈 집합을 만드는 코드는?", ["`{}`", "`set()`", "`[]`", "`set[]`"], 1,
                          "`{}`는 빈 딕셔너리입니다.")]},
    concept={"title": "문자열 나누고 합치기", "blocks": [
        text("`split(구분자)`는 문자열을 잘라 **리스트**로, `구분자.join(리스트)`는 문자열 리스트를 하나로 이어 줍니다. "
             "`split()`에 아무것도 주지 않으면 공백(여러 칸 포함) 기준으로 나눕니다."),
        code('''
            line = "  홍길동, 25, 서울  "
            parts = line.strip().split(", ")
            print(parts)
            name, age, city = parts
            print(f"{name}({age})")
            print("-".join(["2026", "10", "16"]))
            print("a  b   c".split())
        ''', lines(["홍길동", "25", "서울"], "홍길동(25)", "2026-10-16", ["a", "b", "c"])),
        text("검사용 메서드들입니다. `find()`는 위치를(없으면 -1), `startswith()`/`endswith()`는 시작·끝 여부를, `isdigit()`/`isalpha()`는 숫자·문자로만 되어 있는지 알려 줍니다."),
        code('''
            s = "Hello, Python"
            print(s.find("Py"))
            print(s.find("Java"))
            print(s.startswith("Hello"))
            print(s.endswith("!"))
            print("2026".isdigit(), "abc".isalpha())
            print(s.lower().count("o"))
        ''', lines("Hello, Python".find("Py"), -1, True, False, "True True", 2)),
        tip("`join()`은 **문자열 리스트**만 이어 붙일 수 있습니다. 숫자가 섞여 있으면 `str()`로 먼저 바꿔야 합니다. `\", \".join([1, 2])`는 `TypeError`예요."),
    ]},
    fill_intro="이름의 머리글자를 대문자로 모아 봅시다.",
    coding_intro="`split()`과 `strip()`으로 설정 문자열을 딕셔너리로 바꿉니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`s.split(구분자)` → 리스트, `구분자.join(리스트)` → 문자열.",
        "`split()`(인자 없음)은 여러 칸 공백도 한 번에 처리한다.",
        "`find()`는 위치 또는 -1, `startswith()`·`endswith()`·`isdigit()`·`isalpha()`는 참/거짓.",
        "`join()`할 리스트는 모두 문자열이어야 한다."],
        "quiz": [
            quiz("d19_summary_q1", "`\"a,b,,c\".split(\",\")`의 결과는?",
                 ["`['a', 'b', 'c']`", "`['a', 'b', '', 'c']`", "`['a,b,,c']`", "오류"], 1, "쉼표 사이의 빈 문자열도 하나의 항목이 됩니다."),
            quiz("d19_summary_q2", "`\"\".join([\"P\", \"y\"])`의 결과는?", ["`\"P y\"`", "`\"Py\"`", "`[\"Py\"]`", "오류"], 1,
                 "빈 문자열을 구분자로 쓰면 그대로 붙습니다.")]},
    exercises=[
        ex("d19_fill_1", "fill_blank", "머리글자",
           "이름(영문, 공백으로 구분)을 받아 각 단어의 첫 글자를 대문자로 이어 붙여 **반환**하세요. 공백이 여러 칸일 수도 있습니다.\n\n"
           "예: `initials(\"kim min jun\")` → `\"KMJ\"`",
           ["string_parsing", "string_method"], 1,
           '''
            def initials(name):
                words = name.____()
                result = ""
                for w in words:
                    result += w[0].____()
                return result
           ''',
           [t(tid, args=[s], ret=ref_initials(s), desc=d) for s, tid, d in initial_cases],
           ["공백이 여러 칸이어도 단어만 골라내려면 `split`에 아무것도 넣지 않아야 합니다.",
            "대문자로 바꾸는 문자열 메서드를 쓰세요."],
           '''
            def initials(name):
                words = name.split()
                result = ""
                for w in words:
                    result += w[0].upper()
                return result
           ''', mode="function", name="initials"),
        ex("d19_code_1", "coding", "설정 문자열 해석",
           "`\"키=값, 키=값\"` 형식의 문자열을 딕셔너리로 바꿔 **반환**하세요.\n\n"
           "- 항목은 쉼표(`,`)로, 키와 값은 `=`로 구분합니다. 키·값 앞뒤 공백은 제거합니다.\n"
           "- 빈 문자열이면 `{}`를 반환합니다.\n- `=`가 없는 항목이 있으면 `ValueError`를 발생시킵니다.\n\n"
           "예: `parse_settings(\"name=민준, age=20\")` → `{\"name\": \"민준\", \"age\": \"20\"}`",
           ["string_parsing", "dict", "exception"], 2,
           '''
            def parse_settings(text):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_parse(s), desc=d) for s, tid, d in parse_cases if tid.startswith("t")]
           + [t("t3", args=["name=민준, age"], raises="ValueError", desc="= 없음")]
           + [t(tid, args=[s], ret=ref_parse(s)) for s, tid, _ in parse_cases if tid.startswith("h")]
           + [t("h3", args=["only"], raises="ValueError")],
           ["빈 문자열(공백만 있는 경우 포함)을 먼저 처리하세요.",
            "쉼표로 나눈 각 조각에 `=`가 있는지 `in`으로 확인하고, 없으면 예외를 발생시킵니다.",
            "`조각.split(\"=\")`으로 키와 값을 나눈 뒤 각각 `strip()` 하세요."],
           '''
            def parse_settings(text):
                if not text.strip():
                    return {}
                result = {}
                for part in text.split(","):
                    if "=" not in part:
                        raise ValueError(f"잘못된 항목: {part}")
                    key, value = part.split("=", 1)
                    result[key.strip()] = value.strip()
                return result
           ''', mode="function", name="parse_settings", checks={"required_syntax": ["for", "if"], "max_lines": 12}),
    ])

# ====================================================================== Day 20
def ref_pal(s):
    x = s.replace(" ", "").lower()
    return x == x[::-1]


pal_cases = [("Level", "t1", "대소문자"), ("abc", "t2", "회문 아님"), ("Never odd or even", "h1", ""), ("", "h2", ""), ("ab a", "h3", "")]
receipts = [[("커피", 4500, 2), ("케이크", 6000, 1)], [("물", 1000, 1)], [("빵", 2500, 4), ("우유", 1800, 2), ("잼", 12000, 1)]]


def receipt_stdin(rows):
    return lines(len(rows), *[f"{n} {p} {q}" for n, p, q in rows])


day20 = lesson(
    20, "문자열 서식과 문자 다루기", W, ["formatting", "fstring", "string", "string_method"],
    ["f-string 서식으로 천 단위 쉼표, 백분율, 정렬, 자릿수를 맞출 수 있다.", "문자열을 뒤집고 글자 단위로 검사할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `split()`/`join()`으로 문자열을 나누고 합쳤습니다.",
            "quiz": [quiz("d20_review_q1", "`\" \".join([\"a\", \"b\", \"c\"])`의 결과는?", ["`abc`", "`a b c`", "`a,b,c`", "오류"], 1,
                          "공백 한 칸을 구분자로 이어 붙입니다.")]},
    concept={"title": "보기 좋게 출력하기", "blocks": [
        text("f-string의 `{값:서식}`으로 출력 모양을 정합니다. `,`는 천 단위 쉼표, `.1%`는 백분율, `<6`/`>6`은 6칸 왼쪽/오른쪽 정렬, `03d`는 3자리 0 채우기입니다."),
        code('''
            price = 1234567
            print(f"{price:,}원")
            ratio = 0.4567
            print(f"{ratio:.1%}")
            print(f"[{'왼쪽':<6}]")
            print(f"[{'오른쪽':>6}]")
            print(f"[{7:03d}]")
        ''', lines(f"{1234567:,}원", f"{0.4567:.1%}", f"[{'왼쪽':<6}]", f"[{'오른쪽':>6}]", f"[{7:03d}]")),
        text("`[::-1]`은 문자열을 뒤집습니다. `for ch in 문자열`로 한 글자씩 검사할 수도 있습니다."),
        code('''
            word = "level"
            print(word[::-1])
            print(word == word[::-1])
            digits = ""
            for ch in "a1b2c3":
                if ch.isdigit():
                    digits += ch
            print(digits)
        ''', lines("level", True, "123")),
        tip("정렬 폭은 **글자 수** 기준입니다. 한글은 화면에서 영문보다 넓게 보여서 칸이 딱 맞지 않을 수 있습니다. 채점은 글자 그대로 비교하니 걱정하지 마세요."),
    ]},
    fill_intro="공백과 대소문자를 무시하는 회문 검사기를 완성하세요.",
    coding_intro="입력을 읽어 서식이 있는 영수증을 출력합니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`{x:,}` 천 단위 쉼표, `{x:.1%}` 백분율, `{x:.2f}` 소수 둘째 자리.",
        "`{s:<6}` 왼쪽 정렬, `{s:>6}` 오른쪽 정렬, `{n:03d}` 0 채우기.",
        "`s[::-1]`로 뒤집기, `for ch in s`로 글자 단위 검사.",
        "서식 결과는 문자열이다."],
        "quiz": [
            quiz("d20_summary_q1", "`f\"{25000:,}\"`의 결과는?", ["`25000`", "`25,000`", "`25.000`", "`2,5000`"], 1, "세 자리마다 쉼표가 들어갑니다."),
            quiz("d20_summary_q2", "`\"abc\"[::-1]`의 결과는?", ["`abc`", "`cba`", "`c`", "오류"], 1, "간격 -1로 끝에서부터 읽습니다.")]},
    exercises=[
        ex("d20_fill_1", "fill_blank", "회문 검사",
           "문장이 앞뒤로 같게 읽히는지(회문) **반환**하세요. 공백은 무시하고 대소문자는 구분하지 않습니다.\n\n"
           "예: `is_palindrome(\"Level\")` → `True`, `is_palindrome(\"Never odd or even\")` → `True`",
           ["string", "string_method"], 1,
           '''
            def is_palindrome(text):
                cleaned = text.replace(" ", "").____()
                return cleaned == cleaned[____]
           ''',
           [t(tid, args=[s], ret=ref_pal(s), desc=d) for s, tid, d in pal_cases],
           ["대소문자를 무시하려면 모두 한쪽(소문자 등)으로 맞추면 됩니다.", "문자열을 뒤집는 슬라이싱을 떠올려 보세요."],
           '''
            def is_palindrome(text):
                cleaned = text.replace(" ", "").lower()
                return cleaned == cleaned[::-1]
           ''', mode="function", name="is_palindrome"),
        ex("d20_code_1", "coding", "영수증 출력",
           "첫째 줄에 품목 수 `n`, 다음 `n`줄에 `이름 가격 수량`이 공백으로 구분되어 주어집니다. 아래 형식으로 출력하세요.\n\n"
           "**입력 예시**\n```\n2\n커피 4500 2\n케이크 6000 1\n```\n**출력 예시**\n```\n" + ref_receipt(receipts[0]) + "```\n\n"
           "금액에는 천 단위 쉼표를 넣고, f-string을 사용하세요.",
           ["formatting", "fstring", "string_parsing", "accumulation"], 2,
           '''
            n = int(input())
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=receipt_stdin(receipts[0]), out=ref_receipt(receipts[0]), desc="2개 품목")]
           + [t(f"h{i}", stdin=receipt_stdin(r), out=ref_receipt(r)) for i, r in enumerate(receipts[1:], start=1)],
           ["한 줄을 `split()`으로 나누면 이름·가격·수량 세 조각이 됩니다. 가격과 수량은 정수로 바꿔야 해요.",
            "합계를 담을 변수를 반복 전에 0으로 준비하세요.",
            "천 단위 쉼표 서식은 `{값:,}` 입니다."],
           '''
            n = int(input())
            total = 0
            for _ in range(n):
                name, price, qty = input().split()
                amount = int(price) * int(qty)
                total += amount
                print(f"{name} x{qty} = {amount:,}원")
            print(f"합계: {total:,}원")
           ''', checks={"required_syntax": ["for", "fstring"], "max_lines": 10}),
    ])

# ====================================================================== Day 21 (cumulative review)
char_cases = [("a1b2!", "t1", "섞인 문자열"), ("", "h1", ""), ("파이썬 3.14", "h2", "한글·공백·점"), ("12345", "h3", "")]
tag_cases = ["#Python #AI #python #ai #데이터", "#solo", "#B #a #b #A #c"]
ana_cases = [(["eat", "tea", "tan", "ate", "nat", "bat"], "t1", "기본"), (["abc"], "t2", "묶음 없음"), ([], "h1", ""),
             (["listen", "silent", "enlist", "google"], "h2", "")]
day21 = lesson(
    21, "3주차 누적 복습", W, ["dict", "dict_iteration", "nested_dict", "set", "string_parsing", "formatting", "function"],
    ["딕셔너리·집합·문자열 처리를 조합해 데이터를 정리할 수 있다.", "어떤 자료형이 문제에 알맞은지 고를 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 15 | 딕셔너리 기초 | `d[키]`, `in`, `get(키, 기본값)` |\n"
        "| 16 | 순회와 세기 | `items()`, `counts.get(x, 0) + 1` |\n"
        "| 17 | 중첩과 그룹화 | `data[\"a\"][\"b\"]`, 키별 리스트 |\n"
        "| 18 | 집합 | 중복 제거, 합·교·차집합 |\n"
        "| 19 | 문자열 메서드 | `split`, `join`, `find`, `isdigit` |\n"
        "| 20 | 서식 | `{x:,}`, `{x:.1%}`, `{s:<6}`, `[::-1]` |\n\n"
        "**어떤 자료형을 쓸까?** 순서가 중요하면 리스트, 이름으로 찾으면 딕셔너리, 중복 없이 포함 여부만 보면 집합입니다."),
        "quiz": [
            quiz("d21_review_q1", "학생 이름으로 점수를 빠르게 찾고 싶다면 알맞은 자료형은?", ["리스트", "튜플", "딕셔너리", "집합"], 2,
                 "이름(키)으로 값을 찾는 것이 딕셔너리의 역할입니다."),
            quiz("d21_review_q2", "방문한 페이지를 중복 없이 기록하고 방문 여부만 확인하려면?", ["리스트", "딕셔너리", "집합", "문자열"], 2,
                 "중복 없는 모음 + 빠른 `in` 검사 → 집합.")]},
    concept={"title": "자료형 조합하기", "blocks": [
        text("실제 문제는 여러 자료형을 섞어 풉니다. 아래 예제는 문장을 단어로 나누고(문자열), 단어별 개수를 세고(딕셔너리), 서로 다른 단어 수를 셉니다(집합)."),
        code('''
            sentence = "the cat and the hat and the bat"
            words = sentence.split()
            counts = {}
            for w in words:
                counts[w] = counts.get(w, 0) + 1
            print(f"단어 {len(words)}개, 종류 {len(set(words))}개")
            for w in sorted(counts):
                print(f"{w:<4}{counts[w]}")
        ''', lines("단어 8개, 종류 5개", *[f"{w:<4}{n}" for w, n in sorted({"the": 3, "cat": 1, "and": 2, "hat": 1, "bat": 1}.items())])),
        tip("`sorted(딕셔너리)`는 **키**를 정렬한 리스트를 돌려줍니다. 값 기준 정렬은 다음 주 `key=`와 `lambda`에서 배웁니다."),
    ]},
    fill_intro="글자 종류별 개수를 딕셔너리로 정리합니다.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "3주차 마무리", "points": [
        "딕셔너리: 이름으로 찾기·세기·그룹화.",
        "집합: 중복 제거와 포함 여부, 집합 연산.",
        "문자열: `split`/`join`/`strip`으로 다듬고, f-string 서식으로 출력.",
        "다음 주에는 함수를 더 유연하게 만드는 법과 모듈을 배운다."],
        "quiz": [
            quiz("d21_summary_q1", "`sorted({\"b\": 1, \"a\": 2})`의 결과는?", ["`[1, 2]`", "`['a', 'b']`", "`[('a', 2), ('b', 1)]`", "오류"], 1,
                 "딕셔너리를 정렬하면 키 목록이 나옵니다."),
            quiz("d21_summary_q2", "`len(set(\"banana\"))`의 결과는?", ["6", "3", "2", "1"], 1, "b, a, n 세 글자만 남습니다.")]},
    is_review=True,
    exercises=[
        ex("d21_fill_1", "fill_blank", "글자 종류 세기",
           "문자열을 받아 **문자**(letters), **숫자**(digits), **그 밖**(others)의 개수를 딕셔너리로 반환하세요. 한글도 문자입니다.\n\n"
           "예: `char_types(\"a1b2!\")` → `{\"letters\": 2, \"digits\": 2, \"others\": 1}`",
           ["dict", "string_method", "condition"], 2,
           '''
            def char_types(text):
                counts = {"letters": 0, "digits": 0, "others": 0}
                for ch in text:
                    if ch.____():
                        counts["letters"] += 1
                    elif ch.____():
                        counts["digits"] += 1
                    else:
                        counts[____] += 1
                return counts
           ''',
           [t(tid, args=[s], ret=ref_char_types(s), desc=d) for s, tid, d in char_cases],
           ["Day 19에서 배운, 문자로만 되어 있는지·숫자로만 되어 있는지 검사하는 메서드를 떠올려 보세요.",
            "마지막 빈칸은 딕셔너리의 키 이름(문자열)입니다."],
           '''
            def char_types(text):
                counts = {"letters": 0, "digits": 0, "others": 0}
                for ch in text:
                    if ch.isalpha():
                        counts["letters"] += 1
                    elif ch.isdigit():
                        counts["digits"] += 1
                    else:
                        counts["others"] += 1
                return counts
           ''', mode="function", name="char_types"),
        ex("d21_code_1", "coding", "해시태그 정리",
           "해시태그가 공백으로 구분된 한 줄을 입력받습니다. `#`을 떼고 소문자로 바꾼 뒤 **중복을 없애고 사전 순으로 정렬**하여 출력하세요.\n\n"
           "**입력 예시**\n```\n" + tag_cases[0] + "\n```\n**출력 예시**\n```\n" + ref_tags(tag_cases[0]) + "```",
           ["set", "string_parsing", "string_method", "fstring"], 2,
           '''
            line = input()
            # 여기에 코드를 작성하세요
           ''',
           [t("t1", stdin=tag_cases[0] + "\n", out=ref_tags(tag_cases[0]), desc="중복·대소문자")]
           + [t(f"h{i}", stdin=s + "\n", out=ref_tags(s)) for i, s in enumerate(tag_cases[1:], start=1)],
           ["`split()`으로 태그를 나누고, 각 태그에서 `#`을 떼는 방법을 생각해 보세요 (`lstrip(\"#\")`, `replace`, 슬라이싱 모두 가능).",
            "중복 제거에는 집합이 좋습니다. 출력 전에 `sorted()`로 정렬하세요.",
            "두 번째 줄은 `\", \".join(...)`으로 만들 수 있습니다."],
           '''
            line = input()
            tags = set()
            for word in line.split():
                tags.add(word.lstrip("#").lower())
            ordered = sorted(tags)
            print(f"태그 {len(ordered)}개")
            print(", ".join(ordered))
           ''', checks={"required_syntax": ["for"], "max_lines": 10}),
        ex("d21_code_2", "coding", "[도전] 애너그램 묶기",
           "단어 리스트를 받아, 글자 구성이 같은 단어(애너그램)끼리 묶은 **리스트의 리스트**를 반환하세요.\n\n"
           "- 2개 이상 묶인 그룹만 포함합니다.\n- 그룹 순서는 그 그룹의 첫 단어가 처음 등장한 순서, 그룹 안 단어도 등장 순서를 따릅니다.\n\n"
           "예: `[\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]` → `[[\"eat\", \"tea\", \"ate\"], [\"tan\", \"nat\"]]`",
           ["dict", "nested_dict", "string", "sorting"], 3,
           '''
            def group_anagrams(words):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[w], ret=ref_anagrams(w), desc=d) for w, tid, d in ana_cases],
           ["애너그램끼리는 글자를 정렬하면 같아집니다. `\"\".join(sorted(word))`를 키로 써 보세요.",
            "Day 17의 그룹화 패턴으로 키별 단어 리스트를 만듭니다.",
            "마지막에 길이가 2 이상인 리스트만 골라 반환합니다."],
           '''
            def group_anagrams(words):
                groups = {}
                for w in words:
                    key = "".join(sorted(w))
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(w)
                result = []
                for group in groups.values():
                    if len(group) > 1:
                        result.append(group)
                return result
           ''', mode="function", name="group_anagrams", checks={"required_syntax": ["def", "for"]}, required=False),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day15, day16, day17, day18, day19, day20, day21])
