"""Week 6 (Day 36-42): 클래스와 객체지향. Expected values come from independent reference code below."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import code, ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402

W, ST = 6, "advanced_data"


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


# ---------------------------------------------------------------- reference implementations

def ref_cart(commands):
    items = {}
    for c in commands:
        if c[0] == "add":
            name, price, qty = c[1], c[2], c[3]
            old = items.get(name, (price, 0))
            items[name] = (price, old[1] + qty)
        elif c[0] == "remove":
            if c[1] not in items:
                raise KeyError
            del items[c[1]]
    return [sum(p * q for p, q in items.values()), sum(q for _, q in items.values())]


def ref_frac(a, b, c, d):
    n, m = a * d + c * b, b * d
    g = math.gcd(n, m)
    n, m = n // g, m // g
    if m < 0:
        n, m = -n, -m
    return f"{n}/{m}"


def ref_shapes(specs):
    descs, total = [], 0
    for s in specs:
        if s[0] == "circle":
            name, area = "원", math.pi * s[1] ** 2
        else:
            name, area = "직사각형", s[1] * s[2]
        descs.append(f"{name} 넓이 {area:.2f}")
        total += area
    return [descs, round(total, 2)]


def ref_account(ops):
    bal, hist = 0, 0
    for kind, amt in ops:
        if amt <= 0:
            raise ValueError
        if kind == "in":
            bal += amt
        else:
            if amt > bal:
                raise ValueError
            bal -= amt
        hist += 1
    return [bal, hist, False]


def ref_products(csv_lines, rate):
    out, total = [], 0
    for line in csv_lines:
        parts = line.split(",")
        name, price = parts[0], int(parts[1])
        cat = parts[2] if len(parts) > 2 and parts[2] else "기타"
        out.append([name, price, cat])
        total += int(price * (1 - rate))
    return [out, total]


def ref_library(cmds):
    books, out = {}, []
    for c in cmds:
        op = c[0]
        try:
            if op == "add":
                if c[1] in books:
                    raise ValueError(f"이미 있는 책: {c[1]}")
                books[c[1]] = None
                out.append(f"추가: {c[1]}")
            elif op == "borrow":
                if c[1] not in books:
                    raise KeyError(c[1])
                if books[c[1]] is not None:
                    raise ValueError(f"대출 중: {c[1]}")
                books[c[1]] = c[2]
                out.append(f"대출: {c[1]} → {c[2]}")
            elif op == "return":
                if c[1] not in books:
                    raise KeyError(c[1])
                if books[c[1]] is None:
                    raise ValueError(f"대출 기록 없음: {c[1]}")
                books[c[1]] = None
                out.append(f"반납: {c[1]}")
        except KeyError as e:
            out.append(f"오류: 없는 책 {e.args[0]}")
        except ValueError as e:
            out.append(f"오류: {e}")
    return out


def ref_balanced(s):
    pairs, stack = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


# ====================================================================== Day 36
day36 = L(
    36, "클래스와 객체", W, ["class"],
    ["class로 나만의 자료형을 정의하고 객체(인스턴스)를 만들 수 있다.", "__init__과 self로 객체마다 다른 속성을 저장할 수 있다."],
    review={"title": "2단계 시작", "content_md": (
        "1단계에서 Python 기초를 모두 마쳤습니다. **2단계**(Python 심화와 데이터 분석)는 객체지향으로 시작합니다.\n\n"
        "지금까지는 데이터(딕셔너리·리스트)와 그 데이터를 다루는 함수를 따로 만들었습니다. **클래스**는 이 둘을 하나로 묶는 방법입니다."),
        "quiz": [quiz("d36_review_q1", "학생 한 명의 이름·점수를 묶어 표현하던 1단계 방식으로 가장 알맞은 것은?",
                      ["`(\"민준\", 90)` 튜플이나 `{\"name\": \"민준\", \"score\": 90}` 딕셔너리", "집합", "문자열 하나", "`range`"], 0,
                      "오늘은 같은 일을 클래스로 표현합니다.")]},
    concept={"title": "나만의 자료형 만들기", "blocks": [
        text("`class 이름:`으로 **설계도**(클래스)를 만들고, `이름(...)`을 호출해 **객체**(인스턴스)를 찍어 냅니다. "
             "`__init__`은 객체가 만들어질 때 자동으로 실행되는 초기화 메서드이고, 첫 매개변수 `self`는 지금 만들어지는 그 객체 자신입니다."),
        code('''
            class Dog:
                def __init__(self, name, age):
                    self.name = name
                    self.age = age

            a = Dog("초코", 3)
            b = Dog("보리", 5)
            print(a.name, a.age)
            print(b.name)
            b.age += 1
            print(b.age)
            print(type(a).__name__)
        ''', lines("초코 3", "보리", 6, "Dog")),
        text("`self.이름 = 값`으로 저장한 값을 **속성**이라고 합니다. 객체마다 따로 저장되므로 `a`의 나이를 바꿔도 `b`는 그대로입니다."),
        tip("클래스 이름은 관례적으로 `Dog`, `BankAccount`처럼 단어 첫 글자를 대문자로 씁니다. `__init__`의 밑줄은 양쪽에 **두 개씩**입니다. `_init_`으로 쓰면 초기화가 실행되지 않아요."),
    ]},
    fill_intro="`__init__`과 `self`를 채워 좌표 클래스를 완성하세요. 아래 `check` 함수는 채점용이니 고치지 마세요.",
    coding_intro="클래스를 직접 정의합니다. 잘못된 값이면 객체를 만들 때 예외를 발생시키세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`class 이름:` → 설계도, `이름(인자)` → 객체 생성.",
        "`__init__(self, ...)`은 생성될 때 자동 실행, `self`는 그 객체 자신.",
        "`self.속성 = 값`으로 객체마다 데이터를 저장한다.",
        "`객체.속성`으로 읽고 바꾼다."],
        "quiz": [
            quiz("d36_summary_q1", "`p = Point(1, 2)`를 실행할 때 자동으로 호출되는 메서드는?", ["`Point()`", "`__init__`", "`__new_point__`", "`self`"], 1,
                 "객체 생성 시 `__init__`이 실행됩니다."),
            quiz("d36_summary_q2", "`self`가 가리키는 것은?", ["클래스 이름", "지금 다루는 객체 자신", "첫 번째 인자 값", "모듈"], 1,
                 "메서드가 어떤 객체에서 불렸는지를 알려 줍니다.")]},
    exercises=[
        ex("d36_fill_1", "fill_blank", "좌표 클래스",
           "x, y 좌표를 저장하는 `Point` 클래스를 완성하세요.",
           ["class"], 1,
           '''
            class Point:
                def __init__(____, x, y):
                    self.x = x
                    self.____ = y


            def check(x, y):
                p = Point(x, y)
                return [p.x, p.y]
           ''',
           [t("t1", args=[1, 2], ret=[1, 2], desc="(1, 2)"), t("h1", args=[0, -5], ret=[0, -5]), t("h2", args=[3.5, 7], ret=[3.5, 7])],
           ["메서드의 첫 매개변수는 항상 객체 자신을 받습니다. 관례적인 이름이 있어요.", "`p.y`로 읽을 수 있도록 속성 이름을 정하세요."],
           '''
            class Point:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y


            def check(x, y):
                p = Point(x, y)
                return [p.x, p.y]
           ''', mode="function", name="check"),
        ex("d36_code_1", "coding", "직사각형 클래스",
           "`Rectangle(width, height)` 클래스를 정의하세요.\n\n"
           "- 속성 `width`, `height`, 그리고 넓이를 미리 계산한 `area`를 저장합니다.\n"
           "- 너비나 높이가 0 이하이면 `ValueError`를 발생시킵니다.\n\n아래 `describe` 함수는 채점용이니 그대로 두세요.",
           ["class", "exception"], 2,
           '''
            # 여기에 Rectangle 클래스를 작성하세요


            def describe(width, height):
                r = Rectangle(width, height)
                return [r.width, r.height, r.area]
           ''',
           [t("t1", args=[3, 4], ret=[3, 4, 12], desc="3×4"), t("t2", args=[0, 4], raises="ValueError", desc="너비 0"),
            t("h1", args=[2.5, 2], ret=[2.5, 2, 5.0]), t("h2", args=[5, -1], raises="ValueError"), t("h3", args=[1, 1], ret=[1, 1, 1])],
           ["`class Rectangle:` 안에 `__init__(self, width, height)`를 만드세요.",
            "값 검사를 먼저 하고, 통과하면 `self.width`, `self.height`, `self.area`를 저장합니다."],
           '''
            class Rectangle:
                def __init__(self, width, height):
                    if width <= 0 or height <= 0:
                        raise ValueError("너비와 높이는 양수여야 합니다")
                    self.width = width
                    self.height = height
                    self.area = width * height


            def describe(width, height):
                r = Rectangle(width, height)
                return [r.width, r.height, r.area]
           ''', mode="function", name="describe", checks={"required_syntax": ["class"]}),
    ])

# ====================================================================== Day 37
cart_cases = [([["add", "사과", 1000, 2], ["add", "우유", 2500, 1], ["add", "사과", 1000, 1]], "t1", "같은 상품 추가"),
              ([["add", "빵", 3000, 1], ["remove", "빵"]], "t2", "삭제"), ([], "h1", ""),
              ([["add", "a", 100, 5], ["add", "b", 50, 2], ["remove", "a"], ["add", "c", 10, 1]], "h2", "")]
day37 = L(
    37, "메서드", W, ["method", "class"],
    ["객체의 데이터를 다루는 메서드를 정의하고 호출할 수 있다.", "메서드 안에서 self로 속성과 다른 메서드를 사용할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `class`와 `__init__`으로 속성을 가진 객체를 만들었습니다.",
            "quiz": [quiz("d37_review_q1", "`class A:` 안에서 `def __init__(self, v): self.v = v`일 때 `A(5).v`는?", ["`None`", "5", "`v`", "오류"], 1,
                          "생성할 때 넘긴 5가 속성 `v`에 저장됩니다.")]},
    concept={"title": "객체가 할 수 있는 일", "blocks": [
        text("클래스 안에 정의한 함수를 **메서드**라고 합니다. 첫 매개변수는 항상 `self`이고, 호출할 때는 `객체.메서드(인자)`처럼 `self`를 빼고 부릅니다."),
        code('''
            class Counter:
                def __init__(self):
                    self.count = 0

                def increment(self, step=1):
                    self.count += step

                def reset(self):
                    self.count = 0

            c = Counter()
            c.increment()
            c.increment(5)
            print(c.count)
            c.reset()
            print(c.count)
        ''', lines(6, 0)),
        text("메서드는 값을 돌려줄 수도 있고, `self.다른메서드()`로 같은 객체의 다른 메서드를 부를 수도 있습니다."),
        code('''
            class Circle:
                def __init__(self, r):
                    self.r = r

                def area(self):
                    return 3.14 * self.r ** 2

                def describe(self):
                    return f"반지름 {self.r}, 넓이 {self.area():.1f}"

            print(Circle(2).describe())
        ''', lines(f"반지름 2, 넓이 {3.14 * 2 ** 2:.1f}")),
        tip("메서드 정의에 `self`를 빠뜨리면 호출할 때 `TypeError: ... takes 0 positional arguments but 1 was given` 오류가 납니다. 파이썬이 객체를 첫 인자로 자동으로 넘기기 때문이에요."),
    ]},
    fill_intro="입금·출금 메서드를 완성하세요.",
    coding_intro="장바구니 클래스를 메서드로 설계하세요. `simulate` 함수는 채점용입니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "메서드 = 클래스 안의 함수, 첫 매개변수는 `self`.",
        "호출: `객체.메서드(인자)` (self는 자동 전달).",
        "메서드 안에서 `self.속성`으로 상태를 읽고 바꾼다.",
        "`self.다른메서드()`로 메서드끼리 협력한다."],
        "quiz": [
            quiz("d37_summary_q1", "`def add(self, x):`로 정의한 메서드를 올바르게 호출한 것은?", ["`obj.add(obj, 3)`", "`obj.add(3)`", "`add(3)`", "`obj.add(self, 3)`"], 1,
                 "`self`는 파이썬이 자동으로 넘깁니다."),
            quiz("d37_summary_q2", "메서드가 객체의 상태를 바꾸려면?", ["지역 변수에 저장", "`self.속성`에 저장", "`return`만 한다", "전역 변수 사용"], 1, "`self`에 저장해야 객체에 남습니다.")]},
    exercises=[
        ex("d37_fill_1", "fill_blank", "은행 계좌",
           "`BankAccount`의 입금 메서드와 `run` 함수의 빈칸을 채우세요. `ops`는 `[\"in\" 또는 \"out\", 금액]` 목록입니다.",
           ["method"], 1,
           '''
            class BankAccount:
                def __init__(self, balance=0):
                    self.balance = balance

                def deposit(self, amount):
                    self.balance ____ amount

                def withdraw(self, amount):
                    if amount > self.balance:
                        raise ValueError("잔액 부족")
                    self.balance -= amount


            def run(ops):
                acc = BankAccount()
                for kind, amount in ops:
                    if kind == "in":
                        acc.____(amount)
                    else:
                        acc.withdraw(amount)
                return acc.balance
           ''',
           [t("t1", args=[[["in", 100], ["out", 30]]], ret=70, desc="입금 후 출금"), t("t2", args=[[["out", 1]]], raises="ValueError", desc="잔액 부족"),
            t("h1", args=[[]], ret=0), t("h2", args=[[["in", 5], ["in", 7], ["out", 12]]], ret=0)],
           ["잔액에 금액을 더해 다시 저장하는 복합 대입 연산자입니다.", "입금을 담당하는 메서드 이름을 쓰세요."],
           '''
            class BankAccount:
                def __init__(self, balance=0):
                    self.balance = balance

                def deposit(self, amount):
                    self.balance += amount

                def withdraw(self, amount):
                    if amount > self.balance:
                        raise ValueError("잔액 부족")
                    self.balance -= amount


            def run(ops):
                acc = BankAccount()
                for kind, amount in ops:
                    if kind == "in":
                        acc.deposit(amount)
                    else:
                        acc.withdraw(amount)
                return acc.balance
           ''', mode="function", name="run"),
        ex("d37_code_1", "coding", "장바구니",
           "`ShoppingCart` 클래스를 작성하세요.\n\n"
           "- `add(name, price, qty=1)`: 상품 추가. 이미 있으면 수량만 더합니다.\n"
           "- `remove(name)`: 상품 삭제. 없으면 `KeyError`.\n"
           "- `total()`: 가격 × 수량의 합계, `count()`: 전체 수량.\n\n`simulate` 함수는 채점용이니 그대로 두세요.",
           ["method", "class", "dict"], 2,
           '''
            class ShoppingCart:
                def __init__(self):
                    self.items = {}  # 이름 → [가격, 수량]

                # 여기에 메서드를 작성하세요


            def simulate(commands):
                cart = ShoppingCart()
                for c in commands:
                    if c[0] == "add":
                        cart.add(c[1], c[2], c[3])
                    else:
                        cart.remove(c[1])
                return [cart.total(), cart.count()]
           ''',
           [t(tid, args=[c_], ret=ref_cart(c_), desc=d) for c_, tid, d in cart_cases if tid[0] == "t"]
           + [t("t3", args=[[["remove", "없음"]]], raises="KeyError", desc="없는 상품")]
           + [t(tid, args=[c_], ret=ref_cart(c_)) for c_, tid, d in cart_cases if tid[0] == "h"],
           ["`self.items`에 이름이 있으면 수량에 더하고, 없으면 `[price, qty]`를 새로 넣습니다.",
            "`remove`는 `in`으로 확인한 뒤 `del self.items[name]`.",
            "`total`과 `count`는 `self.items.values()`를 돌며 합계를 구합니다."],
           '''
            class ShoppingCart:
                def __init__(self):
                    self.items = {}  # 이름 → [가격, 수량]

                def add(self, name, price, qty=1):
                    if name in self.items:
                        self.items[name][1] += qty
                    else:
                        self.items[name] = [price, qty]

                def remove(self, name):
                    if name not in self.items:
                        raise KeyError(name)
                    del self.items[name]

                def total(self):
                    result = 0
                    for price, qty in self.items.values():
                        result += price * qty
                    return result

                def count(self):
                    result = 0
                    for _, qty in self.items.values():
                        result += qty
                    return result


            def simulate(commands):
                cart = ShoppingCart()
                for c in commands:
                    if c[0] == "add":
                        cart.add(c[1], c[2], c[3])
                    else:
                        cart.remove(c[1])
                return [cart.total(), cart.count()]
           ''', mode="function", name="simulate", checks={"required_syntax": ["class", "def"]}),
    ])

# ====================================================================== Day 38
frac_cases = [((1, 2, 1, 3), "t1", "1/2 + 1/3"), ((1, 4, 1, 4), "t2", "약분"), ((3, -4, 1, 4), "h1", ""), ((0, 5, 2, 10), "h2", ""),
              ((5, 6, 1, 6), "h3", "")]
day38 = L(
    38, "특수 메서드", W, ["dunder", "class", "method"],
    ["__str__, __repr__으로 객체의 출력 모양을 정할 수 있다.", "__add__, __eq__, __len__ 등으로 연산자와 내장 함수를 지원할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 메서드로 객체의 상태를 바꾸고 값을 계산했습니다.",
            "quiz": [quiz("d38_review_q1", "메서드 정의에 `self`를 빠뜨리면?", ["정상 동작", "호출할 때 `TypeError`", "`None` 반환", "속성이 사라짐"], 1,
                          "파이썬이 객체를 첫 인자로 자동 전달하기 때문입니다.")]},
    concept={"title": "파이썬 문법과 연결하기", "blocks": [
        text("이름이 `__이름__` 형태인 **특수 메서드**를 정의하면 `print()`, `+`, `==`, `len()` 같은 문법이 내 객체에서도 동작합니다. "
             "`__str__`은 `print()`·`str()`용, `__repr__`은 리스트 안 표시·디버깅용입니다."),
        code('''
            class Money:
                def __init__(self, amount):
                    self.amount = amount

                def __str__(self):
                    return f"{self.amount:,}원"

                def __repr__(self):
                    return f"Money({self.amount})"

                def __add__(self, other):
                    return Money(self.amount + other.amount)

                def __eq__(self, other):
                    return self.amount == other.amount

            a = Money(1500)
            b = Money(2500)
            print(a)
            print([a, b])
            print(a + b)
            print(a == Money(1500))
        ''', lines("1,500원", "[Money(1500), Money(2500)]", "4,000원", True)),
        code('''
            class Playlist:
                def __init__(self, songs):
                    self.songs = songs

                def __len__(self):
                    return len(self.songs)

            print(len(Playlist(["a", "b", "c"])))
        ''', lines(3)),
        tip("`__eq__`를 정의하지 않으면 `==`는 **같은 객체인지**(메모리 위치)만 비교해서, 내용이 같아도 `False`가 나옵니다. 그 밖에 `__lt__`(<), `__sub__`(-), `__mul__`(*) 등이 있습니다."),
    ]},
    fill_intro="벡터 덧셈과 문자열 표현을 완성하세요.",
    coding_intro="분수 클래스를 만들어 덧셈과 약분을 지원하세요. `add_fractions`는 채점용입니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`__str__` → `print`/`str`, `__repr__` → 리스트 안·디버깅 표시.",
        "`__add__` → `+`, `__eq__` → `==`, `__len__` → `len()`.",
        "특수 메서드는 직접 부르지 않고 문법이 대신 호출한다.",
        "`__eq__`가 없으면 `==`는 같은 객체인지만 본다."],
        "quiz": [
            quiz("d38_summary_q1", "`a + b`를 계산할 때 호출되는 것은?", ["`a.__plus__(b)`", "`a.__add__(b)`", "`b.__add__(a)`", "`add(a, b)`"], 1, "왼쪽 객체의 `__add__`가 호출됩니다."),
            quiz("d38_summary_q2", "`print(obj)`의 출력을 정하는 메서드는?", ["`__init__`", "`__print__`", "`__str__`", "`__len__`"], 2, "`print`는 `str()`을 거칩니다.")]},
    exercises=[
        ex("d38_fill_1", "fill_blank", "벡터 덧셈",
           "`Vector`끼리 `+`로 더할 수 있게 하고, 결과를 문자열로 반환하세요.\n\n예: `check([1, 2], [3, 4])` → `\"(4, 6)\"`",
           ["dunder"], 1,
           '''
            class Vector:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y

                def ____(self, other):
                    return Vector(self.x + other.x, self.y + other.y)

                def __str__(self):
                    return f"({self.x}, {self.y})"


            def check(a, b):
                return ____(Vector(*a) + Vector(*b))
           ''',
           [t("t1", args=[[1, 2], [3, 4]], ret="(4, 6)", desc="기본"), t("h1", args=[[0, 0], [0, 0]], ret="(0, 0)"), t("h2", args=[[-1, 5], [1, -5]], ret="(0, 0)")],
           ["`+` 연산자에 대응하는 특수 메서드 이름입니다(양쪽 밑줄 두 개).", "객체를 문자열로 바꾸는 내장 함수는 `__str__`을 호출합니다."],
           '''
            class Vector:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y

                def __add__(self, other):
                    return Vector(self.x + other.x, self.y + other.y)

                def __str__(self):
                    return f"({self.x}, {self.y})"


            def check(a, b):
                return str(Vector(*a) + Vector(*b))
           ''', mode="function", name="check"),
        ex("d38_code_1", "coding", "분수 클래스",
           "`Fraction(numerator, denominator)` 클래스를 작성하세요.\n\n"
           "- 분모가 0이면 `ValueError`.\n- 만들 때 **기약분수**로 약분하고, 분모는 항상 양수로 둡니다(`math.gcd` 사용 가능).\n"
           "- `__add__`로 더하기, `__str__`은 `\"분자/분모\"`.\n\n예: `add_fractions(1, 2, 1, 3)` → `\"5/6\"`, `add_fractions(1, 4, 1, 4)` → `\"1/2\"`",
           ["dunder", "class", "module"], 3,
           '''
            import math

            # 여기에 Fraction 클래스를 작성하세요


            def add_fractions(a, b, c, d):
                return str(Fraction(a, b) + Fraction(c, d))
           ''',
           [t(tid, args=list(a), ret=ref_frac(*a), desc=d) for a, tid, d in frac_cases if tid[0] == "t"]
           + [t("t3", args=[1, 0, 1, 2], raises="ValueError", desc="분모 0")]
           + [t(tid, args=list(a), ret=ref_frac(*a)) for a, tid, d in frac_cases if tid[0] == "h"],
           ["`__init__`에서 분모 0 검사 → `math.gcd`로 나눈 값 저장 → 분모가 음수면 분자·분모 부호를 함께 뒤집습니다.",
            "a/b + c/d = (a×d + c×b) / (b×d) 입니다. `__add__`에서 새 `Fraction`을 만들어 돌려주면 약분은 `__init__`이 해 줍니다.",
            "`__str__`은 f-string으로 `\"분자/분모\"`를 돌려줍니다."],
           '''
            import math


            class Fraction:
                def __init__(self, numerator, denominator):
                    if denominator == 0:
                        raise ValueError("분모는 0이 될 수 없습니다")
                    g = math.gcd(numerator, denominator)
                    numerator //= g
                    denominator //= g
                    if denominator < 0:
                        numerator, denominator = -numerator, -denominator
                    self.numerator = numerator
                    self.denominator = denominator

                def __add__(self, other):
                    n = self.numerator * other.denominator + other.numerator * self.denominator
                    return Fraction(n, self.denominator * other.denominator)

                def __str__(self):
                    return f"{self.numerator}/{self.denominator}"


            def add_fractions(a, b, c, d):
                return str(Fraction(a, b) + Fraction(c, d))
           ''', mode="function", name="add_fractions", checks={"required_syntax": ["class"]}),
    ])

# ====================================================================== Day 39
shape_cases = [([["circle", 1], ["rect", 2, 3]], "t1", "원과 직사각형"), ([], "t2", "없음"), ([["rect", 1.5, 2]], "h1", ""),
               ([["circle", 2], ["circle", 0.5], ["rect", 10, 1]], "h2", "")]
day39 = L(
    39, "상속", W, ["inheritance", "class", "method"],
    ["기존 클래스를 상속해 새 클래스를 만들 수 있다.", "메서드 재정의(오버라이딩)와 super()를 사용할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `__str__`, `__add__` 등 특수 메서드로 문법을 지원했습니다.",
            "quiz": [quiz("d39_review_q1", "`len(obj)`가 동작하려면 정의해야 하는 메서드는?", ["`__size__`", "`__len__`", "`__count__`", "`len`"], 1,
                          "`len()`은 `__len__`을 호출합니다.")]},
    concept={"title": "물려받고 바꾸기", "blocks": [
        text("`class 자식(부모):`처럼 쓰면 부모 클래스의 속성과 메서드를 **물려받습니다(상속)**. 자식에서 같은 이름의 메서드를 다시 정의하면 부모 것을 **덮어씁니다(오버라이딩)**."),
        code('''
            class Animal:
                def __init__(self, name):
                    self.name = name

                def speak(self):
                    return "..."

                def introduce(self):
                    return f"{self.name}: {self.speak()}"

            class Dog(Animal):
                def speak(self):
                    return "멍멍"

            class Cat(Animal):
                def speak(self):
                    return "야옹"

            for pet in [Dog("초코"), Cat("나비"), Animal("??")]:
                print(pet.introduce())
            print(isinstance(Dog("a"), Animal))
        ''', lines("초코: 멍멍", "나비: 야옹", "??: ...", True)),
        text("`super()`는 부모 클래스를 가리킵니다. 자식의 `__init__`에서 부모 초기화를 재사용하거나, 부모 메서드 결과에 무언가를 더할 때 씁니다."),
        code('''
            class Employee:
                def __init__(self, name, salary):
                    self.name = name
                    self.salary = salary

                def pay(self):
                    return self.salary

            class Manager(Employee):
                def __init__(self, name, salary, bonus):
                    super().__init__(name, salary)
                    self.bonus = bonus

                def pay(self):
                    return super().pay() + self.bonus

            print(Manager("민준", 300, 50).pay())
        ''', lines(350)),
        tip("부모의 `introduce()` 안에서 부른 `self.speak()`는 실제 객체의 종류에 맞는 메서드를 찾아갑니다. 같은 코드로 여러 종류를 처리하는 이 성질을 **다형성**이라고 합니다."),
    ]},
    fill_intro="정사각형을 직사각형의 자식 클래스로 만드세요.",
    coding_intro="도형 클래스 계층을 만들어 넓이를 계산하세요. `report`는 채점용입니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`class Child(Parent):` → 부모의 속성·메서드 상속.",
        "같은 이름의 메서드를 다시 정의하면 오버라이딩.",
        "`super().__init__(...)`, `super().메서드()`로 부모 기능 재사용.",
        "`isinstance(객체, 부모클래스)`는 자식 객체에도 True."],
        "quiz": [
            quiz("d39_summary_q1", "`class B(A):`에서 B의 객체가 A에만 정의된 메서드를 호출하면?", ["오류", "A의 메서드가 실행된다", "`None`", "B를 다시 정의해야 함"], 1,
                 "상속받은 메서드가 그대로 쓰입니다."),
            quiz("d39_summary_q2", "자식 `__init__`에서 부모의 초기화를 호출하는 코드는?", ["`Parent()`", "`self.__init__()`", "`super().__init__(...)`", "`init()`"], 2,
                 "`super()`가 부모를 가리킵니다.")]},
    exercises=[
        ex("d39_fill_1", "fill_blank", "정사각형은 직사각형",
           "`Square`가 `Rectangle`을 상속하도록 완성하세요. 한 변의 길이만 받아 부모의 초기화를 재사용합니다.",
           ["inheritance"], 1,
           '''
            class Rectangle:
                def __init__(self, w, h):
                    self.w = w
                    self.h = h

                def area(self):
                    return self.w * self.h


            class Square(____):
                def __init__(self, side):
                    ____().__init__(side, side)


            def check(side):
                s = Square(side)
                return [s.area(), isinstance(s, Rectangle)]
           ''',
           [t("t1", args=[3], ret=[9, True], desc="한 변 3"), t("h1", args=[1], ret=[1, True]), t("h2", args=[2.5], ret=[6.25, True])],
           ["괄호 안에는 부모 클래스 이름을 씁니다.", "부모 클래스를 가리키는 내장 함수입니다."],
           '''
            class Rectangle:
                def __init__(self, w, h):
                    self.w = w
                    self.h = h

                def area(self):
                    return self.w * self.h


            class Square(Rectangle):
                def __init__(self, side):
                    super().__init__(side, side)


            def check(side):
                s = Square(side)
                return [s.area(), isinstance(s, Rectangle)]
           ''', mode="function", name="check"),
        ex("d39_code_1", "coding", "도형 계층",
           "부모 클래스 `Shape`와 자식 `Circle(r)`, `Rect(w, h)`를 만드세요.\n\n"
           "- `Shape`에는 `name` 속성과 `describe()`가 있고, `describe()`는 `f\"{self.name} 넓이 {self.area():.2f}\"`를 돌려줍니다.\n"
           "- 자식은 `name`(`\"원\"`, `\"직사각형\"`)을 정하고 `area()`를 오버라이딩합니다. 원의 넓이는 `math.pi * r ** 2`.\n\n"
           "`report`는 채점용입니다. 예: `report([[\"circle\", 1], [\"rect\", 2, 3]])` → `[[\"원 넓이 3.14\", \"직사각형 넓이 6.00\"], 9.14]`",
           ["inheritance", "class", "method"], 2,
           '''
            import math

            # 여기에 Shape, Circle, Rect 클래스를 작성하세요


            def report(specs):
                shapes = []
                for s in specs:
                    shapes.append(Circle(s[1]) if s[0] == "circle" else Rect(s[1], s[2]))
                total = 0
                descriptions = []
                for shape in shapes:
                    descriptions.append(shape.describe())
                    total += shape.area()
                return [descriptions, round(total, 2)]
           ''',
           [t(tid, args=[s], ret=ref_shapes(s), desc=d, compare={"mode": "float", "tol": 1e-9}) for s, tid, d in shape_cases],
           ["`Shape.__init__(self, name)`에서 이름을 저장하고, 자식은 `super().__init__(...)`에 자기 이름 문자열을 넘깁니다.",
            "`describe`는 부모에만 두고, 그 안에서 `self.area()`를 부르면 자식의 `area`가 실행됩니다.",
            "`Shape.area()`에서 `NotImplementedError` 예외를 발생시켜 두면 자식이 꼭 구현해야 함을 알릴 수 있습니다."],
           '''
            import math


            class Shape:
                def __init__(self, name):
                    self.name = name

                def area(self):
                    raise NotImplementedError

                def describe(self):
                    return f"{self.name} 넓이 {self.area():.2f}"


            class Circle(Shape):
                def __init__(self, r):
                    super().__init__("원")
                    self.r = r

                def area(self):
                    return math.pi * self.r ** 2


            class Rect(Shape):
                def __init__(self, w, h):
                    super().__init__("직사각형")
                    self.w = w
                    self.h = h

                def area(self):
                    return self.w * self.h


            def report(specs):
                shapes = []
                for s in specs:
                    shapes.append(Circle(s[1]) if s[0] == "circle" else Rect(s[1], s[2]))
                total = 0
                descriptions = []
                for shape in shapes:
                    descriptions.append(shape.describe())
                    total += shape.area()
                return [descriptions, round(total, 2)]
           ''', mode="function", name="report", checks={"required_syntax": ["class"]}),
    ])

# ====================================================================== Day 40
acc_cases = [([["in", 1000], ["out", 300]], "t1", "입출금"), ([], "t2", "거래 없음"), ([["in", 1], ["in", 2], ["out", 3]], "h1", "")]
day40 = L(
    40, "캡슐화와 프로퍼티", W, ["property", "class", "exception"],
    ["밑줄(_) 관례로 내부 속성을 표시할 수 있다.", "@property와 setter로 읽기 전용 속성과 값 검증을 구현할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 상속과 `super()`로 클래스를 확장했습니다.",
            "quiz": [quiz("d40_review_q1", "자식 클래스가 부모 메서드를 같은 이름으로 다시 정의하는 것은?", ["상속", "오버라이딩", "캡슐화", "인스턴스화"], 1, "")]},
    concept={"title": "속성을 안전하게 지키기", "blocks": [
        text("외부에서 마음대로 바꾸면 안 되는 속성은 이름 앞에 `_`를 붙여 \"내부용\"임을 표시합니다(강제는 아닌 약속). "
             "`@property`를 붙인 메서드는 **괄호 없이 속성처럼** 읽히고, `@이름.setter`로 값을 넣을 때 검사할 수 있습니다."),
        code('''
            class Temperature:
                def __init__(self, celsius):
                    self._celsius = celsius

                @property
                def celsius(self):
                    return self._celsius

                @celsius.setter
                def celsius(self, value):
                    if value < -273.15:
                        raise ValueError("절대영도보다 낮을 수 없습니다")
                    self._celsius = value

                @property
                def fahrenheit(self):
                    return self._celsius * 9 / 5 + 32

            t = Temperature(25)
            print(t.fahrenheit)
            t.celsius = 30
            print(t.celsius, t.fahrenheit)
            try:
                t.celsius = -300
            except ValueError as e:
                print(e)
        ''', lines(25 * 9 / 5 + 32, f"30 {30 * 9 / 5 + 32}", "절대영도보다 낮을 수 없습니다")),
        tip("setter가 없는 property에 값을 넣으면 `AttributeError`가 납니다. 잔액처럼 **메서드를 통해서만 바뀌어야 하는 값**을 읽기 전용으로 만들 때 유용합니다."),
    ]},
    fill_intro="이름을 합쳐 주는 읽기 전용 속성을 만드세요.",
    coding_intro="잔액을 읽기 전용으로 보호하는 계좌 클래스를 만드세요. `simulate`는 채점용입니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`_속성`은 \"내부용\" 약속.",
        "`@property`: 메서드를 괄호 없는 속성처럼 읽기.",
        "`@이름.setter`: 값을 넣을 때 검증.",
        "setter가 없으면 읽기 전용(쓰면 `AttributeError`)."],
        "quiz": [
            quiz("d40_summary_q1", "`@property def area(self): ...`를 올바르게 사용하는 코드는?", ["`obj.area()`", "`obj.area`", "`area(obj)`", "`obj.get_area()`"], 1,
                 "property는 괄호 없이 읽습니다."),
            quiz("d40_summary_q2", "setter 없는 property에 `obj.x = 1`을 하면?", ["값이 바뀐다", "`AttributeError`", "`None`", "무시된다"], 1, "읽기 전용입니다.")]},
    exercises=[
        ex("d40_fill_1", "fill_blank", "성과 이름 합치기",
           "`full_name`을 괄호 없이 읽을 수 있는 속성으로 만드세요.\n\n예: `check(\"민준\", \"김\")` → `\"김민준\"`",
           ["property"], 1,
           '''
            class Person:
                def __init__(self, first, last):
                    self.first = first
                    self.last = last

                @____
                def full_name(self):
                    return f"{self.last}{self.first}"


            def check(first, last):
                return Person(first, last).____
           ''',
           [t("t1", args=["민준", "김"], ret="김민준", desc="기본"), t("h1", args=["", "이"], ret="이"), t("h2", args=["Ada", "Lovelace "], ret="Lovelace Ada")],
           ["메서드를 속성처럼 만드는 데코레이터 이름입니다.", "property는 괄호 없이 이름만으로 읽습니다."],
           '''
            class Person:
                def __init__(self, first, last):
                    self.first = first
                    self.last = last

                @property
                def full_name(self):
                    return f"{self.last}{self.first}"


            def check(first, last):
                return Person(first, last).full_name
           ''', mode="function", name="check"),
        ex("d40_code_1", "coding", "보호된 잔액",
           "`Account` 클래스를 작성하세요.\n\n"
           "- 잔액은 내부 속성 `_balance`에 저장하고, `balance`는 **읽기 전용 property**로 제공합니다.\n"
           "- `deposit(amount)`, `withdraw(amount)`: 금액이 0 이하이거나 잔액보다 많이 출금하면 `ValueError`.\n"
           "- 성공한 거래는 `history` 리스트에 `(종류, 금액)`으로 기록합니다.\n\n`simulate`는 채점용입니다(마지막 값은 잔액을 직접 바꿀 수 있는지 여부).",
           ["property", "class", "method", "exception"], 2,
           '''
            # 여기에 Account 클래스를 작성하세요


            def simulate(ops):
                acc = Account()
                for kind, amount in ops:
                    if kind == "in":
                        acc.deposit(amount)
                    else:
                        acc.withdraw(amount)
                try:
                    acc.balance = 0
                    can_set = True
                except AttributeError:
                    can_set = False
                return [acc.balance, len(acc.history), can_set]
           ''',
           [t(tid, args=[o], ret=ref_account(o), desc=d) for o, tid, d in acc_cases if tid[0] == "t"]
           + [t("t3", args=[[["out", 1]]], raises="ValueError", desc="잔액 부족"), t("h2", args=[[["in", 0]]], raises="ValueError")]
           + [t(tid, args=[o], ret=ref_account(o)) for o, tid, d in acc_cases if tid[0] == "h"],
           ["`__init__`에서 `self._balance = 0`, `self.history = []`로 시작하세요.",
            "`@property def balance(self): return self._balance`만 있고 setter가 없으면 읽기 전용이 됩니다.",
            "`deposit`/`withdraw`는 검사 → `_balance` 변경 → `history.append(...)` 순서입니다."],
           '''
            class Account:
                def __init__(self):
                    self._balance = 0
                    self.history = []

                @property
                def balance(self):
                    return self._balance

                def deposit(self, amount):
                    if amount <= 0:
                        raise ValueError("금액은 양수여야 합니다")
                    self._balance += amount
                    self.history.append(("in", amount))

                def withdraw(self, amount):
                    if amount <= 0 or amount > self._balance:
                        raise ValueError("출금할 수 없는 금액입니다")
                    self._balance -= amount
                    self.history.append(("out", amount))


            def simulate(ops):
                acc = Account()
                for kind, amount in ops:
                    if kind == "in":
                        acc.deposit(amount)
                    else:
                        acc.withdraw(amount)
                try:
                    acc.balance = 0
                    can_set = True
                except AttributeError:
                    can_set = False
                return [acc.balance, len(acc.history), can_set]
           ''', mode="function", name="simulate", checks={"required_syntax": ["class"]}),
    ])

# ====================================================================== Day 41
prod_cases = [(["펜,1000,문구", "노트,3000", "물,800,식품"], 0.1, "t1", "분류 생략"), ([], 0.5, "h1", ""), (["책,15000,도서"], 0, "h2", "")]
day41 = L(
    41, "클래스 변수와 dataclass", W, ["classmethod", "class"],
    ["클래스 변수와 인스턴스 변수를 구분할 수 있다.", "@classmethod, @staticmethod, @dataclass를 쓸 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `@property`로 속성을 보호했습니다.",
            "quiz": [quiz("d41_review_q1", "`_balance`처럼 이름 앞의 밑줄 하나가 뜻하는 것은?", ["비공개 강제", "내부용이라는 약속", "상수", "클래스 변수"], 1,
                          "파이썬은 강제하지 않고, 개발자 사이의 약속입니다.")]},
    concept={"title": "클래스 전체가 공유하는 것들", "blocks": [
        text("클래스 바로 아래에 쓴 변수는 모든 객체가 공유하는 **클래스 변수**입니다. `@classmethod`는 객체 대신 클래스(`cls`)를 받아 **다른 방식의 생성자**를 만들 때, "
             "`@staticmethod`는 `self`가 필요 없는 도우미 함수를 클래스 안에 둘 때 씁니다."),
        code('''
            class Student:
                school = "파이썬고"
                count = 0

                def __init__(self, name):
                    self.name = name
                    Student.count += 1

                @classmethod
                def from_string(cls, text):
                    name = text.split(":")[1]
                    return cls(name)

                @staticmethod
                def is_valid_name(name):
                    return len(name) >= 2

            a = Student("민준")
            b = Student.from_string("이름:서연")
            print(b.name, Student.count, a.school)
            print(Student.is_valid_name("A"))
        ''', lines("서연 2 파이썬고", False)),
        text("데이터를 담는 것이 주 목적인 클래스는 `@dataclass`가 `__init__`, `__repr__`, `__eq__`를 자동으로 만들어 줍니다. 필드는 `이름: 자료형` 형식으로 적습니다."),
        code('''
            from dataclasses import dataclass

            @dataclass
            class Item:
                name: str
                price: int
                qty: int = 1

                def total(self):
                    return self.price * self.qty

            a = Item("펜", 1000, 3)
            print(a)
            print(a.total())
            print(a == Item("펜", 1000, 3))
        ''', lines("Item(name='펜', price=1000, qty=3)", 3000, True)),
        tip("클래스 변수를 `self.count += 1`로 바꾸면 그 객체에만 새 인스턴스 변수가 생깁니다. 공유 값을 바꿀 때는 `클래스이름.변수`로 쓰세요."),
    ]},
    fill_intro="dataclass로 좌표를 정의하세요.",
    coding_intro="dataclass와 classmethod, staticmethod를 함께 씁니다. `run`은 채점용입니다.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "클래스 변수: 모든 객체가 공유, `클래스.변수`로 수정.",
        "`@classmethod def f(cls, ...)`: 대체 생성자 등.",
        "`@staticmethod`: self가 필요 없는 도우미.",
        "`@dataclass`: `__init__`·`__repr__`·`__eq__` 자동 생성."],
        "quiz": [
            quiz("d41_summary_q1", "`@classmethod`의 첫 매개변수 관례 이름은?", ["`self`", "`cls`", "`klass`", "없음"], 1, ""),
            quiz("d41_summary_q2", "`@dataclass`가 자동으로 만들어 주지 **않는** 것은?", ["`__init__`", "`__repr__`", "`__eq__`", "속성 검증 로직"], 3,
                 "검증은 직접 작성해야 합니다(`__post_init__` 등).")]},
    exercises=[
        ex("d41_fill_1", "fill_blank", "dataclass 좌표",
           "`y`의 기본값이 0인 dataclass `Point`를 완성하세요.",
           ["classmethod"], 1,
           '''
            from dataclasses import ____


            @dataclass
            class Point:
                x: int
                y: int = ____


            def check(x):
                p = Point(x)
                return [p.x, p.y, p == Point(x, 0)]
           ''',
           [t("t1", args=[3], ret=[3, 0, True], desc="기본값"), t("h1", args=[-1], ret=[-1, 0, True])],
           ["데코레이터 이름과 같은 이름을 모듈에서 가져옵니다.", "기본값은 숫자 0입니다."],
           '''
            from dataclasses import dataclass


            @dataclass
            class Point:
                x: int
                y: int = 0


            def check(x):
                p = Point(x)
                return [p.x, p.y, p == Point(x, 0)]
           ''', mode="function", name="check"),
        ex("d41_code_1", "coding", "상품 목록",
           "dataclass `Product(name, price, category=\"기타\")`를 만들고 다음을 추가하세요.\n\n"
           "- `@classmethod from_csv(cls, line)`: `\"이름,가격,분류\"` 또는 `\"이름,가격\"`을 해석해 객체를 만듭니다(가격은 정수).\n"
           "- `@staticmethod discounted(price, rate)`: `int(price * (1 - rate))`를 반환합니다.\n\n"
           "`run`은 채점용입니다. 예: `run([\"펜,1000,문구\", \"노트,3000\"], 0.1)` → `[[[\"펜\", 1000, \"문구\"], [\"노트\", 3000, \"기타\"]], 3600]`",
           ["classmethod", "class", "string_parsing"], 2,
           '''
            from dataclasses import dataclass

            # 여기에 Product 클래스를 작성하세요


            def run(lines, rate):
                products = [Product.from_csv(line) for line in lines]
                rows = [[p.name, p.price, p.category] for p in products]
                total = sum(Product.discounted(p.price, rate) for p in products)
                return [rows, total]
           ''',
           [t(tid, args=[ls, r], ret=ref_products(ls, r), desc=d) for ls, r, tid, d in prod_cases],
           ["필드 세 개를 선언하고 `category`에 기본값을 줍니다.",
            "`from_csv`에서 `line.split(\",\")` 결과의 길이에 따라 `cls(이름, int(가격))` 또는 `cls(이름, int(가격), 분류)`를 반환합니다.",
            "`discounted`는 `self`도 `cls`도 받지 않습니다."],
           '''
            from dataclasses import dataclass


            @dataclass
            class Product:
                name: str
                price: int
                category: str = "기타"

                @classmethod
                def from_csv(cls, line):
                    parts = line.split(",")
                    if len(parts) >= 3 and parts[2]:
                        return cls(parts[0], int(parts[1]), parts[2])
                    return cls(parts[0], int(parts[1]))

                @staticmethod
                def discounted(price, rate):
                    return int(price * (1 - rate))


            def run(lines, rate):
                products = [Product.from_csv(line) for line in lines]
                rows = [[p.name, p.price, p.category] for p in products]
                total = sum(Product.discounted(p.price, rate) for p in products)
                return [rows, total]
           ''', mode="function", name="run", checks={"required_syntax": ["class"]}),
    ])

# ====================================================================== Day 42 (review)
lib_cmds = [[["add", "파이썬"], ["add", "자료구조"], ["borrow", "파이썬", "민준"], ["borrow", "파이썬", "서연"], ["return", "자료구조"],
             ["borrow", "C언어", "지호"], ["return", "파이썬"], ["add", "파이썬"]],
            [["add", "a"], ["return", "a"]], []]
bal_cases = [("(a[b]{c})", "t1", "올바름"), ("(]", "t2", "짝 안 맞음"), ("", "h1", ""), ("((()", "h2", ""), ("{[()()]}x", "h3", ""), ("}{", "h4", "")]
day42 = L(
    42, "6주차 누적 복습", W, ["class", "method", "dunder", "inheritance", "property", "classmethod"],
    ["클래스·메서드·특수 메서드·상속·프로퍼티를 조합해 작은 시스템을 설계할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 36 | 클래스와 객체 | `class`, `__init__`, `self.속성` |\n"
        "| 37 | 메서드 | `def m(self, ...)`, `obj.m()` |\n"
        "| 38 | 특수 메서드 | `__str__`, `__repr__`, `__add__`, `__eq__`, `__len__` |\n"
        "| 39 | 상속 | `class B(A)`, 오버라이딩, `super()` |\n"
        "| 40 | 캡슐화 | `_속성`, `@property`, setter |\n"
        "| 41 | 클래스 수준 | 클래스 변수, `@classmethod`, `@staticmethod`, `@dataclass` |"),
        "quiz": [
            quiz("d42_review_q1", "객체를 리스트에 넣고 출력할 때 보이는 모양을 정하는 메서드는?", ["`__str__`", "`__repr__`", "`__init__`", "`__len__`"], 1, ""),
            quiz("d42_review_q2", "\"관리자는 직원이다\" 관계를 코드로 표현하면?", ["`class Employee(Manager)`", "`class Manager(Employee)`", "`Manager = Employee`", "`@dataclass`"], 1,
                 "자식(Manager)이 부모(Employee)를 상속합니다.")]},
    concept={"title": "객체로 설계하기", "blocks": [
        text("객체지향 설계는 \"어떤 **물건**(명사)이 있고, 각각 **무엇을 할 수 있나**(동사)\"를 정하는 일입니다. 명사는 클래스, 동사는 메서드가 됩니다. "
             "규칙에 어긋나는 요청은 예외로 알리고, 바깥(화면·입출력)은 그 예외를 받아 메시지로 바꿉니다."),
        code('''
            class Stack:
                def __init__(self):
                    self._items = []

                def push(self, x):
                    self._items.append(x)

                def pop(self):
                    if not self._items:
                        raise IndexError("빈 스택")
                    return self._items.pop()

                def __len__(self):
                    return len(self._items)

            s = Stack()
            s.push(1)
            s.push(2)
            print(s.pop(), len(s))
        ''', lines("2 1")),
        tip("오늘 도전 문제의 괄호 검사는 스택(나중에 넣은 것을 먼저 꺼내는 구조)의 대표적인 활용입니다."),
    ]},
    fill_intro="스택 클래스의 빈칸을 채우세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "6주차 마무리", "points": [
        "클래스 = 데이터(속성) + 동작(메서드).",
        "특수 메서드로 파이썬 문법과 연결, 상속으로 재사용, property로 보호.",
        "규칙 위반은 예외로, 메시지 출력은 바깥에서.",
        "다음 주: 컴프리헨션·제너레이터·데코레이터로 더 파이썬다운 코드 쓰기."],
        "quiz": [
            quiz("d42_summary_q1", "스택에서 `push(1)`, `push(2)`, `push(3)` 후 `pop()`의 결과는?", ["1", "2", "3", "오류"], 2, "나중에 넣은 것이 먼저 나옵니다."),
            quiz("d42_summary_q2", "설계할 때 메서드가 되기 알맞은 것은?", ["명사", "동사(할 수 있는 일)", "숫자", "모듈 이름"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d42_fill_1", "fill_blank", "스택",
           "`Stack`의 `push`와 `peek`(꺼내지 않고 맨 위 값 보기)을 완성하세요. 빈 스택에서 `peek`하면 `IndexError`입니다.",
           ["class", "method", "dunder"], 1,
           '''
            class Stack:
                def __init__(self):
                    self._items = []

                def push(self, x):
                    self._items.____(x)

                def peek(self):
                    if not self._items:
                        raise IndexError("빈 스택")
                    return self._items[____]

                def __len__(self):
                    return len(self._items)


            def check(values):
                s = Stack()
                for v in values:
                    s.push(v)
                return [s.peek(), len(s)]
           ''',
           [t("t1", args=[[1, 2, 3]], ret=[3, 3], desc="세 개"), t("t2", args=[[]], raises="IndexError", desc="빈 스택"), t("h1", args=[["a"]], ret=["a", 1])],
           ["리스트 끝에 추가하는 메서드입니다.", "리스트의 마지막 원소를 가리키는 인덱스입니다."],
           '''
            class Stack:
                def __init__(self):
                    self._items = []

                def push(self, x):
                    self._items.append(x)

                def peek(self):
                    if not self._items:
                        raise IndexError("빈 스택")
                    return self._items[-1]

                def __len__(self):
                    return len(self._items)


            def check(values):
                s = Stack()
                for v in values:
                    s.push(v)
                return [s.peek(), len(s)]
           ''', mode="function", name="check"),
        ex("d42_code_1", "coding", "도서관 시스템",
           "`Library` 클래스를 작성하세요. 책 이름 → 빌린 사람(없으면 `None`)을 관리합니다.\n\n"
           "- `add(title)`: 이미 있으면 `ValueError(\"이미 있는 책: 제목\")`\n"
           "- `borrow(title, person)`: 없는 책이면 `KeyError(title)`, 대출 중이면 `ValueError(\"대출 중: 제목\")`\n"
           "- `return_book(title)`: 없는 책이면 `KeyError(title)`, 빌려 가지 않은 책이면 `ValueError(\"대출 기록 없음: 제목\")`\n\n"
           "`simulate`는 채점용이며 성공 메시지와 예외 메시지를 기록합니다.",
           ["class", "method", "exception", "dict"], 3,
           '''
            # 여기에 Library 클래스를 작성하세요


            def simulate(commands):
                lib = Library()
                log = []
                for c in commands:
                    try:
                        if c[0] == "add":
                            lib.add(c[1])
                            log.append(f"추가: {c[1]}")
                        elif c[0] == "borrow":
                            lib.borrow(c[1], c[2])
                            log.append(f"대출: {c[1]} → {c[2]}")
                        else:
                            lib.return_book(c[1])
                            log.append(f"반납: {c[1]}")
                    except KeyError as e:
                        log.append(f"오류: 없는 책 {e.args[0]}")
                    except ValueError as e:
                        log.append(f"오류: {e}")
                return log
           ''',
           [t("t1", args=[lib_cmds[0]], ret=ref_library(lib_cmds[0]), desc="여러 명령")]
           + [t(f"h{i}", args=[c_], ret=ref_library(c_)) for i, c_ in enumerate(lib_cmds[1:], start=1)],
           ["`__init__`에서 `self.books = {}`로 시작합니다. 값이 `None`이면 대출 가능.",
            "각 메서드는 검사 순서가 중요합니다: 먼저 책이 있는지(`KeyError`), 그다음 상태(`ValueError`).",
            "`KeyError(title)`처럼 책 이름을 넘겨야 `simulate`가 메시지를 만들 수 있습니다."],
           '''
            class Library:
                def __init__(self):
                    self.books = {}

                def add(self, title):
                    if title in self.books:
                        raise ValueError(f"이미 있는 책: {title}")
                    self.books[title] = None

                def borrow(self, title, person):
                    if title not in self.books:
                        raise KeyError(title)
                    if self.books[title] is not None:
                        raise ValueError(f"대출 중: {title}")
                    self.books[title] = person

                def return_book(self, title):
                    if title not in self.books:
                        raise KeyError(title)
                    if self.books[title] is None:
                        raise ValueError(f"대출 기록 없음: {title}")
                    self.books[title] = None


            def simulate(commands):
                lib = Library()
                log = []
                for c in commands:
                    try:
                        if c[0] == "add":
                            lib.add(c[1])
                            log.append(f"추가: {c[1]}")
                        elif c[0] == "borrow":
                            lib.borrow(c[1], c[2])
                            log.append(f"대출: {c[1]} → {c[2]}")
                        else:
                            lib.return_book(c[1])
                            log.append(f"반납: {c[1]}")
                    except KeyError as e:
                        log.append(f"오류: 없는 책 {e.args[0]}")
                    except ValueError as e:
                        log.append(f"오류: {e}")
                return log
           ''', mode="function", name="simulate", checks={"required_syntax": ["class"]}),
        ex("d42_code_2", "coding", "[도전] 괄호 짝 검사",
           "문자열의 괄호 `()`, `[]`, `{}`가 올바르게 짝지어져 있는지 **반환**하세요. 괄호가 아닌 문자는 무시합니다. 스택을 사용해 보세요.\n\n"
           "예: `balanced(\"(a[b]{c})\")` → `True`, `balanced(\"(]\")` → `False`",
           ["class", "list_method"], 3,
           '''
            def balanced(text):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_balanced(s), desc=d) for s, tid, d in bal_cases],
           ["여는 괄호를 만나면 스택에 넣고, 닫는 괄호를 만나면 맨 위의 여는 괄호와 짝이 맞는지 확인합니다.",
            "닫는 괄호 → 여는 괄호 짝을 딕셔너리 `{\")\": \"(\", ...}`로 두면 편합니다.",
            "마지막에 스택이 비어 있어야 모든 괄호가 닫힌 것입니다."],
           '''
            def balanced(text):
                pairs = {")": "(", "]": "[", "}": "{"}
                stack = []
                for ch in text:
                    if ch in "([{":
                        stack.append(ch)
                    elif ch in pairs:
                        if not stack or stack.pop() != pairs[ch]:
                            return False
                return len(stack) == 0
           ''', mode="function", name="balanced", required=False),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day36, day37, day38, day39, day40, day41, day42])
