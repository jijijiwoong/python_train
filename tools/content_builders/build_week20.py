"""Week 20 (Day 134-140): Dataset, DataLoader, 최적화 기법."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, c, write_lessons  # noqa: E402

W = 20
CLS = {"required_syntax": ["class"]}

# ====================================================================== Day 134
day134 = D(
    134, "TensorDataset과 DataLoader", W, ["dataloader", "tensor"],
    ["TensorDataset으로 입력과 정답을 묶을 수 있다.", "DataLoader로 미니배치를 만들고 섞을 수 있다."],
    "지난주에는 데이터 전체를 한 번에 모델에 넣었습니다. 데이터가 수만 개라면 한 번에 넣기 어렵겠죠.",
    [("학습 루프의 네 단계 중 기울기를 지우는 호출은?", ["`optimizer.step()`", "`optimizer.zero_grad()`", "`loss.backward()`", "`model.eval()`"], 1)],
    "데이터를 조각내기",
    "- `TensorDataset(X, y)`: 입력과 정답을 짝지어 `ds[i]` → `(X[i], y[i])`\n"
    "- `DataLoader(ds, batch_size=32, shuffle=True)`: 반복할 때마다 **미니배치** `(xb, yb)`를 꺼내 줌\n\n"
    "`len(loader)`는 배치 개수입니다. 마지막 배치는 남은 개수만큼 작아질 수 있고, `drop_last=True`면 버립니다. "
    "섞는 순서를 고정하려면 `generator=torch.Generator().manual_seed(값)`을 넘깁니다.",
    '''
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    X = torch.arange(20, dtype=torch.float32).reshape(10, 2)
    y = torch.arange(10)
    ds = TensorDataset(X, y)
    print(len(ds), ds[3])
    loader = DataLoader(ds, batch_size=4)
    print(len(loader))
    for xb, yb in loader:
        print(xb.shape, yb.tolist())
    ''',
    "학습 데이터는 `shuffle=True`로 매 에폭 순서를 섞고, 평가 데이터는 섞을 필요가 없습니다.",
    "배치 정보를 구하세요.", "섞인 배치를 확인하세요.",
    ["`TensorDataset(X, y)`로 짝짓기.", "`DataLoader(ds, batch_size, shuffle)`로 미니배치.", "`len(loader)` = 배치 수.",
     "`generator`로 섞는 순서 고정, `drop_last`로 자투리 버리기."],
    [("샘플 10개를 batch_size 4로 나누면 배치 수는?", ["2", "3", "4", "10"], 1),
     ("학습용 DataLoader에 보통 주는 옵션은?", ["`shuffle=True`", "`shuffle=False`", "`drop_last=True`만", "없음"], 0)],
    [
        X("d134_fill_1", "배치 정보",
          "샘플 `n`개를 `batch_size`로 나눈 DataLoader의 `[배치 수, 배치마다의 크기 리스트]`를 반환하세요.", ["dataloader"], 1,
          '''
          import torch
          from torch.utils.data import DataLoader, TensorDataset


          def batch_info(n, batch_size):
              X = torch.arange(n * 2, dtype=torch.float32).reshape(n, 2)
              y = torch.arange(n)
              loader = DataLoader(TensorDataset(X, y), batch_size=batch_size)
              sizes = [len(yb) for xb, yb in loader]
              return [len(loader), sizes]
          ''', "batch_info", [[10, 4], [6, 3], [5, 10]],
          ["입력과 정답을 짝짓는 데이터셋을 만드세요.", "DataLoader에 len을 적용하면 배치 수입니다."],
          blanks=["TensorDataset(X, y)", "len(loader)"], tol=None),
        X("d134_code_1", "섞인 배치",
          "정답이 `0 ~ n-1`인 TensorDataset(입력은 `torch.zeros(n, 1)`)을 만들고, `torch.Generator().manual_seed(seed)`로 섞는 DataLoader(`shuffle=True`)의 첫 배치 정답 리스트와, "
          "`drop_last=True`일 때의 배치 수를 `[첫 배치 정답, 배치 수]`로 반환하세요.",
          ["dataloader"], 2,
          '''
          import torch
          from torch.utils.data import DataLoader, TensorDataset


          def shuffled(seed, n, batch_size):
              ds = TensorDataset(torch.zeros(n, 1), torch.arange(n))
              g = torch.Generator().manual_seed(seed)
              loader = DataLoader(ds, batch_size=batch_size, shuffle=True, generator=g)
              xb, yb = next(iter(loader))
              dropped = DataLoader(ds, batch_size=batch_size, drop_last=True)
              return [yb.tolist(), len(dropped)]
          ''', "shuffled", [[0, 10, 4], [1, 7, 3], [42, 5, 2]],
          ["`next(iter(loader))`로 첫 배치를 꺼낼 수 있습니다.", "배치 수 확인용 DataLoader는 `drop_last=True`로 따로 만드세요."], tol=None),
    ], review_title="지난주 돌아보기")

# ====================================================================== Day 135
DS_STARTER = c('''
    import torch
    from torch.utils.data import DataLoader, Dataset


    class RecordDataset(Dataset):
        def __init__(self, records):
            self.records = records

        def __len__(self):
            # 데이터 개수를 반환하세요
            pass

        def __getitem__(self, i):
            # (특성 텐서, 정답 텐서)를 반환하세요
            pass


    def first_batch(records, batch_size):
        loader = DataLoader(RecordDataset(records), batch_size=batch_size)
        xb, yb = next(iter(loader))
        return [list(xb.shape), yb.tolist()]
''')
day135 = D(
    135, "사용자 정의 Dataset", W, ["dataloader", "class", "dunder"],
    ["Dataset을 상속해 __len__과 __getitem__을 구현할 수 있다.", "원하는 형식의 데이터를 DataLoader로 읽을 수 있다."],
    "어제는 텐서를 TensorDataset으로 묶었습니다. 데이터가 딕셔너리 목록이나 파일이라면 어떻게 할까요?",
    [("`DataLoader`의 `drop_last=True`는?", ["마지막 자투리 배치를 버린다", "마지막 샘플을 버린다", "섞지 않는다", "배치를 하나만 만든다"], 0)],
    "내 데이터에 맞는 Dataset",
    "`torch.utils.data.Dataset`을 상속하고 두 메서드만 만들면 DataLoader가 사용할 수 있습니다.\n\n"
    "- `__len__(self)`: 전체 개수\n- `__getitem__(self, i)`: i번째 `(입력, 정답)`\n\n"
    "2단계에서 배운 매직 메서드 그대로입니다. 이미지 파일을 i번째에 열어 읽는 식으로, 메모리에 다 올리지 않고도 큰 데이터를 다룰 수 있습니다.",
    '''
    import torch
    from torch.utils.data import DataLoader, Dataset

    class SquareDataset(Dataset):
        def __init__(self, n):
            self.n = n

        def __len__(self):
            return self.n

        def __getitem__(self, i):
            x = torch.tensor([float(i)])
            return x, x ** 2

    ds = SquareDataset(5)
    print(len(ds), ds[3])
    for xb, yb in DataLoader(ds, batch_size=2):
        print(xb.flatten().tolist(), yb.flatten().tolist())
    ''',
    "DataLoader는 `__getitem__`이 돌려준 샘플들을 모아 배치 텐서로 쌓아 줍니다.",
    "Dataset의 두 메서드를 채우세요.", "딕셔너리 목록용 Dataset을 만드세요.",
    ["Dataset 상속 + `__len__` + `__getitem__`.", "`__getitem__`은 (입력, 정답) 한 쌍.", "DataLoader가 샘플을 배치로 쌓는다.",
     "파일 등 큰 데이터도 필요할 때 읽을 수 있다."],
    [("`len(ds)`가 호출하는 메서드는?", ["`__getitem__`", "`__len__`", "`__init__`", "`forward`"], 1),
     ("`ds[3]`이 호출하는 메서드는?", ["`__getitem__`", "`__len__`", "`__iter__`", "`__call__`"], 0)],
    [
        X("d135_fill_1", "두 메서드",
          "0부터 n-1까지의 수 i에 대해 `(i, i의 짝수 여부)`를 주는 Dataset을 완성하고 `[길이, 마지막 샘플]`을 반환하세요.", ["dataloader", "dunder"], 1,
          '''
          import torch
          from torch.utils.data import Dataset


          class EvenDataset(Dataset):
              def __init__(self, n):
                  self.n = n

              def __len__(self):
                  return self.n

              def __getitem__(self, i):
                  return torch.tensor(float(i)), torch.tensor(int(i % 2 == 0))


          def even_info(n):
              ds = EvenDataset(n)
              return [len(ds), [v.item() for v in ds[n - 1]]]
          ''', "even_info", [[5], [8]],
          ["`len()`이 부르는 매직 메서드 이름입니다.", "대괄호 인덱싱이 부르는 매직 메서드 이름입니다."],
          blanks=["__len__", "__getitem__"], tol=None),
        X("d135_code_1", "레코드 Dataset",
          "`records`는 `{\"x1\": 실수, \"x2\": 실수, \"label\": 정수}` 딕셔너리 목록입니다. `RecordDataset`의 `__len__`과 `__getitem__`을 완성하세요. "
          "`__getitem__`은 `(torch.tensor([x1, x2], dtype=torch.float32), torch.tensor(label))`을 반환합니다.",
          ["dataloader", "class"], 2,
          '''
          import torch
          from torch.utils.data import DataLoader, Dataset


          class RecordDataset(Dataset):
              def __init__(self, records):
                  self.records = records

              def __len__(self):
                  return len(self.records)

              def __getitem__(self, i):
                  r = self.records[i]
                  return torch.tensor([r["x1"], r["x2"]], dtype=torch.float32), torch.tensor(r["label"])


          def first_batch(records, batch_size):
              loader = DataLoader(RecordDataset(records), batch_size=batch_size)
              xb, yb = next(iter(loader))
              return [list(xb.shape), yb.tolist()]
          ''', "first_batch",
          [[[{"x1": 1.0, "x2": 2.0, "label": 0}, {"x1": 0.5, "x2": 1.5, "label": 1}, {"x1": 3.0, "x2": 1.0, "label": 1}], 2],
           [[{"x1": 0.0, "x2": 0.0, "label": 2}], 4]],
          ["`__len__`은 레코드 목록의 길이입니다.", "`self.records[i]`에서 값을 꺼내 두 텐서를 만드세요."],
          starter=DS_STARTER, checks=CLS, tol=None),
    ])

# ====================================================================== Day 136
DATA_SRC = '''from torch.utils.data import DataLoader, TensorDataset


          def make_data(seed, n=64):
              torch.manual_seed(seed)
              X = torch.randn(n, 2)
              y = (2 * X[:, 0] - X[:, 1] + 0.5).unsqueeze(1) + 0.1 * torch.randn(n, 1)
              return X, y
'''
day136 = D(
    136, "미니배치 학습", W, ["dataloader", "training_loop"],
    ["DataLoader로 미니배치 학습 루프를 작성할 수 있다.", "에폭과 스텝(배치)을 구분하고 에폭 평균 손실을 구할 수 있다."],
    "어제는 직접 만든 Dataset을 DataLoader로 읽었습니다. 이제 학습 루프에 넣어 봅시다.",
    [("Dataset 클래스에 반드시 필요한 두 메서드는?", ["`__init__`, `forward`", "`__len__`, `__getitem__`", "`fit`, `transform`", "`step`, `zero_grad`"], 1)],
    "에폭과 배치",
    "학습 루프가 두 겹이 됩니다. 바깥 루프는 **에폭**(데이터 전체를 한 번 보는 것), 안쪽 루프는 **배치**마다 한 번의 갱신(스텝)입니다.\n\n"
    "배치마다 손실이 다르므로 보통 에폭이 끝날 때 배치 손실에 배치 크기를 곱해 더한 뒤 전체 개수로 나눈 **에폭 평균 손실**을 기록합니다.",
    '''
    import torch
    from torch import nn, optim
    from torch.utils.data import DataLoader, TensorDataset

    torch.manual_seed(0)
    X = torch.randn(64, 2)
    y = (2 * X[:, 0] - X[:, 1]).unsqueeze(1)
    loader = DataLoader(TensorDataset(X, y), batch_size=16, shuffle=True)
    model = nn.Linear(2, 1)
    optimizer = optim.SGD(model.parameters(), lr=0.1)
    for epoch in range(3):
        total = 0.0
        for xb, yb in loader:
            loss = nn.MSELoss()(model(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += loss.item() * len(xb)
        print(epoch, round(total / len(X), 4))
    ''',
    "배치가 작을수록 한 에폭에 갱신을 여러 번 해서 빨리 배우지만, 손실은 더 들쭉날쭉합니다.",
    "배치 루프를 완성하세요.", "에폭마다 평균 손실을 기록하세요.",
    ["에폭 = 전체 한 바퀴, 스텝 = 배치 하나.", "안쪽 루프에서 배치마다 갱신.", "에폭 평균 손실 = Σ(손실×배치 크기) / 전체 수.",
     "배치 크기는 속도와 안정성의 균형."],
    [("샘플 64개, batch_size 16이면 한 에폭의 스텝 수는?", ["1", "4", "16", "64"], 1),
     ("에폭 평균 손실을 구할 때 배치 손실에 곱하는 것은?", ["학습률", "배치 크기", "에폭 번호", "1"], 1)],
    [
        X("d136_fill_1", "배치 루프",
          "주어진 데이터로 한 에폭 동안 배치마다 갱신하고, 수행한 스텝 수를 반환하세요.", ["dataloader", "training_loop"], 1,
          '''
          import torch
          from torch import nn, optim
          from torch.utils.data import DataLoader, TensorDataset


          def one_epoch(n, batch_size):
              torch.manual_seed(0)
              X, y = torch.randn(n, 2), torch.randn(n, 1)
              loader = DataLoader(TensorDataset(X, y), batch_size=batch_size)
              model = nn.Linear(2, 1)
              optimizer = optim.SGD(model.parameters(), lr=0.1)
              steps = 0
              for xb, yb in loader:
                  loss = nn.MSELoss()(model(xb), yb)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
                  steps += 1
              return steps
          ''', "one_epoch", [[64, 16], [10, 3], [5, 8]],
          ["DataLoader에서 꺼내는 값은 입력 배치와 정답 배치 두 개입니다.", "갱신 호출 뒤 스텝 수를 1 늘리세요."],
          blanks=["xb, yb in loader", "steps += 1"], tol=None),
        X("d136_code_1", "에폭 평균 손실",
          "주어진 `make_data(seed)`로 데이터를 만든 뒤 `torch.manual_seed(0)` 후 `nn.Linear(2, 1)`과 `optim.SGD(lr=0.1)`을 만드세요. "
          "DataLoader는 `batch_size`, `shuffle=True`, `generator=torch.Generator().manual_seed(0)`으로 만듭니다. "
          "MSELoss로 `epochs`번 학습하며 에폭 평균 손실을 소수 넷째 자리로 기록한 리스트를 반환하세요.",
          ["dataloader", "training_loop"], 3,
          '''
          import torch
          from torch import nn, optim
          ''' + DATA_SRC + '''

          def epoch_losses(seed, batch_size, epochs):
              X, y = make_data(seed)
              torch.manual_seed(0)
              model = nn.Linear(2, 1)
              optimizer = optim.SGD(model.parameters(), lr=0.1)
              g = torch.Generator().manual_seed(0)
              loader = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True, generator=g)
              history = []
              for _ in range(epochs):
                  total = 0.0
                  for xb, yb in loader:
                      loss = nn.MSELoss()(model(xb), yb)
                      optimizer.zero_grad()
                      loss.backward()
                      optimizer.step()
                      total += loss.item() * len(xb)
                  history.append(round(total / len(X), 4))
              return history
          ''', "epoch_losses", [[0, 16, 3], [1, 8, 4], [2, 64, 2]],
          ["바깥 루프는 에폭, 안쪽 루프는 DataLoader입니다.", "에폭이 끝날 때 합계를 `len(X)`로 나누어 기록합니다."], tol=2e-3),
    ])

# ====================================================================== Day 137
BOWL = '''
          def bowl(w):
              return (w[0] - 3) ** 2 + 10 * (w[1] + 1) ** 2
'''
day137 = D(
    137, "옵티마이저 비교", W, ["optimizer", "gradient_descent"],
    ["SGD, 모멘텀, Adam의 차이를 설명할 수 있다.", "같은 문제에서 옵티마이저별 수렴 속도를 비교할 수 있다."],
    "어제는 미니배치 학습 루프를 작성했습니다. 오늘은 갱신 규칙인 옵티마이저를 바꿔 봅니다.",
    [("한 에폭 동안 갱신이 일어나는 횟수는?", ["1번", "배치 수만큼", "샘플 수만큼", "에폭 수만큼"], 1)],
    "갱신 규칙의 차이",
    "- **SGD**: `w -= lr × 기울기`. 단순하지만 골짜기가 좁고 길면 지그재그로 느리게 움직입니다.\n"
    "- **모멘텀**: `optim.SGD(..., momentum=0.9)`. 이전 이동 방향을 관성처럼 더해 지그재그를 줄입니다.\n"
    "- **Adam**: 매개변수마다 기울기 크기에 맞춰 보폭을 자동 조절합니다. 가장 무난한 기본값(`lr=0.001` 근처)입니다.\n\n"
    "아래 예제는 한쪽이 가파른 그릇 모양 함수의 최솟값 (3, -1)을 각 옵티마이저로 찾아갑니다.",
    '''
    import torch
    from torch import optim

    def bowl(w):
        return (w[0] - 3) ** 2 + 10 * (w[1] + 1) ** 2

    makers = {"SGD": lambda p: optim.SGD(p, lr=0.01), "모멘텀": lambda p: optim.SGD(p, lr=0.01, momentum=0.9),
              "Adam": lambda p: optim.Adam(p, lr=0.1)}
    for name, make in makers.items():
        w = torch.zeros(2, requires_grad=True)
        opt = make([w])
        for _ in range(100):
            loss = bowl(w)
            opt.zero_grad()
            loss.backward()
            opt.step()
        print(name, [round(v, 3) for v in w.tolist()], round(bowl(w).item(), 5))
    ''',
    "옵티마이저마다 알맞은 학습률이 다릅니다. 비교할 때는 각자 몇 가지 학습률을 시험해 보는 것이 공정합니다.",
    "모멘텀과 Adam 옵티마이저를 만드세요.", "옵티마이저별 결과를 비교하세요.",
    ["SGD: 기본 경사하강.", "모멘텀: 관성으로 지그재그 감소.", "Adam: 매개변수별 보폭 자동 조절, 무난한 기본값.",
     "옵티마이저마다 좋은 학습률이 다르다."],
    [("이전 이동 방향을 누적해 쓰는 기법은?", ["드롭아웃", "모멘텀", "정규화", "스케줄러"], 1),
     ("매개변수마다 보폭을 자동으로 조절하는 옵티마이저는?", ["SGD", "Adam", "StepLR", "MSELoss"], 1)],
    [
        X("d137_fill_1", "옵티마이저 만들기",
          "이름이 `\"momentum\"`이면 모멘텀 0.9인 SGD, `\"adam\"`이면 Adam을 lr 0.1로 만들어 bowl 함수를 `steps`번 줄인 뒤 손실(소수 넷째 자리)을 반환하세요.",
          ["optimizer"], 1,
          '''
          import torch
          from torch import optim
          ''' + BOWL + '''

          def minimize(name, steps):
              w = torch.zeros(2, requires_grad=True)
              if name == "momentum":
                  opt = optim.SGD([w], lr=0.01, momentum=0.9)
              else:
                  opt = optim.Adam([w], lr=0.1)
              for _ in range(steps):
                  loss = bowl(w)
                  opt.zero_grad()
                  loss.backward()
                  opt.step()
              return round(bowl(w).item(), 4)
          ''', "minimize", [["momentum", 50], ["adam", 50], ["momentum", 5]],
          ["SGD에 관성 계수를 주는 키워드 인자와 값입니다.", "적응형 옵티마이저 클래스 이름입니다."],
          blanks=["momentum=0.9", "Adam"], tol=1e-3),
        X("d137_code_1", "옵티마이저 비교",
          "bowl 함수를 `w = torch.zeros(2, requires_grad=True)`에서 시작해 `steps`번 줄이세요. "
          "`\"sgd\"`: `SGD(lr=0.01)`, `\"momentum\"`: `SGD(lr=0.01, momentum=0.9)`, `\"adam\"`: `Adam(lr=0.1)` 각각의 최종 손실(소수 넷째 자리)을 딕셔너리로, "
          "가장 작은 손실의 이름을 `best`로 넣어 `{\"losses\": ..., \"best\": ...}`를 반환하세요.",
          ["optimizer"], 2,
          '''
          import torch
          from torch import optim
          ''' + BOWL + '''

          def compare(steps):
              makers = {
                  "sgd": lambda p: optim.SGD(p, lr=0.01),
                  "momentum": lambda p: optim.SGD(p, lr=0.01, momentum=0.9),
                  "adam": lambda p: optim.Adam(p, lr=0.1),
              }
              losses = {}
              for name, make in makers.items():
                  w = torch.zeros(2, requires_grad=True)
                  opt = make([w])
                  for _ in range(steps):
                      loss = bowl(w)
                      opt.zero_grad()
                      loss.backward()
                      opt.step()
                  losses[name] = round(bowl(w).item(), 4)
              return {"losses": losses, "best": min(losses, key=losses.get)}
          ''', "compare", [[100], [20], [50]],
          ["이름 → 옵티마이저를 만드는 함수 딕셔너리를 두면 반복문 하나로 처리할 수 있습니다.", "옵티마이저마다 `w`를 새로 만들어야 공정합니다."],
          tol=1e-3),
    ])

# ====================================================================== Day 138
day138 = D(
    138, "학습률과 스케줄러", W, ["lr_schedule", "optimizer"],
    ["학습률이 너무 크거나 작을 때의 문제를 설명할 수 있다.", "StepLR 등 스케줄러로 학습률을 줄여 갈 수 있다."],
    "어제는 옵티마이저를 비교했습니다. 어떤 옵티마이저든 가장 중요한 설정은 **학습률**입니다.",
    [("무난한 기본값으로 많이 쓰는 옵티마이저는?", ["SGD", "Adam", "모멘텀 없는 SGD", "없음"], 1)],
    "학습률 조절하기",
    "학습률이 너무 크면 손실이 튀거나 발산하고, 너무 작으면 학습이 끝나지 않습니다. 그래서 처음엔 크게, 나중엔 작게 하는 **스케줄러**를 씁니다.\n\n"
    "- `StepLR(opt, step_size=2, gamma=0.5)`: 2 에폭마다 학습률 × 0.5\n- `ExponentialLR(opt, gamma=0.9)`: 매 에폭 × 0.9\n\n"
    "에폭이 끝날 때 `scheduler.step()`을 부릅니다. 현재 학습률은 `optimizer.param_groups[0][\"lr\"]`에 있습니다.",
    '''
    import torch
    from torch import optim

    w = torch.zeros(1, requires_grad=True)
    opt = optim.SGD([w], lr=0.1)
    scheduler = optim.lr_scheduler.StepLR(opt, step_size=2, gamma=0.5)
    for epoch in range(6):
        print(epoch, opt.param_groups[0]["lr"])
        opt.step()
        scheduler.step()
    ''',
    "스케줄러의 `step()`은 옵티마이저의 `step()` 다음에, 보통 에폭마다 한 번 부릅니다.",
    "StepLR을 적용하세요.", "스케줄별 학습률 변화를 기록하세요.",
    ["학습률이 크면 발산, 작으면 느림.", "스케줄러로 점점 줄인다.", "StepLR: 일정 간격마다 gamma배, ExponentialLR: 매번 gamma배.",
     "에폭 끝에 `scheduler.step()`."],
    [("StepLR(step_size=3, gamma=0.1), 처음 lr 1.0이면 3 에폭 뒤 lr은?", ["1.0", "0.1", "0.3", "0.01"], 1),
     ("현재 학습률이 저장된 곳은?", ["`optimizer.lr`", "`optimizer.param_groups[0][\"lr\"]`", "`model.lr`", "`scheduler.gamma`"], 1)],
    [
        X("d138_fill_1", "StepLR",
          "lr로 SGD를 만들고 `StepLR(step_size=2, gamma=0.5)`를 붙여 `epochs`번 에폭을 진행한 뒤의 학습률을 반환하세요.", ["lr_schedule"], 1,
          '''
          import torch
          from torch import optim


          def lr_after(lr, epochs):
              w = torch.zeros(1, requires_grad=True)
              opt = optim.SGD([w], lr=lr)
              scheduler = optim.lr_scheduler.StepLR(opt, step_size=2, gamma=0.5)
              for _ in range(epochs):
                  opt.step()
                  scheduler.step()
              return opt.param_groups[0]["lr"]
          ''', "lr_after", [[0.1, 4], [1.0, 3], [0.5, 0]],
          ["일정 간격마다 줄이는 스케줄러 클래스 이름입니다.", "에폭마다 스케줄러를 한 칸 진행시키는 호출입니다."],
          blanks=["StepLR", "scheduler.step()"], tol=1e-9),
        X("d138_code_1", "학습률 기록",
          "`kind`가 `\"step\"`이면 `StepLR(step_size=2, gamma=0.5)`, `\"exp\"`면 `ExponentialLR(gamma=0.9)`를 씁니다. "
          "에폭마다 **시작할 때의** 학습률을 소수 여섯째 자리로 기록한 길이 `epochs`의 리스트를 반환하세요.",
          ["lr_schedule"], 2,
          '''
          import torch
          from torch import optim


          def lr_history(kind, lr, epochs):
              w = torch.zeros(1, requires_grad=True)
              opt = optim.SGD([w], lr=lr)
              if kind == "step":
                  scheduler = optim.lr_scheduler.StepLR(opt, step_size=2, gamma=0.5)
              else:
                  scheduler = optim.lr_scheduler.ExponentialLR(opt, gamma=0.9)
              history = []
              for _ in range(epochs):
                  history.append(round(opt.param_groups[0]["lr"], 6))
                  opt.step()
                  scheduler.step()
              return history
          ''', "lr_history", [["step", 0.1, 5], ["exp", 1.0, 4], ["exp", 0.5, 2]],
          ["기록은 `opt.step()`보다 먼저 합니다.", "두 스케줄러 모두 `optim.lr_scheduler` 안에 있습니다."], tol=1e-7),
    ])

# ====================================================================== Day 139
WD_SRC = '''
          def noisy_data(seed):
              torch.manual_seed(seed)
              X = torch.randn(12, 8)
              y = X[:, :1] + 0.5 * torch.randn(12, 1)
              return X, y
'''
day139 = D(
    139, "드롭아웃과 가중치 감쇠", W, ["dropout", "overfitting"],
    ["드롭아웃이 학습·평가 모드에서 다르게 동작함을 설명할 수 있다.", "weight_decay로 가중치를 작게 유지할 수 있다."],
    "어제는 학습률 스케줄러를 배웠습니다. Day 96에서 배운 **과적합**을 신경망에서는 어떻게 막을까요?",
    [("과적합의 특징은?", ["학습·테스트 모두 나쁨", "학습은 좋은데 테스트가 나쁨", "테스트만 좋음", "둘 다 좋음"], 1)],
    "신경망 규제",
    "- **드롭아웃** `nn.Dropout(p)`: 학습 중 뉴런을 확률 p로 무작위로 끄고, 남은 값은 `1/(1-p)`배 키웁니다. 특정 뉴런에 의존하지 않게 만듭니다.\n"
    "- **가중치 감쇠** `optim.SGD(..., weight_decay=0.01)`: 가중치가 커지지 않게 매번 조금씩 줄입니다(Ridge 규제와 같은 효과).\n\n"
    "드롭아웃은 평가할 때 꺼야 하므로 `model.train()`과 `model.eval()`로 모드를 바꿉니다.",
    '''
    import torch
    from torch import nn

    torch.manual_seed(0)
    drop = nn.Dropout(p=0.5)
    x = torch.ones(8)
    print(drop(x))
    drop.eval()
    print(drop(x))
    ''',
    "평가·예측 전에는 꼭 `model.eval()`, 다시 학습할 때는 `model.train()`을 부르세요. 다음 주 배치 정규화도 이 모드를 따릅니다.",
    "드롭아웃의 두 모드를 확인하세요.", "가중치 감쇠의 효과를 비교하세요.",
    ["드롭아웃: 학습 중 무작위로 끄고 남은 값 확대.", "평가 땐 `model.eval()`로 드롭아웃 끄기.", "weight_decay: 가중치를 작게(L2 규제).",
     "둘 다 과적합을 줄이는 방법."],
    [("p=0.5 드롭아웃에서 학습 중 살아남은 값은?", ["그대로", "2배", "절반", "0"], 1),
     ("평가 모드로 바꾸는 호출은?", ["`model.train()`", "`model.eval()`", "`model.test()`", "`torch.no_grad()`"], 1)],
    [
        X("d139_fill_1", "두 모드",
          "`torch.manual_seed(0)` 후 `nn.Dropout(p)`에 `torch.ones(20)`을 넣어 학습 모드에서 0이 된 개수와, 평가 모드에서의 합을 `[0의 개수, 평가 모드 합]`으로 반환하세요.",
          ["dropout"], 1,
          '''
          import torch
          from torch import nn


          def dropout_modes(p):
              torch.manual_seed(0)
              drop = nn.Dropout(p)
              x = torch.ones(20)
              zeros = int((drop(x) == 0).sum().item())
              drop.eval()
              return [zeros, drop(x).sum().item()]
          ''', "dropout_modes", [[0.5], [0.2], [0.0]],
          ["드롭아웃 층 클래스 이름입니다.", "평가 모드로 바꾸는 메서드입니다."], blanks=["Dropout", "eval()"], tol=None),
        X("d139_code_1", "가중치 감쇠 효과",
          "주어진 `noisy_data(seed)`로 데이터를 만드세요. `weight_decay`가 0일 때와 `wd`일 때 각각 `torch.manual_seed(0)` 후 `nn.Linear(8, 1)`, "
          "`optim.SGD(lr=0.05, weight_decay=값)`, MSELoss로 500번 학습합니다. 두 모델 가중치의 L2 노름(`model.weight.norm()`)을 "
          "`[감쇠 없음, 감쇠 있음, 감쇠 있음이 더 작은지]`로 반환하세요(노름은 소수 넷째 자리).",
          ["dropout", "regularization"], 3,
          '''
          import torch
          from torch import nn, optim
          ''' + WD_SRC + '''

          def train_norm(X, y, wd):
              torch.manual_seed(0)
              model = nn.Linear(8, 1)
              optimizer = optim.SGD(model.parameters(), lr=0.05, weight_decay=wd)
              for _ in range(500):
                  loss = nn.MSELoss()(model(X), y)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return round(model.weight.norm().item(), 4)


          def decay_effect(seed, wd):
              X, y = noisy_data(seed)
              plain, decayed = train_norm(X, y, 0.0), train_norm(X, y, wd)
              return [plain, decayed, decayed < plain]
          ''', "decay_effect", [[0, 0.1], [1, 0.5]],
          ["학습 과정을 `weight_decay`만 다른 함수 하나로 만들어 두 번 부르면 편합니다.", "노름은 `model.weight.norm().item()`입니다."],
          tol=2e-3),
    ])

# ====================================================================== Day 140 (review)
WINE_SRC = '''
          def wine_loaders(seed):
              X, y = load_wine(return_X_y=True)
              X_train, X_test, y_train, y_test = train_test_split(
                  X, y, test_size=0.3, random_state=seed, stratify=y)
              scaler = StandardScaler().fit(X_train)
              to_t = lambda a: torch.tensor(a, dtype=torch.float32)
              train = TensorDataset(to_t(scaler.transform(X_train)), torch.tensor(y_train))
              test = TensorDataset(to_t(scaler.transform(X_test)), torch.tensor(y_test))
              g = torch.Generator().manual_seed(0)
              return DataLoader(train, batch_size=16, shuffle=True, generator=g), DataLoader(test, batch_size=64)
'''
WINE_IMPORTS = '''
          import torch
          from sklearn.datasets import load_wine
          from sklearn.model_selection import train_test_split
          from sklearn.preprocessing import StandardScaler
          from torch import nn, optim
          from torch.utils.data import DataLoader, TensorDataset
'''
day140 = D(
    140, "20주차 누적 복습", W, ["dataloader", "optimizer", "lr_schedule", "dropout", "training_loop"],
    ["실제 데이터를 DataLoader로 읽어 드롭아웃이 있는 모델을 Adam으로 학습하고 평가할 수 있다."],
    "| 날 | 주제 | 핵심 |\n|---|---|---|\n| 134 | DataLoader | `TensorDataset`, `batch_size`, `shuffle` |\n| 135 | Dataset | `__len__`, `__getitem__` |\n"
    "| 136 | 미니배치 | 에폭·스텝, 에폭 평균 손실 |\n| 137 | 옵티마이저 | SGD, 모멘텀, Adam |\n| 138 | 스케줄러 | StepLR, ExponentialLR |\n"
    "| 139 | 규제 | 드롭아웃, `train()`/`eval()`, weight_decay |",
    [("평가 전에 반드시 부를 것은?", ["`model.train()`", "`model.eval()`", "`scheduler.step()`", "`optimizer.step()`"], 1),
     ("에폭 끝에 학습률을 줄이는 호출은?", ["`optimizer.zero_grad()`", "`scheduler.step()`", "`loss.backward()`", "`model.eval()`"], 1)],
    "전체 과정 정리",
    "지금까지 배운 것을 한 번에 쓰면 아래와 같습니다. **평가 함수**를 따로 두면 학습 중간에도 쉽게 성능을 확인할 수 있습니다.",
    '''
    import torch
    from torch import nn

    def evaluate(model, loader):
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for xb, yb in loader:
                correct += (model(xb).argmax(dim=1) == yb).sum().item()
                total += len(yb)
        model.train()
        return correct / total

    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Dropout(0.2), nn.Linear(8, 3))
    loader = [(torch.randn(5, 4), torch.tensor([0, 1, 2, 0, 1]))]
    print(round(evaluate(model, loader), 2), model.training)
    ''',
    "도전 문제의 **워밍업**은 처음 몇 에폭 동안 학습률을 0에서 목표값까지 천천히 올리는 기법입니다. `LambdaLR`에 에폭 → 배율 함수를 넘기면 됩니다.",
    "모드 전환을 확인하세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["데이터: Dataset → DataLoader(셔플).", "학습: 에폭 × 배치, zero_grad → backward → step.", "규제: 드롭아웃·weight_decay, 평가 땐 eval.",
     "다음 주: 이미지를 위한 합성곱 신경망."],
    [("`model.training` 속성이 False인 상태는?", ["학습 모드", "평가 모드", "기울기 없음", "오류"], 1),
     ("`LambdaLR`에 넘기는 함수의 반환값은?", ["새 손실", "기본 학습률에 곱할 배율", "에폭 수", "가중치"], 1)],
    [
        X("d140_fill_1", "모드 전환",
          "드롭아웃이 있는 Sequential 모델을 만들고 `[처음 training 값, eval 뒤 training 값, train 뒤 training 값]`을 반환하세요.", ["dropout"], 1,
          '''
          from torch import nn


          def modes(p):
              model = nn.Sequential(nn.Linear(2, 4), nn.Dropout(p), nn.Linear(4, 1))
              states = [model.training]
              model.eval()
              states.append(model.training)
              model.train()
              states.append(model.training)
              return states
          ''', "modes", [[0.5], [0.1]],
          ["평가 모드로 바꾸는 메서드입니다.", "학습 모드로 되돌리는 메서드입니다."], blanks=["eval()", "train()"], tol=None),
        X("d140_code_1", "와인 분류기",
          "주어진 `wine_loaders(seed)`로 학습·테스트 DataLoader를 만드세요. `torch.manual_seed(0)` 후 "
          "`nn.Sequential(nn.Linear(13, 32), nn.ReLU(), nn.Dropout(0.2), nn.Linear(32, 3))`, `optim.Adam(lr=0.01)`, CrossEntropyLoss로 `epochs` 에폭 학습하세요. "
          "그다음 `model.eval()` 상태에서 테스트 정확도를 구해 `[마지막 에폭 평균 손실, 테스트 정확도]`(소수 넷째 자리)를 반환합니다.",
          ["dataloader", "training_loop", "dropout"], 3,
          WINE_IMPORTS + WINE_SRC + '''

          def train_wine(seed, epochs):
              train_loader, test_loader = wine_loaders(seed)
              torch.manual_seed(0)
              model = nn.Sequential(nn.Linear(13, 32), nn.ReLU(), nn.Dropout(0.2), nn.Linear(32, 3))
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              loss_fn = nn.CrossEntropyLoss()
              for _ in range(epochs):
                  total, count = 0.0, 0
                  for xb, yb in train_loader:
                      loss = loss_fn(model(xb), yb)
                      optimizer.zero_grad()
                      loss.backward()
                      optimizer.step()
                      total += loss.item() * len(yb)
                      count += len(yb)
              model.eval()
              correct = 0
              with torch.no_grad():
                  for xb, yb in test_loader:
                      correct += (model(xb).argmax(dim=1) == yb).sum().item()
              return [round(total / count, 4), round(correct / len(test_loader.dataset), 4)]
          ''', "train_wine", [[0, 20], [1, 10]],
          ["에폭 평균 손실은 에폭마다 합계를 새로 시작해 구합니다.", "평가는 `model.eval()`과 `torch.no_grad()` 안에서, 맞힌 개수를 테스트 개수로 나눕니다."],
          tol=2e-3, tl=90),
        X("d140_code_2", "학습률 워밍업(도전)",
          "`optim.lr_scheduler.LambdaLR`로 처음 `warmup` 에폭 동안 배율을 `(에폭 + 1) / warmup`으로 키우고, 그 뒤로는 1을 유지하세요. "
          "기본 학습률 `base_lr`인 SGD에서 에폭마다 시작할 때의 학습률을 소수 여섯째 자리로 기록한 리스트를 반환합니다.",
          ["lr_schedule"], 3,
          '''
          import torch
          from torch import optim


          def warmup_lrs(base_lr, warmup, epochs):
              w = torch.zeros(1, requires_grad=True)
              opt = optim.SGD([w], lr=base_lr)
              scheduler = optim.lr_scheduler.LambdaLR(opt, lambda e: min(1.0, (e + 1) / warmup))
              history = []
              for _ in range(epochs):
                  history.append(round(opt.param_groups[0]["lr"], 6))
                  opt.step()
                  scheduler.step()
              return history
          ''', "warmup_lrs", [[0.1, 4, 6], [1.0, 2, 3], [0.5, 1, 2]],
          ["LambdaLR의 두 번째 인자는 에폭 번호를 받아 배율을 돌려주는 함수입니다.", "배율은 `min(1.0, (e + 1) / warmup)`처럼 1을 넘지 않게 하세요."],
          tol=1e-7, required=False),
    ], review_title="20주차 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day134, day135, day136, day137, day138, day139, day140])
