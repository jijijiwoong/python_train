"""Week 18 (Day 120-126): 텐서와 자동 미분."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, write_lessons  # noqa: E402

W = 18

# ====================================================================== Day 120
day120 = D(
    120, "PyTorch와 텐서", W, ["tensor"],
    ["torch.tensor, zeros, ones, arange로 텐서를 만들 수 있다.", "shape, dtype, ndim으로 텐서의 정보를 확인할 수 있다."],
    "4단계를 시작합니다. 3단계에서는 scikit-learn이 학습을 대신해 주었지만, 이제는 **PyTorch**로 신경망을 직접 만들고 학습시킵니다. "
    "PyTorch의 기본 자료형은 **텐서**(tensor)로, Day 50에서 배운 NumPy 배열과 아주 비슷합니다.",
    [("NumPy 배열의 모양을 알려 주는 속성은?", ["`size`", "`shape`", "`len`", "`dim`"], 1)],
    "텐서 만들기",
    "텐서는 숫자를 담는 n차원 배열입니다. NumPy 배열과 다른 점은 **GPU 계산**과 **자동 미분**을 지원한다는 것입니다.\n\n"
    "- `torch.tensor(리스트)`: 값으로 만들기\n- `torch.zeros(행, 열)`, `torch.ones(...)`: 0 또는 1로 채우기\n"
    "- `torch.arange(시작, 끝, 간격)`: 범위 값\n\n정수로 만들면 `torch.int64`, 실수로 만들면 `torch.float32`가 기본 자료형입니다. "
    "값 하나짜리 텐서는 `.item()`으로 파이썬 숫자로 꺼냅니다.",
    '''
    import torch

    a = torch.tensor([[1, 2, 3], [4, 5, 6]])
    print(a)
    print(a.shape, a.ndim, a.dtype)
    b = torch.zeros(2, 3)
    print(b.dtype)
    print(torch.arange(0, 10, 3))
    print(a.sum().item())
    ''',
    "신경망의 가중치와 입력은 거의 항상 `float32`입니다. `torch.tensor(값, dtype=torch.float32)`처럼 자료형을 지정할 수 있어요.",
    "텐서를 만들고 정보를 확인하세요.", "텐서로 간단한 통계를 구하세요.",
    ["텐서 = GPU·자동 미분을 지원하는 n차원 배열.", "`torch.tensor`, `zeros`, `ones`, `arange`로 만든다.",
     "`shape`, `ndim`, `dtype`으로 정보 확인.", "`.item()`으로 값 하나를 파이썬 숫자로."],
    [("`torch.tensor([1.5, 2.0])`의 dtype은?", ["torch.int64", "torch.float32", "torch.float64", "torch.bool"], 1),
     ("`torch.zeros(3, 4).shape`는?", ["(3, 4)", "(4, 3)", "12", "(12,)"], 0)],
    [
        X("d120_fill_1", "텐서 정보",
          "값 목록으로 `float32` 텐서를 만들어 `[모양 리스트, 차원 수, dtype 문자열]`을 반환하세요.", ["tensor"], 1,
          '''
          import torch


          def info(values):
              x = torch.tensor(values, dtype=torch.float32)
              return [list(x.shape), x.ndim, str(x.dtype)]
          ''', "info", [[[[1, 2], [3, 4]]], [[[1, 2, 3]]], [[5]]],
          ["값 목록을 텐서로 바꾸는 함수 이름입니다.", "모양을 알려 주는 속성입니다."], blanks=["tensor", "shape"]),
        X("d120_code_1", "텐서 통계",
          "숫자 목록을 `float32` 텐서로 만들어 `[합, 평균, 최댓값]`을 파이썬 숫자로 반환하세요(평균은 소수 넷째 자리).", ["tensor"], 1,
          '''
          import torch


          def stats(values):
              x = torch.tensor(values, dtype=torch.float32)
              return [x.sum().item(), round(x.mean().item(), 4), x.max().item()]
          ''', "stats", [[[1, 2, 3, 4]], [[2.5, -1, 7]], [[10]]],
          ["텐서에도 `sum()`, `mean()`, `max()` 메서드가 있습니다.", "결과는 텐서이므로 `.item()`으로 숫자를 꺼냅니다."]),
    ], review_title="4단계 시작")

# ====================================================================== Day 121
day121 = D(
    121, "텐서 연산과 브로드캐스팅", W, ["tensor_ops", "tensor"],
    ["원소별 연산과 행렬 곱(@)을 구분할 수 있다.", "브로드캐스팅과 dim 방향 집계를 사용할 수 있다."],
    "어제는 텐서를 만들고 정보를 확인했습니다.",
    [("`torch.arange(0, 6, 2)`의 값은?", ["[0, 2, 4]", "[0, 2, 4, 6]", "[2, 4, 6]", "[0, 1, 2]"], 0)],
    "계산하기",
    "`+ - * /`는 같은 위치끼리 계산하는 **원소별 연산**, `@`는 **행렬 곱**입니다. 신경망의 한 층은 결국 `X @ W + b`입니다.\n\n"
    "모양이 다르면 NumPy처럼 **브로드캐스팅**이 적용됩니다. `sum(dim=0)`은 행 방향으로 접어 열마다, `sum(dim=1)`은 행마다 계산합니다.",
    '''
    import torch

    X = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    W = torch.tensor([[1.0], [0.5]])
    print(X * 2)
    print(X @ W)
    print(X + torch.tensor([10.0, 20.0]))
    print(X.sum(dim=0), X.mean(dim=1))
    ''',
    "행렬 곱은 앞 텐서의 열 수와 뒤 텐서의 행 수가 같아야 합니다. `(2, 3) @ (3, 4)` → `(2, 4)`.",
    "선형 변환을 계산하세요.", "열마다 표준화하세요.",
    ["`*`는 원소별 곱, `@`는 행렬 곱.", "신경망 층 = `X @ W + b`.", "모양이 다르면 브로드캐스팅.",
     "`dim=0`은 열마다, `dim=1`은 행마다 집계."],
    [("`(4, 3) @ (3, 2)`의 결과 모양은?", ["(4, 2)", "(3, 3)", "(4, 3)", "오류"], 0),
     ("2차원 텐서에서 열마다 평균을 구하려면?", ["`mean(dim=0)`", "`mean(dim=1)`", "`mean()`", "`mean(dim=2)`"], 0)],
    [
        X("d121_fill_1", "선형 변환", "입력 `x`, 가중치 `w`, 편향 `b`로 `x @ w + b`를 계산해 반환하세요.", ["tensor_ops"], 1,
          '''
          import torch


          def linear(x, w, b):
              X = torch.tensor(x, dtype=torch.float32)
              W = torch.tensor(w, dtype=torch.float32)
              return X @ W + torch.tensor(b, dtype=torch.float32)
          ''', "linear", [[[[1, 2]], [[1], [1]], [0.5]], [[[1, 0], [0, 1]], [[2, 3], [4, 5]], [1, -1]]],
          ["행렬 곱 연산자는 기호 하나입니다.", "이메일 주소에 들어가는 기호와 같습니다."], blanks=["@"]),
        X("d121_code_1", "열 표준화",
          "2차원 목록을 `float32` 텐서로 만들어 열마다 `(x - 평균) / 표준편차`로 바꾼 텐서를 반환하세요. 표준편차는 `std(dim=0, correction=0)`으로 구합니다.",
          ["tensor_ops"], 2,
          '''
          import torch


          def standardize(rows):
              X = torch.tensor(rows, dtype=torch.float32)
              return (X - X.mean(dim=0)) / X.std(dim=0, correction=0)
          ''', "standardize", [[[[1, 10], [3, 30]]], [[[1, 2, 3], [4, 0, 6], [7, 8, 0]]]],
          ["평균과 표준편차를 `dim=0`으로 구하면 열마다 값이 하나씩 나옵니다.", "브로드캐스팅 덕분에 `(n, m) - (m,)`이 그대로 계산됩니다."]),
    ])

# ====================================================================== Day 122
day122 = D(
    122, "인덱싱과 모양 바꾸기", W, ["tensor_shape", "tensor"],
    ["인덱싱·슬라이싱으로 텐서 일부를 꺼낼 수 있다.", "reshape, unsqueeze, cat, stack으로 모양을 바꿀 수 있다."],
    "어제는 텐서 연산과 브로드캐스팅을 배웠습니다.",
    [("`X`가 (2, 3)일 때 `X.sum(dim=1)`의 모양은?", ["(2,)", "(3,)", "(2, 3)", "()"], 0)],
    "모양 다루기",
    "신경망에서는 \"모양이 맞지 않는다\"는 오류를 가장 자주 만납니다. 모양 바꾸기 도구를 익혀 둡시다.\n\n"
    "- `x[1]`, `x[:, 2]`: 행·열 꺼내기(NumPy와 같음)\n- `reshape(3, 4)`: 원소 수는 그대로 모양만 바꾸기, `-1`은 자동 계산\n"
    "- `unsqueeze(0)`: 크기 1인 차원 추가, `squeeze()`: 크기 1인 차원 제거\n- `torch.cat`: 기존 차원으로 이어 붙이기, `torch.stack`: 새 차원을 만들어 쌓기",
    '''
    import torch

    x = torch.arange(12).reshape(3, 4)
    print(x)
    print(x[1], x[:, 2])
    print(x.reshape(-1, 6).shape)
    print(x[0].unsqueeze(0).shape)
    a, b = torch.ones(2), torch.zeros(2)
    print(torch.cat([a, b]).shape, torch.stack([a, b]).shape)
    ''',
    "모델은 보통 (배치 크기, 특성 수) 모양을 기대합니다. 샘플 하나를 넣을 때 `unsqueeze(0)`으로 배치 차원을 만들어 주는 이유입니다.",
    "reshape로 모양을 바꾸세요.", "값을 배치로 나누어 합을 구하세요.",
    ["인덱싱·슬라이싱은 NumPy와 같다.", "`reshape`의 `-1`은 자동 계산.", "`unsqueeze`/`squeeze`로 크기 1 차원 추가·제거.",
     "`cat`은 이어 붙이기, `stack`은 새 차원으로 쌓기."],
    [("원소 12개 텐서를 `reshape(-1, 3)` 하면?", ["(4, 3)", "(3, 4)", "(12, 3)", "오류"], 0),
     ("모양 (2,) 텐서 두 개를 `torch.stack` 하면?", ["(4,)", "(2, 2)", "(2,)", "(1, 4)"], 1)],
    [
        X("d122_fill_1", "열 수 맞추기",
          "`torch.arange(n)`을 열이 `cols`개인 2차원으로 바꾸고 `[모양 리스트, 첫 열 리스트]`를 반환하세요.", ["tensor_shape"], 1,
          '''
          import torch


          def arrange(n, cols):
              x = torch.arange(n).reshape(-1, cols)
              return [list(x.shape), x[:, 0].tolist()]
          ''', "arrange", [[12, 4], [6, 2], [10, 5]],
          ["원소 수는 유지하고 모양만 바꾸는 메서드입니다.", "행 수를 자동으로 계산하게 하는 값입니다."], blanks=["reshape", "-1"]),
        X("d122_code_1", "배치로 나누기",
          "숫자 목록을 `batch_size`개씩 묶어 2차원 텐서로 만드세요. 나누어떨어지지 않는 뒤쪽 나머지는 버립니다. `[모양 리스트, 행마다의 합 리스트]`를 반환하세요.",
          ["tensor_shape", "tensor_ops"], 2,
          '''
          import torch


          def batchify(values, batch_size):
              usable = len(values) // batch_size * batch_size
              x = torch.tensor(values[:usable]).reshape(-1, batch_size)
              return [list(x.shape), x.sum(dim=1).tolist()]
          ''', "batchify", [[[1, 2, 3, 4, 5, 6, 7], 3], [[5, 5, 5, 5], 2], [list(range(10)), 4]],
          ["사용할 개수는 `len(values) // batch_size * batch_size`입니다.", "자른 뒤 `reshape(-1, batch_size)`, 행마다 합은 `sum(dim=1)`."]),
    ])

# ====================================================================== Day 123
day123 = D(
    123, "NumPy와 텐서 오가기", W, ["tensor", "numpy_array"],
    ["NumPy 배열과 텐서를 서로 변환할 수 있다.", "자료형을 float32로 맞추고 argmax로 위치를 찾을 수 있다."],
    "어제는 텐서의 모양을 바꾸는 방법을 배웠습니다.",
    [("크기 1인 차원을 새로 추가하는 메서드는?", ["`squeeze`", "`unsqueeze`", "`reshape`", "`cat`"], 1)],
    "NumPy와 함께 쓰기",
    "데이터는 NumPy·pandas로 준비하고 학습은 PyTorch로 하는 경우가 많습니다.\n\n"
    "- `torch.from_numpy(arr)`: 메모리를 **공유**하는 텐서(한쪽을 바꾸면 다른 쪽도 바뀜)\n- `torch.tensor(arr)`: 복사본\n"
    "- `t.numpy()`: 텐서 → 배열\n\nNumPy 실수 배열은 `float64`라서 모델에 넣기 전에 `.float()`로 `float32`로 바꿉니다. "
    "가장 큰 값의 위치는 `argmax()`로 찾습니다.",
    '''
    import numpy as np
    import torch

    arr = np.array([1.0, 2.0, 3.0])
    shared = torch.from_numpy(arr)
    copied = torch.tensor(arr)
    arr[0] = 100
    print(shared, copied)
    print(shared.dtype, shared.float().dtype)
    t = torch.tensor([[3, 9], [7, 1]])
    print(t.numpy().tolist(), t.argmax().item(), t.argmax(dim=1))
    ''',
    "`argmax()`에 dim을 주지 않으면 모든 값을 한 줄로 펼친 위치를 돌려줍니다. 분류 모델의 예측은 보통 `argmax(dim=1)`입니다.",
    "배열을 float32 텐서로 바꾸세요.", "합이 가장 큰 행을 찾으세요.",
    ["`from_numpy`는 메모리 공유, `torch.tensor`는 복사.", "`.numpy()`로 다시 배열로.", "NumPy 실수(float64) → `.float()`로 float32.",
     "`argmax`로 최댓값 위치."],
    [("`torch.from_numpy(arr)` 후 `arr`을 바꾸면?", ["텐서도 바뀐다", "텐서는 그대로", "오류", "복사본이 생긴다"], 0),
     ("NumPy 실수 배열을 변환한 텐서의 기본 dtype은?", ["float32", "float64", "int64", "float16"], 1)],
    [
        X("d123_fill_1", "자료형 맞추기",
          "목록으로 NumPy 배열을 만들고 텐서로 바꾼 뒤 `float32`로 변환해 `[dtype 문자열, 합]`을 반환하세요.", ["tensor", "numpy_array"], 1,
          '''
          import numpy as np
          import torch


          def to_float_tensor(values):
              arr = np.array(values, dtype=float)
              t = torch.from_numpy(arr).float()
              return [str(t.dtype), t.sum().item()]
          ''', "to_float_tensor", [[[1, 2, 3.5]], [[-1, 1]]],
          ["NumPy 배열에서 텐서를 만드는 함수는 `from_…` 형태입니다.", "float32로 바꾸는 메서드입니다."],
          blanks=["from_numpy", "float()"]),
        X("d123_code_1", "가장 큰 행",
          "2차원 목록을 NumPy 배열로 받았다고 생각하고 텐서로 바꿔, 행마다의 합이 가장 큰 행의 번호와 그 합을 `[번호, 합]`으로 반환하세요.",
          ["tensor", "numpy_array"], 2,
          '''
          import numpy as np
          import torch


          def best_row(rows):
              t = torch.from_numpy(np.array(rows, dtype=float))
              sums = t.sum(dim=1)
              idx = sums.argmax().item()
              return [idx, sums[idx].item()]
          ''', "best_row", [[[[1, 2], [5, 1], [0, 0]]], [[[-1, -2, -3], [-1, 0, 0]]]],
          ["행마다의 합은 `sum(dim=1)`입니다.", "`argmax().item()`으로 위치를 파이썬 정수로 꺼내세요."]),
    ])

# ====================================================================== Day 124
day124 = D(
    124, "자동 미분(autograd)", W, ["autograd", "gradient_descent"],
    ["requires_grad와 backward로 기울기를 자동으로 계산할 수 있다.", "grad가 누적된다는 점을 이해한다."],
    "Day 83에서 경사하강법을 구현할 때 기울기 공식을 손으로 유도했습니다. PyTorch는 이 미분을 **자동으로** 해 줍니다.",
    [("경사하강법에서 가중치를 갱신하는 방향은?", ["기울기 방향", "기울기의 반대 방향", "무작위", "항상 양수 방향"], 1)],
    "미분을 맡기기",
    "`requires_grad=True`인 텐서로 계산하면 PyTorch가 계산 과정을 기록합니다. 마지막 값(스칼라)에서 `backward()`를 부르면 "
    "각 텐서의 `.grad`에 기울기가 저장됩니다.\n\n예를 들어 y = x² + 2x에서 x = 3일 때 기울기는 2x + 2 = 8입니다.",
    '''
    import torch

    x = torch.tensor(3.0, requires_grad=True)
    y = x ** 2 + 2 * x
    y.backward()
    print(y.item(), x.grad.item())

    w = torch.tensor([1.0, 2.0], requires_grad=True)
    loss = (w * w).sum()
    loss.backward()
    print(w.grad)
    loss = (w * w).sum()
    loss.backward()
    print(w.grad)
    ''',
    "같은 텐서로 `backward()`를 다시 부르면 기울기가 **더해집니다**(위의 마지막 출력). 그래서 학습 루프에서는 매번 기울기를 0으로 지워야 합니다.",
    "도함수 값을 구하세요.", "평균 제곱 오차의 기울기를 구하세요.",
    ["`requires_grad=True`로 기록 시작.", "스칼라 결과에서 `backward()`.", "기울기는 `.grad`에 저장.",
     "기울기는 누적되므로 매번 지워야 한다."],
    [("`backward()` 후 기울기가 저장되는 속성은?", ["`.grad`", "`.data`", "`.backward`", "`.value`"], 0),
     ("`backward()`를 두 번 부르면 기울기는?", ["덮어쓴다", "더해진다", "0이 된다", "오류"], 1)],
    [
        X("d124_fill_1", "도함수 값", "f(x) = x³ - 2x의 x = x0에서의 기울기를 autograd로 구해 반환하세요.", ["autograd"], 1,
          '''
          import torch


          def derivative(x0):
              x = torch.tensor(float(x0), requires_grad=True)
              y = x ** 3 - 2 * x
              y.backward()
              return x.grad.item()
          ''', "derivative", [[2], [0], [-1.5]],
          ["기울기 기록을 켜는 옵션 이름과 값입니다.", "결과에서 기울기 계산을 시작하는 메서드입니다."],
          blanks=["requires_grad=True", "backward"]),
        X("d124_code_1", "MSE의 기울기",
          "가중치 `w0`, 편향 `b0`에서 시작해 평균 제곱 오차 `((w*x + b - y)**2).mean()`의 `[w 기울기, b 기울기]`를 반환하세요(소수 넷째 자리).",
          ["autograd"], 2,
          '''
          import torch


          def mse_grad(w0, b0, xs, ys):
              w = torch.tensor(float(w0), requires_grad=True)
              b = torch.tensor(float(b0), requires_grad=True)
              x, y = torch.tensor(xs, dtype=torch.float32), torch.tensor(ys, dtype=torch.float32)
              loss = ((w * x + b - y) ** 2).mean()
              loss.backward()
              return [round(w.grad.item(), 4), round(b.grad.item(), 4)]
          ''', "mse_grad", [[0, 0, [1, 2, 3], [2, 4, 6]], [1, 1, [0, 1], [1, 3]], [2, -1, [1, 2], [0, 0]]],
          ["w와 b를 모두 `requires_grad=True` 텐서로 만드세요.", "손실에서 `backward()`를 부른 뒤 두 텐서의 `.grad`를 읽습니다."]),
    ])

# ====================================================================== Day 125
day125 = D(
    125, "autograd로 경사하강법", W, ["autograd", "gradient_descent"],
    ["autograd로 구한 기울기로 가중치를 갱신할 수 있다.", "torch.no_grad와 grad.zero_()의 역할을 설명할 수 있다."],
    "어제는 autograd로 기울기를 구했습니다. 오늘은 그 기울기로 직접 학습해 봅니다.",
    [("기울기가 누적되지 않게 하려면?", ["매번 `.grad`를 지운다", "backward를 두 번 부른다", "requires_grad를 끈다", "아무것도 안 해도 된다"], 0)],
    "직접 학습시키기",
    "학습 한 번(스텝)은 네 단계입니다.\n\n1. 예측과 손실 계산\n2. `loss.backward()`로 기울기 계산\n"
    "3. `with torch.no_grad():` 안에서 `w -= lr * w.grad` (갱신 자체는 기록하면 안 되므로)\n4. `w.grad.zero_()`로 기울기 지우기",
    '''
    import torch

    x = torch.tensor([1.0, 2.0, 3.0, 4.0])
    y = 2 * x + 1
    w = torch.tensor(0.0, requires_grad=True)
    b = torch.tensor(0.0, requires_grad=True)
    for epoch in range(500):
        loss = ((w * x + b - y) ** 2).mean()
        loss.backward()
        with torch.no_grad():
            w -= 0.05 * w.grad
            b -= 0.05 * b.grad
        w.grad.zero_()
        b.grad.zero_()
    print(round(w.item(), 3), round(b.item(), 3), round(loss.item(), 6))
    ''',
    "다음 주에는 이 네 단계를 `optimizer.zero_grad()`, `loss.backward()`, `optimizer.step()`으로 줄여 씁니다. 원리는 똑같습니다.",
    "갱신 단계를 완성하세요.", "직선을 학습시키세요.",
    ["손실 → backward → 갱신 → 기울기 지우기.", "갱신은 `torch.no_grad()` 안에서.", "`grad.zero_()`로 누적 방지.",
     "학습률이 너무 크면 발산한다."],
    [("갱신을 `torch.no_grad()` 안에서 하는 이유는?", ["속도 때문", "갱신 연산이 기록되지 않게", "오류 메시지 때문", "학습률 때문"], 1),
     ("`zero_()`처럼 이름 끝에 `_`가 붙은 메서드는?", ["새 텐서 반환", "제자리에서 값을 바꿈", "기울기 계산", "복사"], 1)],
    [
        X("d125_fill_1", "최솟값 찾기",
          "f(w) = (w - 3)²을 `w0`에서 시작해 학습률 `lr`로 `steps`번 경사하강한 뒤의 w를 소수 넷째 자리로 반환하세요.", ["autograd", "gradient_descent"], 1,
          '''
          import torch


          def descend(w0, lr, steps):
              w = torch.tensor(float(w0), requires_grad=True)
              for _ in range(steps):
                  loss = (w - 3) ** 2
                  loss.backward()
                  with torch.no_grad():
                      w -= lr * w.grad
                  w.grad.zero_()
              return round(w.item(), 4)
          ''', "descend", [[0, 0.1, 50], [10, 0.25, 3], [-2, 0.01, 10]],
          ["기록하지 않는 구역을 여는 함수 이름입니다.", "기울기를 제자리에서 0으로 만드는 메서드입니다."],
          blanks=["no_grad", "zero_()"], tol=1e-3),
        X("d125_code_1", "직선 학습",
          "w = 0, b = 0에서 시작해 평균 제곱 오차로 `epochs`번 경사하강(학습률 `lr`)한 뒤 `[w, b]`를 소수 셋째 자리로 반환하세요.",
          ["autograd", "gradient_descent"], 2,
          '''
          import torch


          def fit_line(xs, ys, lr, epochs):
              x, y = torch.tensor(xs, dtype=torch.float32), torch.tensor(ys, dtype=torch.float32)
              w = torch.tensor(0.0, requires_grad=True)
              b = torch.tensor(0.0, requires_grad=True)
              for _ in range(epochs):
                  loss = ((w * x + b - y) ** 2).mean()
                  loss.backward()
                  with torch.no_grad():
                      w -= lr * w.grad
                      b -= lr * b.grad
                  w.grad.zero_()
                  b.grad.zero_()
              return [round(w.item(), 3), round(b.item(), 3)]
          ''', "fit_line", [[[1, 2, 3, 4], [3, 5, 7, 9], 0.05, 1000], [[0, 1, 2], [1, 0, -1], 0.1, 300], [[1, 2], [1, 1], 0.1, 5]],
          ["개념 설명의 네 단계를 그대로 반복하세요.", "w와 b 모두 갱신하고 둘 다 기울기를 지워야 합니다."], tol=2e-3),
    ])

# ====================================================================== Day 126 (review)
day126 = D(
    126, "18주차 누적 복습", W, ["tensor", "tensor_ops", "tensor_shape", "autograd"],
    ["텐서 연산과 autograd를 함께 써서 모델을 학습시킬 수 있다."],
    "| 날 | 주제 | 핵심 |\n|---|---|---|\n| 120 | 텐서 | `torch.tensor`, `shape`, `dtype`, `item` |\n| 121 | 연산 | `@`, 브로드캐스팅, `dim` |\n"
    "| 122 | 모양 | `reshape`, `unsqueeze`, `cat`, `stack` |\n| 123 | NumPy | `from_numpy`, `.float()`, `argmax` |\n"
    "| 124 | autograd | `requires_grad`, `backward`, `.grad` |\n| 125 | 경사하강 | `no_grad`, `zero_` |",
    [("`(5, 3)` 텐서에 `unsqueeze(0)`을 하면?", ["(1, 5, 3)", "(5, 1, 3)", "(5, 3, 1)", "(15,)"], 0),
     ("기울기를 계산하는 메서드는?", ["`step()`", "`backward()`", "`grad()`", "`zero_()`"], 1)],
    "여러 매개변수 한 번에 학습하기",
    "매개변수가 많아지면 하나씩 만들지 않고 **텐서 하나**에 담습니다. 예를 들어 이차식 y = a·x² + b·x + c는 "
    "`theta = [a, b, c]`와 특성 행렬 `[x², x, 1]`의 행렬 곱으로 쓸 수 있습니다.",
    '''
    import torch

    x = torch.tensor([-1.0, 0.0, 1.0, 2.0])
    features = torch.stack([x ** 2, x, torch.ones_like(x)], dim=1)
    print(features)
    theta = torch.tensor([1.0, -2.0, 0.5])
    print(features @ theta)
    ''',
    "도전 문제는 autograd 기울기가 맞는지 **수치 미분**으로 확인합니다. 아주 작은 h에 대해 (f(x+h) - f(x-h)) / 2h가 기울기의 근삿값입니다.",
    "특성 행렬을 만드세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["텐서 = 모양·자료형·연산.", "모델 = 행렬 곱 + 편향.", "학습 = 손실 → backward → no_grad 갱신 → zero_.",
     "다음 주: `nn`과 `optim`으로 이 과정을 간단하게."],
    [("매개변수 여러 개를 한 텐서에 담는 장점은?", ["코드가 간결하고 행렬 곱으로 계산", "속도가 느려진다", "기울기가 필요 없다", "오류가 없다"], 0),
     ("`torch.ones_like(x)`의 결과는?", ["x와 같은 모양의 1", "x의 복사본", "스칼라 1", "x의 길이"], 0)],
    [
        X("d126_fill_1", "다항 특성",
          "값 목록 x로 열이 `[x², x, 1]`인 특성 행렬을 만들어 반환하세요.", ["tensor_shape"], 1,
          '''
          import torch


          def poly_features(xs):
              x = torch.tensor(xs, dtype=torch.float32)
              return torch.stack([x ** 2, x, torch.ones_like(x)], dim=1)
          ''', "poly_features", [[[1, 2]], [[-1, 0, 3]]],
          ["여러 텐서를 새 차원으로 쌓는 함수입니다.", "열 방향으로 쌓으려면 dim을 1로 줍니다."], blanks=["stack", "dim=1"]),
        X("d126_code_1", "이차식 학습",
          "`theta = torch.zeros(3, requires_grad=True)`에서 시작해 특성 `[x², x, 1]`로 평균 제곱 오차를 `epochs`번 경사하강(학습률 `lr`)하세요. "
          "학습된 `theta`를 소수 셋째 자리 리스트로 반환합니다.",
          ["autograd", "tensor_ops", "gradient_descent"], 3,
          '''
          import torch


          def fit_quadratic(xs, ys, lr, epochs):
              x, y = torch.tensor(xs, dtype=torch.float32), torch.tensor(ys, dtype=torch.float32)
              features = torch.stack([x ** 2, x, torch.ones_like(x)], dim=1)
              theta = torch.zeros(3, requires_grad=True)
              for _ in range(epochs):
                  loss = ((features @ theta - y) ** 2).mean()
                  loss.backward()
                  with torch.no_grad():
                      theta -= lr * theta.grad
                  theta.grad.zero_()
              return [round(v, 3) for v in theta.tolist()]
          ''', "fit_quadratic", [[[-2, -1, 0, 1, 2], [9, 3, 1, 3, 9], 0.02, 2000], [[0, 1, 2, 3], [1, 2, 5, 10], 0.01, 3000]],
          ["특성 행렬과 `theta`의 행렬 곱이 예측입니다.", "갱신 뒤 `theta.grad.zero_()`를 잊지 마세요."], tol=2e-3),
        X("d126_code_2", "기울기 검산(도전)",
          "f(x) = `(torch.sin(x) * x).sum()`의 기울기를 autograd로 구하고, h = 1e-3인 중앙 차분 `(f(x+h) - f(x-h)) / (2h)`(원소마다)과 비교하세요. "
          "`[autograd 기울기(소수 넷째 자리 리스트), 최대 차이가 1e-3보다 작은지]`를 반환합니다. 계산은 `float64`로 하세요.",
          ["autograd"], 3,
          '''
          import torch


          def f(x):
              return (torch.sin(x) * x).sum()


          def grad_check(values):
              x = torch.tensor(values, dtype=torch.float64, requires_grad=True)
              f(x).backward()
              h = 1e-3
              numeric = []
              with torch.no_grad():
                  for i in range(len(values)):
                      step = torch.zeros_like(x)
                      step[i] = h
                      numeric.append(((f(x + step) - f(x - step)) / (2 * h)).item())
              diff = (x.grad - torch.tensor(numeric, dtype=torch.float64)).abs().max().item()
              return [[round(v, 4) for v in x.grad.tolist()], diff < 1e-3]
          ''', "grad_check", [[[0.5, 1.0, 2.0]], [[-1.0, 3.0]]],
          ["원소 i만 h만큼 움직인 텐서를 만들어 앞뒤로 f를 계산합니다.", "수치 미분은 기록이 필요 없으니 `torch.no_grad()` 안에서 하세요."],
          required=False),
    ], review_title="18주차 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day120, day121, day122, day123, day124, day125, day126])
