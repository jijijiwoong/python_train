"""Week 19 (Day 127-133): 신경망 기초와 학습 루프."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, c, write_lessons  # noqa: E402

W = 19
CLS = {"required_syntax": ["class"]}

# ====================================================================== Day 127
day127 = D(
    127, "nn.Linear와 순전파", W, ["nn_linear", "tensor_ops"],
    ["nn.Linear의 가중치·편향 모양을 설명할 수 있다.", "층에 입력을 넣어 순전파 결과를 구할 수 있다."],
    "지난주에는 `w`, `b`를 직접 만들어 `x @ w + b`를 계산했습니다. `torch.nn`에는 이것을 묶어 둔 **층**(layer)이 있습니다.",
    [("신경망 한 층의 계산은?", ["`X @ W + b`", "`X + W`", "`X * b`", "`argmax(X)`"], 0)],
    "선형 층",
    "`nn.Linear(입력 수, 출력 수)`는 가중치 `weight`(모양: 출력 × 입력)와 편향 `bias`(모양: 출력)를 무작위로 만들어 가지고 있습니다. "
    "층을 함수처럼 부르면 `x @ weight.T + bias`를 계산하는데, 이것을 **순전파**(forward)라고 합니다.\n\n"
    "무작위 초깃값을 매번 같게 하려면 `torch.manual_seed(정수)`를 먼저 부릅니다.",
    '''
    import torch
    from torch import nn

    torch.manual_seed(0)
    layer = nn.Linear(3, 2)
    print(layer.weight.shape, layer.bias.shape)
    x = torch.ones(4, 3)
    print(layer(x).shape)
    print(sum(p.numel() for p in layer.parameters()))
    ''',
    "`parameters()`는 학습할 텐서(가중치·편향)를 차례로 돌려줍니다. `numel()`은 원소 수입니다. 3×2 가중치 6개 + 편향 2개 = 8개.",
    "층들의 매개변수 수를 세세요.", "층의 계산을 직접 확인하세요.",
    ["`nn.Linear(입력, 출력)`: weight (출력, 입력), bias (출력).", "층(x) = `x @ weight.T + bias`.",
     "`torch.manual_seed`로 초깃값 고정.", "`parameters()`와 `numel()`로 매개변수 수 세기."],
    [("`nn.Linear(10, 5)`의 weight 모양은?", ["(10, 5)", "(5, 10)", "(5,)", "(50,)"], 1),
     ("`nn.Linear(10, 5)`의 매개변수 수는?", ["50", "55", "60", "15"], 1)],
    [
        X("d127_fill_1", "매개변수 세기",
          "`sizes`가 `[4, 8, 3]`이면 `nn.Linear(4, 8)`, `nn.Linear(8, 3)`처럼 이웃한 수로 층을 만들고 전체 매개변수 수를 반환하세요.", ["nn_linear"], 1,
          '''
          from torch import nn


          def param_count(sizes):
              layers = [nn.Linear(a, b) for a, b in zip(sizes, sizes[1:])]
              return sum(p.numel() for layer in layers for p in layer.parameters())
          ''', "param_count", [[[4, 8, 3]], [[2, 1]], [[10, 20, 20, 5]]],
          ["선형 층 클래스 이름입니다.", "텐서의 원소 수를 돌려주는 메서드입니다."], blanks=["Linear", "numel"], tol=None),
        X("d127_code_1", "순전파 확인",
          "`torch.manual_seed(seed)` 후 `nn.Linear(2, 1)`을 만들고 입력 `rows`에 대해 ① 층 호출 결과와 ② `x @ weight.T + bias`를 직접 계산하세요. "
          "`[층 결과를 펼친 리스트(소수 넷째 자리), 두 결과가 같은지(torch.allclose)]`를 반환합니다.",
          ["nn_linear"], 2,
          '''
          import torch
          from torch import nn


          def check_forward(seed, rows):
              torch.manual_seed(seed)
              layer = nn.Linear(2, 1)
              x = torch.tensor(rows, dtype=torch.float32)
              out = layer(x)
              manual = x @ layer.weight.T + layer.bias
              return [[round(v, 4) for v in out.flatten().tolist()], torch.allclose(out, manual)]
          ''', "check_forward", [[0, [[1, 2], [3, 4]]], [7, [[0, 0], [1, -1], [2, 5]]]],
          ["층을 함수처럼 부르면 순전파 결과가 나옵니다.", "가중치는 (출력, 입력) 모양이라 `.T`로 뒤집어 곱합니다."]),
    ], review_title="지난주 돌아보기")

# ====================================================================== Day 128
day128 = D(
    128, "활성화 함수", W, ["activation", "nn_linear"],
    ["ReLU, 시그모이드, tanh의 모양과 용도를 설명할 수 있다.", "nn.Sequential로 층과 활성화 함수를 쌓을 수 있다."],
    "어제는 선형 층 하나를 썼습니다. 그렇다면 선형 층을 여러 개 쌓기만 하면 더 강력해질까요?",
    [("`nn.Linear(3, 2)`에 (4, 3) 입력을 넣으면 출력 모양은?", ["(4, 2)", "(2, 4)", "(3, 2)", "(4, 3)"], 0)],
    "비선형성 더하기",
    "선형 층을 몇 개 쌓아도 결과는 결국 선형 층 하나와 같습니다. 그래서 층 사이에 **활성화 함수**를 넣어 곡선을 표현할 수 있게 합니다.\n\n"
    "- **ReLU**: `max(0, x)`, 은닉층의 기본값\n- **시그모이드**: 0~1, 이진 분류 확률\n- **tanh**: -1~1\n\n"
    "`nn.Sequential(층, 활성화, 층, ...)`은 순서대로 통과시키는 모델을 만듭니다.",
    '''
    import torch
    from torch import nn

    x = torch.tensor([-2.0, 0.0, 3.0])
    print(torch.relu(x))
    print(torch.sigmoid(x).round(decimals=3))
    print(torch.tanh(x).round(decimals=3))

    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))
    print(model)
    print(model(torch.ones(3, 2)).shape)
    ''',
    "함수형 `torch.relu(x)`와 층 형태 `nn.ReLU()`는 같은 계산입니다. Sequential 안에는 층 형태를 넣습니다.",
    "활성화 함수를 적용하세요.", "작은 다층 신경망을 통과시키세요.",
    ["선형 층만 쌓으면 여전히 선형.", "ReLU = max(0, x), 은닉층 기본.", "시그모이드 0~1, tanh -1~1.", "`nn.Sequential`로 차례대로 쌓기."],
    [("ReLU(-3)의 값은?", ["-3", "0", "3", "0.5"], 1), ("시그모이드 출력 범위는?", ["-1~1", "0~1", "0~∞", "-∞~∞"], 1)],
    [
        X("d128_fill_1", "활성화 적용",
          "값 목록에 ReLU와 시그모이드를 적용해 `[ReLU 결과, 시그모이드 결과(소수 넷째 자리)]`를 반환하세요.", ["activation"], 1,
          '''
          import torch


          def activate(values):
              x = torch.tensor(values, dtype=torch.float32)
              return [torch.relu(x).tolist(), torch.sigmoid(x).round(decimals=4).tolist()]
          ''', "activate", [[[-1, 0, 2]], [[5, -5]]],
          ["음수를 0으로 만드는 함수입니다.", "0~1로 눌러 주는 S자 함수입니다."], blanks=["relu", "sigmoid"]),
        X("d128_code_1", "다층 신경망",
          "`torch.manual_seed(seed)` 후 `nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))`을 만들어 입력 `rows`의 출력을 펼친 리스트(소수 넷째 자리)로 반환하세요. "
          "기울기가 필요 없으니 `torch.no_grad()` 안에서 계산합니다.",
          ["activation", "nn_linear"], 2,
          '''
          import torch
          from torch import nn


          def mlp_output(seed, rows):
              torch.manual_seed(seed)
              model = nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))
              with torch.no_grad():
                  out = model(torch.tensor(rows, dtype=torch.float32))
              return [round(v, 4) for v in out.flatten().tolist()]
          ''', "mlp_output", [[0, [[1, 2], [0, 0]]], [3, [[-1, 1], [2, 2], [0.5, 0]]]],
          ["층을 만드는 순서가 무작위 초깃값을 결정하니 문제와 같은 순서로 만드세요.", "출력은 (n, 1) 모양이라 `flatten()`으로 펼칩니다."]),
    ])

# ====================================================================== Day 129
day129 = D(
    129, "손실 함수", W, ["loss_fn", "multiclass"],
    ["회귀에는 MSELoss, 분류에는 CrossEntropyLoss를 쓸 수 있다.", "CrossEntropyLoss가 로짓과 정수 레이블을 받는다는 것을 안다."],
    "어제는 활성화 함수와 Sequential로 모델을 만들었습니다. 이제 모델이 얼마나 틀렸는지 재는 **손실 함수**가 필요합니다.",
    [("은닉층에 가장 흔히 쓰는 활성화 함수는?", ["시그모이드", "ReLU", "softmax", "없음"], 1)],
    "틀린 정도 재기",
    "- `nn.MSELoss()`: 회귀, 평균 제곱 오차\n- `nn.CrossEntropyLoss()`: 다중 분류. 입력은 softmax 전의 점수인 **로짓**(logit) `(n, 클래스 수)`, "
    "정답은 클래스 번호 `(n,)`이며 자료형은 `torch.long`\n- `nn.BCEWithLogitsLoss()`: 이진 분류(로짓 하나, 정답 0/1 실수)\n\n"
    "CrossEntropyLoss는 내부에서 softmax와 로그를 함께 계산하므로 모델 끝에 softmax를 넣지 않습니다.",
    '''
    import torch
    from torch import nn

    pred, target = torch.tensor([2.5, 0.0]), torch.tensor([3.0, -1.0])
    print(nn.MSELoss()(pred, target))
    logits = torch.tensor([[2.0, 0.5, -1.0], [0.1, 0.2, 3.0]])
    labels = torch.tensor([0, 2])
    print(nn.CrossEntropyLoss()(logits, labels).round(decimals=4))
    print(torch.softmax(logits, dim=1).round(decimals=3))
    ''',
    "정답 클래스의 로짓이 클수록 CrossEntropy 손실이 작아집니다. 손실 = -log(정답 클래스의 softmax 확률)의 평균입니다.",
    "교차 엔트로피 손실을 구하세요.", "교차 엔트로피를 직접 계산하세요.",
    ["회귀 → MSELoss.", "다중 분류 → CrossEntropyLoss(로짓, long 레이블).", "모델 끝에 softmax를 넣지 않는다.",
     "손실 = -log(정답 확률)의 평균."],
    [("CrossEntropyLoss의 정답 레이블 자료형은?", ["float32", "long(int64)", "bool", "문자열"], 1),
     ("모델이 정답 클래스를 확률 1로 맞히면 교차 엔트로피는?", ["0", "1", "무한대", "-1"], 0)],
    [
        X("d129_fill_1", "분류 손실", "로짓과 정답 번호로 교차 엔트로피 손실(소수 넷째 자리)을 반환하세요.", ["loss_fn"], 1,
          '''
          import torch
          from torch import nn


          def ce_loss(logits, labels):
              x = torch.tensor(logits, dtype=torch.float32)
              y = torch.tensor(labels, dtype=torch.long)
              return round(nn.CrossEntropyLoss()(x, y).item(), 4)
          ''', "ce_loss", [[[[2, 0.5, -1], [0.1, 0.2, 3]], [0, 2]], [[[0, 0]], [1]], [[[5, 1], [1, 5]], [1, 0]]],
          ["다중 분류 손실 클래스 이름입니다.", "정답 레이블은 정수(64비트) 자료형이어야 합니다."], blanks=["CrossEntropyLoss", "long"]),
        X("d129_code_1", "직접 계산하기",
          "`torch.log_softmax(x, dim=1)`로 각 행의 정답 클래스 로그 확률을 꺼내 평균에 -1을 곱한 값과, `nn.CrossEntropyLoss`의 결과를 `[직접 계산, 내장 함수]`로 반환하세요(소수 넷째 자리).",
          ["loss_fn"], 2,
          '''
          import torch
          from torch import nn


          def my_ce(logits, labels):
              x = torch.tensor(logits, dtype=torch.float32)
              y = torch.tensor(labels, dtype=torch.long)
              log_prob = torch.log_softmax(x, dim=1)
              manual = -log_prob[torch.arange(len(labels)), y].mean()
              builtin = nn.CrossEntropyLoss()(x, y)
              return [round(manual.item(), 4), round(builtin.item(), 4)]
          ''', "my_ce", [[[[2, 0.5, -1], [0.1, 0.2, 3]], [0, 2]], [[[1, 2, 3, 4]], [0]], [[[0, 1], [3, -1], [2, 2]], [1, 0, 1]]],
          ["행 번호 `torch.arange(n)`과 정답 `y`로 인덱싱하면 정답 위치의 값만 꺼낼 수 있습니다.", "평균을 구한 뒤 부호를 바꾸세요."]),
    ])

# ====================================================================== Day 130
day130 = D(
    130, "옵티마이저와 학습 루프", W, ["training_loop", "loss_fn", "nn_linear"],
    ["optimizer.zero_grad, loss.backward, optimizer.step의 순서를 쓸 수 있다.", "nn.Linear를 학습 루프로 학습시킬 수 있다."],
    "어제는 손실 함수를 배웠습니다. Day 125에서 손으로 썼던 갱신 과정을 이제 **옵티마이저**가 맡습니다.",
    [("회귀 문제에 쓰는 손실 함수는?", ["CrossEntropyLoss", "MSELoss", "BCEWithLogitsLoss", "softmax"], 1)],
    "학습 루프의 표준 형태",
    "`optim.SGD(model.parameters(), lr=0.1)`은 모델의 모든 매개변수를 경사하강법으로 갱신합니다. 학습 루프는 항상 같은 모양입니다.\n\n"
    "1. `pred = model(X)`, `loss = loss_fn(pred, y)`\n2. `optimizer.zero_grad()` (기울기 지우기)\n3. `loss.backward()`\n4. `optimizer.step()` (갱신)",
    '''
    import torch
    from torch import nn, optim

    torch.manual_seed(0)
    X = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
    y = 3 * X - 1
    model = nn.Linear(1, 1)
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.05)
    for epoch in range(1000):
        loss = loss_fn(model(X), y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(round(model.weight.item(), 3), round(model.bias.item(), 3))
    ''',
    "`zero_grad()`는 `backward()` 전이면 어디에 두어도 됩니다. 루프 맨 앞에 두는 사람도 많아요.",
    "학습 루프를 완성하세요.", "선형 모델을 학습시키세요.",
    ["옵티마이저 = 매개변수 갱신 담당.", "zero_grad → backward → step.", "`optim.SGD(model.parameters(), lr=...)`.",
     "같은 모양의 루프가 모든 신경망 학습에 쓰인다."],
    [("기울기로 매개변수를 실제로 바꾸는 호출은?", ["`loss.backward()`", "`optimizer.step()`", "`optimizer.zero_grad()`", "`model(X)`"], 1),
     ("옵티마이저를 만들 때 넘기는 것은?", ["손실 함수", "`model.parameters()`", "입력 데이터", "에폭 수"], 1)],
    [
        X("d130_fill_1", "루프 완성",
          "`torch.manual_seed(0)` 후 `nn.Linear(1, 1)`을 y = 2x 데이터로 `steps`번 학습(SGD, lr 0.1)하고 마지막 손실(소수 넷째 자리)을 반환하세요.", ["training_loop"], 1,
          '''
          import torch
          from torch import nn, optim


          def final_loss(steps):
              torch.manual_seed(0)
              X = torch.tensor([[0.0], [1.0], [2.0]])
              y = 2 * X
              model = nn.Linear(1, 1)
              optimizer = optim.SGD(model.parameters(), lr=0.1)
              for _ in range(steps):
                  loss = nn.MSELoss()(model(X), y)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return round(loss.item(), 4)
          ''', "final_loss", [[1], [20], [200]],
          ["기울기를 지우는 옵티마이저 메서드입니다.", "기울기로 매개변수를 갱신하는 메서드입니다."], blanks=["zero_grad", "step"], tol=1e-3),
        X("d130_code_1", "선형 모델 학습",
          "`torch.manual_seed(0)` 후 `nn.Linear(1, 1)`, `nn.MSELoss()`, `optim.SGD(lr=lr)`로 `epochs`번 학습하세요. 입력 `xs`는 1차원 목록이니 (n, 1) 모양으로 바꿉니다. "
          "`[가중치, 편향]`을 소수 셋째 자리로 반환하세요.",
          ["training_loop", "nn_linear"], 2,
          '''
          import torch
          from torch import nn, optim


          def train_linear(xs, ys, lr, epochs):
              torch.manual_seed(0)
              X = torch.tensor(xs, dtype=torch.float32).reshape(-1, 1)
              y = torch.tensor(ys, dtype=torch.float32).reshape(-1, 1)
              model = nn.Linear(1, 1)
              loss_fn = nn.MSELoss()
              optimizer = optim.SGD(model.parameters(), lr=lr)
              for _ in range(epochs):
                  loss = loss_fn(model(X), y)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return [round(model.weight.item(), 3), round(model.bias.item(), 3)]
          ''', "train_linear", [[[1, 2, 3, 4], [2, 5, 8, 11], 0.05, 1000], [[0, 1, 2], [1, 1.5, 2], 0.1, 500], [[1, 2], [0, 0], 0.1, 3]],
          ["`reshape(-1, 1)`로 입력과 정답을 열 하나짜리로 만드세요.", "개념 예제의 루프와 같은 순서로 작성합니다."], tol=2e-3),
    ])

# ====================================================================== Day 131
NET_STARTER = c('''
    import torch
    from torch import nn


    class Net(nn.Module):
        def __init__(self, n_in, n_hidden, n_out):
            super().__init__()
            # self.hidden, self.out 층을 만드세요
            pass

        def forward(self, x):
            # hidden → ReLU → out 순서로 계산하세요
            pass


    def net_output(seed, rows):
        torch.manual_seed(seed)
        net = Net(len(rows[0]), 4, 2)
        with torch.no_grad():
            out = net(torch.tensor(rows, dtype=torch.float32))
        return out.round(decimals=4)
''')
day131 = D(
    131, "nn.Module로 모델 만들기", W, ["nn_module", "class", "inheritance"],
    ["nn.Module을 상속해 __init__에 층을, forward에 계산을 정의할 수 있다.", "Sequential보다 자유로운 모델 구조를 만들 수 있다."],
    "어제는 학습 루프를 완성했습니다. 2단계에서 배운 **클래스와 상속**이 오늘 다시 등장합니다.",
    [("부모 클래스의 `__init__`을 부르는 코드는?", ["`super().__init__()`", "`self.__init__()`", "`parent()`", "`init()`"], 0)],
    "나만의 모델 클래스",
    "PyTorch 모델은 `nn.Module`을 상속한 클래스입니다.\n\n- `__init__`: `super().__init__()`를 먼저 부르고, 층을 `self.이름`으로 만들어 둡니다.\n"
    "- `forward(self, x)`: 입력이 층을 지나는 계산을 씁니다.\n\n`model(x)`처럼 부르면 PyTorch가 `forward`를 대신 호출합니다. "
    "`self`에 넣은 층의 매개변수는 자동으로 `model.parameters()`에 포함됩니다.",
    '''
    import torch
    from torch import nn

    class TwoLayer(nn.Module):
        def __init__(self):
            super().__init__()
            self.hidden = nn.Linear(3, 5)
            self.out = nn.Linear(5, 2)

        def forward(self, x):
            return self.out(torch.relu(self.hidden(x)))

    torch.manual_seed(0)
    model = TwoLayer()
    print(model(torch.ones(4, 3)).shape)
    print([name for name, p in model.named_parameters()])
    ''',
    "`forward`를 직접 부르지 말고 `model(x)`로 부르세요. 그래야 PyTorch가 필요한 처리를 함께 해 줍니다.",
    "모델 클래스를 완성하세요.", "은닉층이 있는 모델 클래스를 직접 작성하세요.",
    ["`class 모델(nn.Module)`.", "`__init__`: super 호출 후 층 만들기.", "`forward`: 계산 순서.", "`model(x)`로 호출 → forward 실행."],
    [("`model(x)`를 부르면 실행되는 메서드는?", ["`__init__`", "`forward`", "`backward`", "`step`"], 1),
     ("층을 `self`의 속성으로 두면 좋은 점은?", ["매개변수가 자동 등록된다", "속도가 빨라진다", "기울기가 필요 없다", "출력 모양이 고정된다"], 0)],
    [
        X("d131_fill_1", "모델 클래스",
          "입력 `n_in`개를 출력 1개로 바꾸는 모델 클래스를 완성하고, 만든 모델의 매개변수 수를 반환하세요.", ["nn_module"], 1,
          '''
          from torch import nn


          class Tiny(nn.Module):
              def __init__(self, n_in):
                  super().__init__()
                  self.layer = nn.Linear(n_in, 1)

              def forward(self, x):
                  return self.layer(x)


          def tiny_params(n_in):
              return sum(p.numel() for p in Tiny(n_in).parameters())
          ''', "tiny_params", [[3], [10]],
          ["부모 클래스의 초기화를 부르는 표현입니다.", "순전파를 정의하는 메서드 이름입니다."],
          blanks=["super().__init__()", "forward"], tol=None),
        X("d131_code_1", "은닉층 모델",
          "`Net` 클래스를 완성하세요. `__init__`에서 `self.hidden = nn.Linear(n_in, n_hidden)`, `self.out = nn.Linear(n_hidden, n_out)`을 **이 순서로** 만들고, "
          "`forward`는 hidden → ReLU → out을 계산합니다. `net_output`은 이미 작성되어 있습니다.",
          ["nn_module", "activation"], 2,
          '''
          import torch
          from torch import nn


          class Net(nn.Module):
              def __init__(self, n_in, n_hidden, n_out):
                  super().__init__()
                  self.hidden = nn.Linear(n_in, n_hidden)
                  self.out = nn.Linear(n_hidden, n_out)

              def forward(self, x):
                  return self.out(torch.relu(self.hidden(x)))


          def net_output(seed, rows):
              torch.manual_seed(seed)
              net = Net(len(rows[0]), 4, 2)
              with torch.no_grad():
                  out = net(torch.tensor(rows, dtype=torch.float32))
              return out.round(decimals=4)
          ''', "net_output", [[0, [[1, 2, 3]]], [5, [[0, 1], [1, 0], [2, 2]]]],
          ["`__init__` 첫 줄은 부모 초기화 호출입니다.", "forward는 은닉층 결과에 `torch.relu`를 적용한 뒤 출력층에 넣습니다."],
          starter=NET_STARTER, checks=CLS),
    ])

# ====================================================================== Day 132
MOONS = '''from sklearn.datasets import make_moons


          def moons(seed):
              X, y = make_moons(n_samples=200, noise=0.2, random_state=seed)
              return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)
'''
day132 = D(
    132, "분류 신경망 만들기", W, ["training_loop", "nn_module", "multiclass"],
    ["신경망으로 비선형 분류 문제를 학습시킬 수 있다.", "argmax로 예측 클래스와 정확도를 구할 수 있다."],
    "어제는 nn.Module로 모델 클래스를 만들었습니다. 오늘은 로지스틱 회귀로는 풀기 어려운 초승달 모양 데이터를 신경망으로 분류합니다.",
    [("`forward`를 정의한 모델을 실행하는 올바른 방법은?", ["`model.forward(x)`", "`model(x)`", "`forward(model)`", "`model.run(x)`"], 1)],
    "곡선 경계 학습하기",
    "분류 신경망의 출력은 클래스마다 점수(로짓) 하나씩입니다. 학습은 CrossEntropyLoss로, 예측은 `logits.argmax(dim=1)`로 합니다. "
    "정확도는 `(예측 == 정답).float().mean()`입니다.\n\n"
    "Adam은 다음 주에 자세히 배우지만, 기본 SGD보다 빨리 수렴해서 오늘 예제에 먼저 써 봅니다.",
    '''
    import torch
    from torch import nn, optim
    from sklearn.datasets import make_moons

    X, y = make_moons(n_samples=200, noise=0.2, random_state=0)
    X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 2))
    optimizer = optim.Adam(model.parameters(), lr=0.05)
    for epoch in range(200):
        loss = nn.CrossEntropyLoss()(model(X), y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    acc = (model(X).argmax(dim=1) == y).float().mean()
    print(round(loss.item(), 4), round(acc.item(), 3))
    ''',
    "로지스틱 회귀는 직선 경계만 만들지만, ReLU 은닉층이 있는 신경망은 휘어진 경계를 만들 수 있습니다.",
    "정확도를 계산하세요.", "초승달 데이터를 분류하세요.",
    ["분류 신경망 출력 = 클래스별 로짓.", "학습은 CrossEntropyLoss.", "예측 = `argmax(dim=1)`.", "정확도 = `(예측 == 정답).float().mean()`."],
    [("로짓 `[[0.2, 1.5], [3.0, -1.0]]`의 예측 클래스는?", ["[1, 0]", "[0, 1]", "[1, 1]", "[0, 0]"], 0),
     ("bool 텐서의 평균을 구하려면 먼저?", ["`.float()`로 변환", "`.long()`으로 변환", "그대로", "`.item()`"], 0)],
    [
        X("d132_fill_1", "정확도",
          "로짓과 정답 번호로 정확도(0~1)를 반환하세요.", ["multiclass"], 1,
          '''
          import torch


          def accuracy(logits, labels):
              pred = torch.tensor(logits).argmax(dim=1)
              return (pred == torch.tensor(labels)).float().mean().item()
          ''', "accuracy", [[[[0.2, 1.5], [3.0, -1.0]], [1, 1]], [[[1, 2, 3], [3, 2, 1], [0, 5, 0]], [2, 0, 1]]],
          ["가장 큰 값의 위치를 찾는 메서드입니다.", "bool을 평균 낼 수 있는 실수형으로 바꾸는 메서드입니다."], blanks=["argmax", "float()"]),
        X("d132_code_1", "초승달 분류",
          "주어진 `moons(seed)`로 데이터를 만든 뒤 앞 150개로 학습, 뒤 50개로 평가하세요. `torch.manual_seed(0)` 후 "
          "`nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 2))`, `optim.Adam(lr=0.05)`, CrossEntropyLoss로 `epochs`번 학습합니다. "
          "`[마지막 학습 손실, 테스트 정확도]`를 소수 넷째 자리로 반환하세요.",
          ["training_loop", "multiclass"], 3,
          '''
          import torch
          from torch import nn, optim
          ''' + MOONS + '''

          def train_moons(seed, epochs):
              X, y = moons(seed)
              X_train, y_train, X_test, y_test = X[:150], y[:150], X[150:], y[150:]
              torch.manual_seed(0)
              model = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 2))
              optimizer = optim.Adam(model.parameters(), lr=0.05)
              for _ in range(epochs):
                  loss = nn.CrossEntropyLoss()(model(X_train), y_train)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              with torch.no_grad():
                  acc = (model(X_test).argmax(dim=1) == y_test).float().mean()
              return [round(loss.item(), 4), round(acc.item(), 4)]
          ''', "train_moons", [[0, 200], [1, 300]],
          ["슬라이싱으로 학습 150개, 테스트 50개를 나누세요.", "평가는 `torch.no_grad()` 안에서 테스트 데이터의 argmax와 정답을 비교합니다."],
          tol=2e-3),
    ])

# ====================================================================== Day 133 (review)
MYLIN_STARTER = c('''
    import torch
    from torch import nn, optim


    class MyLinear(nn.Module):
        def __init__(self):
            super().__init__()
            # self.w, self.b를 nn.Parameter로 만드세요
            pass

        def forward(self, x):
            # w * x + b를 반환하세요
            pass


    def fit_my_linear(xs, ys, epochs):
        model = MyLinear()
        x, y = torch.tensor(xs, dtype=torch.float32), torch.tensor(ys, dtype=torch.float32)
        optimizer = optim.SGD(model.parameters(), lr=0.05)
        for _ in range(epochs):
            loss = ((model(x) - y) ** 2).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        return [round(model.w.item(), 3), round(model.b.item(), 3)]
''')
day133 = D(
    133, "19주차 누적 복습", W, ["nn_module", "training_loop", "loss_fn", "activation", "nn_linear"],
    ["모델 정의 → 손실 → 옵티마이저 → 학습 루프 → 평가의 전 과정을 작성할 수 있다."],
    "| 날 | 주제 | 핵심 |\n|---|---|---|\n| 127 | 선형 층 | `nn.Linear`, weight·bias 모양 |\n| 128 | 활성화 | ReLU, 시그모이드, `nn.Sequential` |\n"
    "| 129 | 손실 | MSELoss, CrossEntropyLoss(로짓, long) |\n| 130 | 학습 루프 | zero_grad → backward → step |\n"
    "| 131 | nn.Module | `__init__`에 층, `forward`에 계산 |\n| 132 | 분류 | argmax, 정확도 |",
    [("학습 루프의 올바른 순서는?", ["step → backward → zero_grad", "zero_grad → backward → step", "backward → zero_grad → step", "step → zero_grad → backward"], 1),
     ("선형 층 사이에 활성화 함수가 필요한 이유는?", ["속도", "비선형 표현", "메모리 절약", "기울기 제거"], 1)],
    "XOR: 신경망이 필요한 이유",
    "XOR은 두 입력이 다를 때만 1인 문제입니다. 네 점을 직선 하나로 나눌 수 없어서 로지스틱 회귀는 풀지 못하지만, 은닉층이 있는 신경망은 풀 수 있습니다.\n\n"
    "도전 문제에서는 `nn.Linear` 대신 `nn.Parameter`로 직접 매개변수를 만듭니다. `nn.Parameter(텐서)`로 감싸 `self`에 두면 `parameters()`에 자동 등록됩니다.",
    '''
    import torch
    from torch import nn

    class Scale(nn.Module):
        def __init__(self):
            super().__init__()
            self.k = nn.Parameter(torch.tensor(2.0))

        def forward(self, x):
            return self.k * x

    model = Scale()
    print([p.item() for p in model.parameters()])
    print(model(torch.tensor([1.0, 3.0])))
    ''',
    None,
    "Sequential 모델의 층 수를 세세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["신경망 = 선형 층 + 활성화의 반복.", "분류는 CrossEntropyLoss + argmax.", "학습 루프는 항상 같은 4단계.",
     "다음 주: 데이터를 미니배치로 나누어 학습."],
    [("`nn.Parameter`로 만든 값의 특징은?", ["학습 대상으로 자동 등록", "상수", "기울기가 없다", "GPU 전용"], 0),
     ("XOR을 로지스틱 회귀로 못 푸는 이유는?", ["데이터가 적어서", "직선으로 나눌 수 없어서", "레이블이 문자라서", "학습률 때문"], 1)],
    [
        X("d133_fill_1", "선형 층 세기",
          "주어진 Sequential 모델에서 `nn.Linear` 층의 개수를 반환하세요.", ["nn_linear"], 1,
          '''
          from torch import nn


          def count_linear(hidden):
              model = nn.Sequential(nn.Linear(2, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))
              return sum(isinstance(layer, nn.Linear) for layer in model)
          ''', "count_linear", [[4], [8]],
          ["객체가 어떤 클래스인지 확인하는 내장 함수입니다.", "Sequential은 반복문으로 층을 하나씩 꺼낼 수 있습니다."],
          blanks=["isinstance", "model)"], tol=None),
        X("d133_code_1", "XOR 풀기",
          "XOR 데이터 `X = [[0,0],[0,1],[1,0],[1,1]]`, `y = [0,1,1,0]`을 만들고 `torch.manual_seed(seed)` 후 "
          "`nn.Sequential(nn.Linear(2, 8), nn.Tanh(), nn.Linear(8, 2))`, `optim.Adam(lr=0.05)`, CrossEntropyLoss로 300번 학습하세요. "
          "`[예측 클래스 리스트, 마지막 손실이 0.05보다 작은지]`를 반환합니다.",
          ["training_loop", "activation", "multiclass"], 2,
          '''
          import torch
          from torch import nn, optim


          def solve_xor(seed):
              X = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32)
              y = torch.tensor([0, 1, 1, 0])
              torch.manual_seed(seed)
              model = nn.Sequential(nn.Linear(2, 8), nn.Tanh(), nn.Linear(8, 2))
              optimizer = optim.Adam(model.parameters(), lr=0.05)
              for _ in range(300):
                  loss = nn.CrossEntropyLoss()(model(X), y)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return [model(X).argmax(dim=1).tolist(), loss.item() < 0.05]
          ''', "solve_xor", [[0], [1], [2]],
          ["입력은 float32, 정답은 정수 텐서로 만드세요.", "학습 루프 뒤 `model(X).argmax(dim=1)`이 예측입니다."], tol=None),
        X("d133_code_2", "Parameter로 만든 층(도전)",
          "`MyLinear`를 완성하세요. `__init__`에서 `self.w = nn.Parameter(torch.tensor(0.0))`, `self.b = nn.Parameter(torch.tensor(0.0))`를 만들고 "
          "`forward`는 `self.w * x + self.b`를 반환합니다. 학습 함수는 이미 작성되어 있습니다.",
          ["nn_module"], 3,
          '''
          import torch
          from torch import nn, optim


          class MyLinear(nn.Module):
              def __init__(self):
                  super().__init__()
                  self.w = nn.Parameter(torch.tensor(0.0))
                  self.b = nn.Parameter(torch.tensor(0.0))

              def forward(self, x):
                  return self.w * x + self.b


          def fit_my_linear(xs, ys, epochs):
              model = MyLinear()
              x, y = torch.tensor(xs, dtype=torch.float32), torch.tensor(ys, dtype=torch.float32)
              optimizer = optim.SGD(model.parameters(), lr=0.05)
              for _ in range(epochs):
                  loss = ((model(x) - y) ** 2).mean()
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return [round(model.w.item(), 3), round(model.b.item(), 3)]
          ''', "fit_my_linear", [[[1, 2, 3, 4], [3, 5, 7, 9], 1000], [[0, 1, 2], [2, 1, 0], 800]],
          ["`nn.Parameter(torch.tensor(0.0))`처럼 감싸야 옵티마이저가 찾을 수 있습니다.", "forward는 한 줄이면 충분합니다."],
          starter=MYLIN_STARTER, checks=CLS, required=False, tol=2e-3),
    ], review_title="19주차 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day127, day128, day129, day130, day131, day132, day133])
