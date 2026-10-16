"""Week 24 (Day 162-168): 딥러닝 종합 프로젝트 (손글씨 숫자 분류 전 과정)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, write_lessons  # noqa: E402

W = 24

IMPORTS = '''
          import torch
          from sklearn.datasets import load_digits
          from sklearn.model_selection import train_test_split
          from torch import nn, optim
          from torch.utils.data import DataLoader, TensorDataset
'''
SPLIT_SRC = '''

          def split_data(seed):
              digits = load_digits()
              X_tmp, X_test, y_tmp, y_test = train_test_split(
                  digits.images, digits.target, test_size=0.2, random_state=seed, stratify=digits.target)
              X_train, X_val, y_train, y_val = train_test_split(
                  X_tmp, y_tmp, test_size=0.25, random_state=seed, stratify=y_tmp)
              to_x = lambda a: torch.tensor(a, dtype=torch.float32).unsqueeze(1) / 16
              pairs = [(X_train, y_train), (X_val, y_val), (X_test, y_test)]
              return [(to_x(a), torch.tensor(b)) for a, b in pairs]


          def make_loader(data, shuffle=False):
              g = torch.Generator().manual_seed(0)
              return DataLoader(TensorDataset(*data), batch_size=64, shuffle=shuffle, generator=g)
'''
CNN_SRC = '''

          class CNN(nn.Module):
              def __init__(self, c=8):
                  super().__init__()
                  self.features = nn.Sequential(
                      nn.Conv2d(1, c, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                      nn.Conv2d(c, 2 * c, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(),
                  )
                  self.fc = nn.Linear(2 * c * 4, 10)

              def forward(self, x):
                  return self.fc(self.features(x))
'''
TRAIN_SRC = '''

          def train_one_epoch(model, loader, optimizer):
              model.train()
              total = 0.0
              for xb, yb in loader:
                  loss = nn.CrossEntropyLoss()(model(xb), yb)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
                  total += loss.item() * len(yb)
              return total / len(loader.dataset)
'''
EVAL_SRC = '''

          def evaluate(model, loader):
              model.eval()
              correct = 0
              with torch.no_grad():
                  for xb, yb in loader:
                      correct += (model(xb).argmax(dim=1) == yb).sum().item()
              return correct / len(loader.dataset)
'''
FIT_SRC = '''

          def fit(model, train_loader, epochs, lr=0.01):
              optimizer = optim.Adam(model.parameters(), lr=lr)
              for _ in range(epochs):
                  train_one_epoch(model, train_loader, optimizer)
              return model
'''
ALL = IMPORTS + SPLIT_SRC + CNN_SRC + TRAIN_SRC + EVAL_SRC + FIT_SRC
PLAN_MD = ("| 날 | 단계 | 만들 것 |\n|---|---|---|\n| 162 | 데이터 준비 | 학습·검증·테스트 분할, DataLoader |\n| 163 | 학습 | `train_one_epoch` |\n"
           "| 164 | 평가 | 정확도, 혼동 행렬, 클래스별 재현율 |\n| 165 | 비교 | MLP 대 CNN |\n| 166 | 튜닝 | 검증 데이터로 설정 고르기 |\n"
           "| 167 | 추론 | 확률과 상위 k개 예측 |\n| 168 | 마무리 | 전체 파이프라인 |")

# ====================================================================== Day 162
day162 = D(
    162, "프로젝트: 데이터 준비", W, ["dl_project", "train_test", "dataloader"],
    ["데이터를 학습·검증·테스트로 나누고 각 용도를 설명할 수 있다.", "프로젝트에서 재사용할 데이터 준비 함수를 만들 수 있다."],
    "마지막 주입니다. 지금까지 배운 것을 모아 **손글씨 숫자 분류 프로젝트**를 처음부터 끝까지 완성합니다. 하루에 한 단계씩 함수를 만들어 갑니다.\n\n" + PLAN_MD,
    [("모델 설정(학습률 등)을 고를 때 쓰면 안 되는 데이터는?", ["학습 데이터", "검증 데이터", "테스트 데이터", "교차 검증"], 2)],
    "세 갈래로 나누기",
    "- **학습**(60%): 가중치 학습\n- **검증**(20%): 에폭 수·학습률 같은 설정 고르기, 조기 종료\n- **테스트**(20%): 마지막에 한 번만 최종 성능 확인\n\n"
    "`train_test_split`을 두 번 써서 나눕니다. 먼저 20%를 테스트로 떼고, 남은 80%의 25%(전체의 20%)를 검증으로 뗍니다. `stratify`로 숫자 비율을 유지합니다.",
    '''
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split

    digits = load_digits()
    X_tmp, X_test, y_tmp, y_test = train_test_split(
        digits.images, digits.target, test_size=0.2, random_state=0, stratify=digits.target)
    X_train, X_val, y_train, y_val = train_test_split(X_tmp, y_tmp, test_size=0.25, random_state=0, stratify=y_tmp)
    print(len(X_train), len(X_val), len(X_test))
    ''',
    "테스트 점수를 보고 설정을 바꾸기 시작하면 테스트 데이터가 사실상 검증 데이터가 되어, 최종 점수를 믿을 수 없게 됩니다.",
    "두 번 나누세요.", "프로젝트용 데이터 준비 함수를 만드세요.",
    ["학습 = 가중치, 검증 = 설정 선택, 테스트 = 최종 1회.", "`train_test_split` 두 번으로 60/20/20.", "`stratify`로 클래스 비율 유지.",
     "준비 코드를 함수로 만들어 재사용."],
    [("조기 종료 시점을 정할 때 쓰는 데이터는?", ["학습", "검증", "테스트", "아무거나"], 1),
     ("80% 중 25%를 떼면 전체의 몇 %인가?", ["10%", "20%", "25%", "40%"], 1)],
    [
        X("d162_fill_1", "두 번 나누기",
          "digits를 테스트 20%, 남은 것의 25%를 검증으로 나눠(`random_state=seed`, `stratify` 사용) `[학습 수, 검증 수, 테스트 수]`를 반환하세요.", ["dl_project", "train_test"], 1,
          '''
          from sklearn.datasets import load_digits
          from sklearn.model_selection import train_test_split


          def split_sizes(seed):
              digits = load_digits()
              X_tmp, X_test, y_tmp, y_test = train_test_split(
                  digits.images, digits.target, test_size=0.2, random_state=seed, stratify=digits.target)
              X_train, X_val, y_train, y_val = train_test_split(
                  X_tmp, y_tmp, test_size=0.25, random_state=seed, stratify=y_tmp)
              return [len(X_train), len(X_val), len(X_test)]
          ''', "split_sizes", [[0], [1]],
          ["첫 분할에서 떼는 테스트 비율입니다.", "두 번째 분할은 남은 데이터의 정답으로 비율을 맞춥니다."],
          blanks=["test_size=0.2", "stratify=y_tmp"], tol=None),
        X("d162_code_1", "데이터 준비 함수",
          "`split_data(seed)`를 완성하세요. 위와 같이 나눈 뒤 이미지는 `float32`, (N, 1, 8, 8), 16으로 나눈 텐서, 정답은 정수 텐서로 바꿔 "
          "`[(X_train, y_train), (X_val, y_val), (X_test, y_test)]`를 반환합니다. `summary`는 이미 작성되어 있습니다.",
          ["dl_project", "image_tensor"], 2,
          IMPORTS + SPLIT_SRC + '''

          def summary(seed):
              (X_train, y_train), (X_val, y_val), (X_test, y_test) = split_data(seed)
              loader = make_loader((X_train, y_train), shuffle=True)
              return [list(X_train.shape), len(y_val), len(y_test), X_train.max().item(),
                      torch.bincount(y_train).tolist(), len(loader)]
          ''', "summary", [[0], [1]],
          ["두 번 나눈 뒤 세 쌍을 같은 방식으로 변환하니 변환 함수를 하나 만들어 두면 편합니다.", "이미지는 `unsqueeze(1)`로 채널 차원을 추가합니다."],
          starter=None, tol=None),
    ], review_title="4단계 프로젝트 시작")

# fix starter for d162_code_1: keep make_loader + summary, blank out split_data body
_ex = day162["exercises"][1]
_ex["starter_code"] = _ex["solution"].split("def split_data(seed):")[0] + '''def split_data(seed):
    # 여기에 코드를 작성하세요
    pass


def make_loader(data, shuffle=False):
''' + _ex["solution"].split("def make_loader(data, shuffle=False):\n")[1]

# ====================================================================== Day 163
day163 = D(
    163, "프로젝트: 모델과 학습 함수", W, ["dl_project", "training_loop", "cnn"],
    ["한 에폭 학습을 함수로 만들어 재사용할 수 있다.", "에폭마다 학습 손실과 검증 정확도를 기록할 수 있다."],
    "어제는 데이터를 학습·검증·테스트로 나누는 `split_data`를 만들었습니다.",
    [("학습·검증·테스트 중 마지막에 한 번만 쓰는 것은?", ["학습", "검증", "테스트", "모두"], 2)],
    "학습 함수로 묶기",
    "학습 루프를 `train_one_epoch(model, loader, optimizer)` 함수로 만들면 어떤 모델이든 같은 코드로 학습할 수 있습니다. 함수 안에서 `model.train()`을 먼저 부르고, "
    "에폭 평균 손실을 돌려줍니다.\n\n모델은 21주차의 CNN을 채널 수 `c`를 바꿀 수 있게 일반화한 `CNN(c=8)`을 씁니다.",
    '''
    import torch
    from torch import nn

    class CNN(nn.Module):
        def __init__(self, c=8):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, c, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Conv2d(c, 2 * c, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(),
            )
            self.fc = nn.Linear(2 * c * 4, 10)

        def forward(self, x):
            return self.fc(self.features(x))

    for c in [4, 8, 16]:
        model = CNN(c)
        print(c, model(torch.zeros(2, 1, 8, 8)).shape, sum(p.numel() for p in model.parameters()))
    ''',
    "평가 함수 안에서 `model.eval()`을 불렀다면, 다음 학습 전에 `model.train()`으로 돌려놓아야 합니다. 학습 함수 첫 줄에서 부르면 잊을 일이 없습니다.",
    "학습 함수를 완성하세요.", "에폭별 기록을 남기세요.",
    ["학습 루프를 함수로 → 모델과 상관없이 재사용.", "함수 첫 줄에 `model.train()`.", "에폭 평균 손실을 반환.", "에폭마다 학습 손실·검증 정확도를 기록."],
    [("`CNN(c=16)`의 마지막 선형 층 입력 수는?", ["64", "128", "16", "32"], 1),
     ("학습 함수 첫 줄에 `model.train()`을 두는 이유는?", ["평가 모드에서 돌아오기 위해", "속도", "기울기 초기화", "학습률 설정"], 0)],
    [
        X("d163_fill_1", "학습 함수",
          "`train_one_epoch`을 완성하고, `split_data(seed)`의 학습 데이터로 `torch.manual_seed(0)` 후 `CNN()`과 `optim.Adam(lr=0.01)`로 한 에폭 학습한 평균 손실(소수 넷째 자리)을 반환하세요.", ["training_loop"], 1,
          IMPORTS + SPLIT_SRC + CNN_SRC + TRAIN_SRC + '''

          def first_epoch_loss(seed):
              train, _, _ = split_data(seed)
              torch.manual_seed(0)
              model = CNN()
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              return round(train_one_epoch(model, make_loader(train, shuffle=True), optimizer), 4)
          ''', "first_epoch_loss", [[0], [1]],
          ["함수 시작에서 학습 모드로 바꾸는 메서드입니다.", "배치 손실에 배치 크기를 곱해 더합니다."],
          blanks=["model.train()", "loss.item() * len(yb)"], tol=3e-3, tl=90),
        X("d163_code_1", "에폭 기록",
          "`split_data(seed)`로 데이터를 준비하고 `torch.manual_seed(0)` 후 `CNN()`, `optim.Adam(lr=0.01)`을 만드세요. `epochs`번 `train_one_epoch`을 부르며 "
          "에폭마다 `[학습 손실, 검증 정확도]`(소수 넷째 자리)를 기록한 리스트를 반환합니다. 검증 정확도는 주어진 `evaluate`로 구합니다.",
          ["dl_project", "training_loop"], 2,
          IMPORTS + SPLIT_SRC + CNN_SRC + TRAIN_SRC + EVAL_SRC + '''

          def history(seed, epochs):
              train, val, _ = split_data(seed)
              train_loader, val_loader = make_loader(train, shuffle=True), make_loader(val)
              torch.manual_seed(0)
              model = CNN()
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              records = []
              for _ in range(epochs):
                  loss = train_one_epoch(model, train_loader, optimizer)
                  records.append([round(loss, 4), round(evaluate(model, val_loader), 4)])
              return records
          ''', "history", [[0, 3], [1, 2]],
          ["DataLoader는 에폭 반복 전에 한 번만 만드세요.", "학습 손실은 `train_one_epoch`의 반환값입니다."], tol=3e-3, tl=90),
    ])

# ====================================================================== Day 164
REPORT_SRC = '''

          def report(model, data):
              X, y = data
              model.eval()
              with torch.no_grad():
                  pred = model(X).argmax(dim=1)
              cm = torch.bincount(y * 10 + pred, minlength=100).reshape(10, 10)
              recall = cm.diag() / cm.sum(dim=1)
              return cm, recall
'''
day164 = D(
    164, "프로젝트: 평가 함수", W, ["dl_project", "confusion_matrix", "precision_recall"],
    ["혼동 행렬과 클래스별 재현율로 모델의 약점을 찾을 수 있다."],
    "어제는 학습 함수와 에폭 기록을 만들었습니다. 정확도 하나로는 **어떤 숫자를 헷갈리는지** 알 수 없습니다.",
    [("에폭마다 기록한 검증 정확도로 알 수 있는 것은?", ["언제 성능이 멈추는지", "테스트 점수", "가중치 수", "학습률"], 0)],
    "약점 찾기",
    "Day 92의 **혼동 행렬**을 PyTorch로 만들어 봅니다. 행은 정답, 열은 예측입니다. 정답 y와 예측 p를 `y * 10 + p`라는 번호 하나로 바꿔 `torch.bincount`로 세면 "
    "100칸짜리 개수가 나오고, 이것을 (10, 10)으로 바꾸면 혼동 행렬입니다.\n\n대각선이 맞힌 개수이므로 **클래스별 재현율** = 대각선 ÷ 행의 합입니다.",
    '''
    import torch

    y = torch.tensor([0, 0, 1, 1, 2, 2])
    pred = torch.tensor([0, 1, 1, 1, 2, 0])
    cm = torch.bincount(y * 3 + pred, minlength=9).reshape(3, 3)
    print(cm)
    print(cm.diag() / cm.sum(dim=1))
    ''',
    "sklearn의 `confusion_matrix`와 같은 결과지만, 텐서만으로 계산하면 학습 코드 안에서 바로 쓸 수 있습니다.",
    "혼동 행렬을 계산하세요.", "가장 약한 숫자를 찾으세요.",
    ["혼동 행렬: 행 = 정답, 열 = 예측.", "`bincount(y * k + p)`로 한 번에 세기.", "클래스별 재현율 = 대각선 / 행 합.", "약한 클래스를 알면 개선 방향이 보인다."],
    [("혼동 행렬의 대각선 값의 의미는?", ["맞힌 개수", "틀린 개수", "확률", "손실"], 0),
     ("클래스 4개일 때 정답 2, 예측 3의 번호(`y * 4 + p`)는?", ["5", "11", "14", "9"], 1)],
    [
        X("d164_fill_1", "혼동 행렬",
          "정답·예측 목록과 클래스 수 k로 혼동 행렬을 만들어 반환하세요.", ["confusion_matrix"], 1,
          '''
          import torch


          def confusion(y_true, y_pred, k):
              y, p = torch.tensor(y_true), torch.tensor(y_pred)
              return torch.bincount(y * k + p, minlength=k * k).reshape(k, k)
          ''', "confusion", [[[0, 0, 1, 1, 2, 2], [0, 1, 1, 1, 2, 0], 3], [[1, 0, 1], [1, 1, 1], 2]],
          ["정수 값의 개수를 세는 함수입니다.", "개수 목록을 k×k로 바꿉니다."], blanks=["bincount", "reshape(k, k)"], tol=None),
        X("d164_code_1", "약점 분석",
          "주어진 함수로 `split_data(seed)`, `torch.manual_seed(0)` 후 `fit(CNN(), 학습 DataLoader(섞기), epochs)`를 하고, `report(model, 검증 데이터)`를 완성해 사용하세요. "
          "`{\"accuracy\": 검증 정확도, \"worst\": 재현율이 가장 낮은 숫자, \"worst_recall\": 그 재현율, \"confused_with\": 그 숫자를 가장 많이 잘못 예측한 숫자}`를 반환합니다(실수는 소수 넷째 자리). "
          "`confused_with`는 혼동 행렬의 그 행에서 대각선을 0으로 바꾼 뒤 argmax로 구합니다.",
          ["dl_project", "confusion_matrix", "precision_recall"], 3,
          ALL + REPORT_SRC + '''

          def weakness(seed, epochs):
              train, val, _ = split_data(seed)
              torch.manual_seed(0)
              model = fit(CNN(), make_loader(train, shuffle=True), epochs)
              cm, recall = report(model, val)
              worst = recall.argmin().item()
              row = cm[worst].clone()
              row[worst] = 0
              return {
                  "accuracy": round(evaluate(model, make_loader(val)), 4),
                  "worst": worst,
                  "worst_recall": round(recall[worst].item(), 4),
                  "confused_with": row.argmax().item(),
              }
          ''', "weakness", [[0, 4], [1, 3]],
          ["혼동 행렬은 오늘 개념 예제처럼 `bincount`로 만듭니다.", "행을 복사(`clone`)한 뒤 대각선 칸만 0으로 바꾸세요."], tol=3e-3, tl=90),
    ])

# report + weakness are both the student's job
_ex = day164["exercises"][1]
_ex["starter_code"] = (_ex["solution"].split("def report(model, data):")[0]
                       + '''def report(model, data):
    # (혼동 행렬, 클래스별 재현율)을 반환하세요
    pass


def weakness(seed, epochs):
    # 여기에 코드를 작성하세요
    pass
''')

# ====================================================================== Day 165
day165 = D(
    165, "프로젝트: MLP와 CNN 비교", W, ["dl_project", "cnn", "nn_linear"],
    ["같은 조건에서 두 모델을 공정하게 비교할 수 있다.", "정확도와 매개변수 수를 함께 비교할 수 있다."],
    "어제는 혼동 행렬로 모델의 약점을 찾았습니다. 오늘은 **모델 구조**를 바꿔 비교합니다.",
    [("클래스별 재현율 계산식은?", ["대각선 / 행 합", "대각선 / 열 합", "행 합 / 전체", "대각선 / 전체"], 0)],
    "공정한 비교",
    "모델을 비교할 때는 **나머지 조건을 모두 같게** 해야 합니다. 같은 데이터 분할, 같은 옵티마이저와 학습률, 같은 에폭 수, 같은 시드.\n\n"
    "그리고 정확도뿐 아니라 **매개변수 수**(모델 크기), 학습 시간도 함께 봐야 합니다. 정확도가 조금 높아도 모델이 10배 크다면 상황에 따라 작은 모델이 나을 수 있습니다.",
    '''
    import torch
    from torch import nn

    mlp = nn.Sequential(nn.Flatten(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10))
    cnn = nn.Sequential(nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(128, 10))
    for name, model in [("MLP", mlp), ("CNN", cnn)]:
        print(name, model(torch.zeros(1, 1, 8, 8)).shape, sum(p.numel() for p in model.parameters()))
    ''',
    "MLP는 이미지를 64개 숫자로 펼쳐서 보기 때문에 \"이웃한 픽셀\"이라는 정보를 쓰지 못합니다. CNN은 커널로 주변을 함께 봅니다.",
    "매개변수 수를 비교하세요.", "두 모델을 같은 조건으로 학습해 비교하세요.",
    ["비교할 땐 나머지 조건을 모두 같게.", "정확도 + 매개변수 수 + 시간.", "MLP는 픽셀 이웃 관계를 쓰지 못한다.", "CNN은 적은 매개변수로 이미지에 강하다."],
    [("공정한 비교를 위해 같게 둘 것이 아닌 것은?", ["데이터 분할", "학습률", "비교하려는 모델 구조", "에폭 수"], 2),
     ("이미지를 펼쳐서 입력받는 모델은?", ["MLP", "CNN", "RNN", "둘 다"], 0)],
    [
        X("d165_fill_1", "크기 비교",
          "은닉층 크기 h인 MLP와 채널 c인 프로젝트 CNN의 매개변수 수를 `[MLP, CNN]`으로 반환하세요.", ["dl_project"], 1,
          '''
          import torch
          from torch import nn
          ''' + CNN_SRC + '''

          def sizes(h, c):
              mlp = nn.Sequential(nn.Flatten(), nn.Linear(64, h), nn.ReLU(), nn.Linear(h, 10))
              count = lambda m: sum(p.numel() for p in m.parameters())
              return [count(mlp), count(CNN(c))]
          ''', "sizes", [[32, 8], [128, 4]],
          ["이미지를 64개로 펼치는 층입니다.", "매개변수의 원소 수를 세는 메서드입니다."], blanks=["Flatten", "numel"], tol=None),
        X("d165_code_1", "MLP 대 CNN",
          "`split_data(seed)`로 데이터를 준비하세요. 두 모델 각각 `torch.manual_seed(0)` 후 만들어 `fit(모델, 학습 DataLoader(섞기), epochs)`로 학습합니다. "
          "MLP는 `nn.Sequential(nn.Flatten(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10))`, CNN은 `CNN()`입니다. "
          "`{\"mlp\": [검증 정확도, 매개변수 수], \"cnn\": [...], \"better\": 검증 정확도가 높은 이름(같으면 \"cnn\")}`을 반환하세요.",
          ["dl_project", "cnn"], 3,
          ALL + '''

          def compare_models(seed, epochs):
              train, val, _ = split_data(seed)
              makers = {
                  "mlp": lambda: nn.Sequential(nn.Flatten(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10)),
                  "cnn": lambda: CNN(),
              }
              results = {}
              for name, make in makers.items():
                  torch.manual_seed(0)
                  model = fit(make(), make_loader(train, shuffle=True), epochs)
                  n_params = sum(p.numel() for p in model.parameters())
                  results[name] = [round(evaluate(model, make_loader(val)), 4), n_params]
              results["better"] = "mlp" if results["mlp"][0] > results["cnn"][0] else "cnn"
              return results
          ''', "compare_models", [[0, 5], [1, 3]],
          ["모델 만드는 함수를 딕셔너리에 두고 반복하면 조건을 같게 유지하기 쉽습니다.", "모델마다 DataLoader를 새로 만들어야 섞는 순서도 같아집니다."],
          tol=3e-3, tl=120),
    ])

# ====================================================================== Day 166
day166 = D(
    166, "프로젝트: 하이퍼파라미터 조정", W, ["dl_project", "hyperparameter"],
    ["검증 데이터로 하이퍼파라미터를 고르고 테스트로 최종 성능을 확인할 수 있다."],
    "어제는 MLP와 CNN을 비교했습니다. 이제 CNN의 설정(채널 수, 학습률)을 고릅니다.",
    [("모델을 공정하게 비교하려면?", ["나머지 조건을 같게", "에폭을 다르게", "데이터를 다르게", "시드를 다르게"], 0)],
    "검증으로 고르고 테스트로 확인",
    "Day 97의 그리드 탐색을 직접 반복문으로 합니다.\n\n1. 후보 조합마다 학습 → **검증** 정확도 기록\n2. 검증 정확도가 가장 높은 조합 선택\n"
    "3. 그 조합의 모델로 **테스트** 정확도를 딱 한 번 확인\n\n딥러닝은 학습이 오래 걸려서 교차 검증 대신 검증 데이터 하나를 쓰는 경우가 많습니다.",
    '''
    from itertools import product

    channels, lrs = [4, 8], [0.003, 0.01]
    for c, lr in product(channels, lrs):
        print(c, lr)
    ''',
    "후보가 많으면 시간이 오래 걸립니다. 넓은 범위에서 몇 개를 먼저 시험하고 좋은 근처를 더 촘촘히 보는 것이 효율적입니다.",
    "가장 좋은 조합을 고르세요.", "작은 그리드 탐색을 하세요.",
    ["후보마다 학습 → 검증 점수.", "검증 최고 조합 선택.", "테스트는 마지막 한 번.", "`itertools.product`로 조합 만들기."],
    [("하이퍼파라미터를 고를 때 보는 점수는?", ["학습 점수", "검증 점수", "테스트 점수", "손실 합"], 1),
     ("`product([1, 2], [\"a\", \"b\"])`의 조합 수는?", ["2", "3", "4", "6"], 2)],
    [
        X("d166_fill_1", "최고 조합",
          "`{(c, lr): 검증 정확도}` 대신 `[[c, lr, 정확도], ...]` 목록을 받아, 정확도가 가장 높은 `[c, lr]`을 반환하세요(같으면 앞쪽).", ["hyperparameter"], 1,
          '''
          def best_config(results):
              best = max(results, key=lambda r: r[2])
              return best[:2]
          ''', "best_config", [[[[4, 0.003, 0.9], [4, 0.01, 0.95], [8, 0.003, 0.93]]], [[[8, 0.01, 0.8], [4, 0.01, 0.8]]]],
          ["가장 큰 항목을 고르는 내장 함수입니다.", "정확도는 각 항목의 세 번째 값입니다."], blanks=["max", "r[2]"], tol=None),
        X("d166_code_1", "그리드 탐색",
          "`split_data(seed)`로 데이터를 준비하고, 채널 `[4, 8]` × 학습률 `[0.003, 0.01]`의 4가지 조합(`itertools.product` 순서)마다 "
          "`torch.manual_seed(0)` 후 `fit(CNN(c), 학습 DataLoader(섞기), epochs, lr)`로 학습해 검증 정확도를 구하세요. "
          "검증 정확도가 가장 높은 조합(같으면 먼저 나온 것)의 테스트 정확도까지 구해 `{\"val\": [[c, lr, 검증 정확도], ...], \"best\": [c, lr], \"test\": 테스트 정확도}`를 반환하세요.",
          ["dl_project", "hyperparameter"], 3,
          '''
          from itertools import product
          ''' + ALL.lstrip("\n").replace("          import torch", "import torch", 1) + '''

          def grid_search(seed, epochs):
              train, val, test = split_data(seed)
              records, models = [], []
              for c, lr in product([4, 8], [0.003, 0.01]):
                  torch.manual_seed(0)
                  model = fit(CNN(c), make_loader(train, shuffle=True), epochs, lr)
                  records.append([c, lr, round(evaluate(model, make_loader(val)), 4)])
                  models.append(model)
              i = max(range(len(records)), key=lambda k: records[k][2])
              return {"val": records, "best": records[i][:2], "test": round(evaluate(models[i], make_loader(test)), 4)}
          ''', "grid_search", [[0, 3], [1, 2]],
          ["조합마다 학습한 모델을 리스트에 함께 저장해 두면 나중에 최고 모델을 다시 학습하지 않아도 됩니다.",
           "가장 높은 위치는 `max(range(len(records)), key=...)`로 찾을 수 있습니다."], tol=3e-3, tl=150),
    ])

# ====================================================================== Day 167
day167 = D(
    167, "프로젝트: 추론 함수", W, ["inference", "dl_project"],
    ["학습된 모델로 새 입력의 클래스 확률과 상위 k개 예측을 구할 수 있다."],
    "어제는 검증 데이터로 설정을 골랐습니다. 마지막으로 모델을 **사용하는** 함수를 만듭니다.",
    [("최종 테스트 정확도는 몇 번 확인하나?", ["에폭마다", "후보마다", "마지막에 한 번", "확인하지 않는다"], 2)],
    "예측 결과 내보내기",
    "**추론**(inference)은 학습된 모델로 새 데이터를 예측하는 것입니다. 순서는 늘 같습니다.\n\n"
    "1. `model.eval()`과 `torch.no_grad()`\n2. 입력을 학습 때와 같은 방식으로 전처리((N, 1, 8, 8), 16으로 나누기)\n"
    "3. 로짓 → `torch.softmax(로짓, dim=1)`로 확률\n4. `torch.topk(확률, k)`로 가장 그럴듯한 k개\n\n"
    "확률을 함께 보여 주면 모델이 얼마나 확신하는지 알 수 있습니다.",
    '''
    import torch

    logits = torch.tensor([[2.0, 0.5, 4.0, 1.0]])
    probs = torch.softmax(logits, dim=1)
    print(probs.round(decimals=3), probs.sum().item())
    top = torch.topk(probs, 2, dim=1)
    print(top.indices.tolist(), top.values.round(decimals=3).tolist())
    ''',
    "확률이 0.5도 안 되는 예측은 사람이 다시 확인하도록 표시하는 식으로, 확률을 서비스에 활용할 수 있습니다.",
    "상위 k개를 구하세요.", "학습한 모델로 추론하세요.",
    ["추론 = eval + no_grad + 같은 전처리.", "softmax로 확률.", "`topk`로 상위 k개.", "확률로 확신 정도 판단."],
    [("softmax 출력의 합은?", ["0", "1", "클래스 수", "로짓 합"], 1),
     ("`torch.topk(x, 3, dim=1)`이 돌려주는 것은?", ["값과 위치", "위치만", "값만", "합계"], 0)],
    [
        X("d167_fill_1", "상위 k개",
          "로짓 목록(샘플 하나)을 softmax 확률로 바꿔 상위 k개의 `[번호 리스트, 확률 리스트(소수 넷째 자리)]`를 반환하세요.", ["inference"], 1,
          '''
          import torch


          def top_k(logits, k):
              probs = torch.softmax(torch.tensor([logits], dtype=torch.float32), dim=1)
              top = torch.topk(probs, k, dim=1)
              return [top.indices[0].tolist(), [round(v, 4) for v in top.values[0].tolist()]]
          ''', "top_k", [[[2.0, 0.5, 4.0, 1.0], 2], [[0, 0, 0], 1], [[1, 3, 2, -1, 0], 3]],
          ["로짓을 확률로 바꾸는 함수입니다.", "가장 큰 k개를 고르는 함수입니다."], blanks=["softmax", "topk"]),
        X("d167_code_1", "추론 함수",
          "`predict(model, images, k)`를 완성하세요. `images`는 0~16 값의 8×8 목록들입니다. 학습 때와 같이 전처리하고 eval·no_grad 상태에서 "
          "샘플마다 `{\"label\": 1순위 숫자, \"top\": 상위 k개 숫자, \"prob\": 1순위 확률(소수 넷째 자리)}`를 만든 리스트를 반환합니다. `run`은 이미 작성되어 있습니다.",
          ["inference", "dl_project"], 3,
          ALL + '''

          def predict(model, images, k):
              x = torch.tensor(images, dtype=torch.float32).unsqueeze(1) / 16
              model.eval()
              with torch.no_grad():
                  probs = torch.softmax(model(x), dim=1)
              top = torch.topk(probs, k, dim=1)
              return [{"label": idx[0], "top": idx, "prob": round(val[0], 4)}
                      for idx, val in zip(top.indices.tolist(), top.values.tolist())]


          def run(seed, indices, k):
              train, _, test = split_data(seed)
              torch.manual_seed(0)
              model = fit(CNN(), make_loader(train, shuffle=True), 4)
              images = (test[0][indices, 0] * 16).tolist()
              return predict(model, images, k)
          ''', "run", [[0, [0, 1, 2], 2], [1, [5, 10], 3]],
          ["이미지 목록을 (N, 1, 8, 8) 텐서로 만들고 16으로 나누세요.", "`topk` 결과의 `indices`, `values`를 샘플별로 묶어 딕셔너리를 만드세요."],
          tol=3e-3, tl=90),
    ])
# predict only: starter keeps run, blanks predict body
_ex = day167["exercises"][1]
_ex["starter_code"] = (_ex["solution"].split("def predict(model, images, k):")[0]
                       + "def predict(model, images, k):\n    # 여기에 코드를 작성하세요\n    pass\n\n\ndef run(seed, indices, k):"
                       + _ex["solution"].split("def run(seed, indices, k):")[1])

# ====================================================================== Day 168 (final review)
day168 = D(
    168, "4단계 마무리 누적 복습", W, ["dl_project", "early_stopping", "state_dict", "cnn", "inference"],
    ["데이터 준비부터 학습·조기 종료·평가·저장·추론까지 딥러닝 프로젝트 전체를 수행할 수 있다."],
    "168일 과정의 마지막 날입니다.\n\n| 단계 | 기간 | 핵심 |\n|---|---|---|\n| 1 | Day 1~35 | Python 기초 |\n| 2 | Day 36~70 | 객체지향, NumPy, pandas, 시각화 |\n"
    "| 3 | Day 71~119 | scikit-learn 머신러닝 |\n| 4 | Day 120~168 | PyTorch 딥러닝 |\n\n오늘은 4단계 전체를 하나의 함수로 묶습니다.",
    [("딥러닝 학습 루프의 순서는?", ["zero_grad → backward → step", "step → backward → zero_grad", "backward → step → zero_grad", "순서 무관"], 0),
     ("모델을 저장할 때 권장하는 것은?", ["모델 객체 전체", "`state_dict()`", "옵티마이저만", "손실 값"], 1)],
    "전체 파이프라인",
    "한 프로젝트의 흐름을 정리하면 다음과 같습니다.\n\n1. 데이터 분할(학습·검증·테스트)과 DataLoader\n2. 모델 정의(nn.Module)\n3. 에폭마다 학습 → 검증, 최고 검증 점수일 때 체크포인트\n"
    "4. 조기 종료 후 최고 가중치 복원\n5. 테스트 1회 평가\n6. state_dict 저장 → 불러와 추론\n\n"
    "여기까지 왔다면 다음 공부로 torchvision의 사전 학습 모델, 더 큰 데이터셋, GPU 학습을 추천합니다.",
    '''
    import copy
    import torch
    from torch import nn

    model = nn.Linear(2, 1)
    best_state = copy.deepcopy(model.state_dict())
    with torch.no_grad():
        model.weight.fill_(5.0)
    model.load_state_dict(best_state)
    print(model.weight.tolist() != [[5.0, 5.0]])
    ''',
    None,
    "softmax 성질을 확인하세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["데이터 → 모델 → 학습·검증 → 조기 종료 → 테스트 → 저장·추론.", "평가는 eval + no_grad.", "설정은 검증으로, 최종 성능은 테스트로.",
     "168일 완주를 축하합니다!"],
    [("최고 검증 점수일 때 가중치를 복사하는 방법은?", ["`copy.deepcopy(model.state_dict())`", "`model.state_dict()` 그대로", "`model.copy()`", "`torch.save`만"], 0),
     ("최종 성능 보고에 쓰는 데이터는?", ["학습", "검증", "테스트", "학습+검증"], 2)],
    [
        X("d168_fill_1", "softmax 성질",
          "로짓 목록에 같은 상수 `shift`를 더해도 softmax 확률이 같은지 확인해 `[확률(소수 넷째 자리), 같은지]`를 반환하세요.", ["inference"], 1,
          '''
          import torch


          def softmax_shift(logits, shift):
              x = torch.tensor(logits, dtype=torch.float32)
              p = torch.softmax(x, dim=0)
              q = torch.softmax(x + shift, dim=0)
              return [[round(v, 4) for v in p.tolist()], torch.allclose(p, q, atol=1e-6)]
          ''', "softmax_shift", [[[1.0, 2.0, 3.0], 10], [[0.5, -0.5], -3]],
          ["확률로 바꾸는 함수입니다.", "두 텐서가 거의 같은지 비교하는 함수입니다."], blanks=["softmax", "allclose"]),
        X("d168_code_1", "최종 파이프라인",
          "`split_data(seed)`로 데이터를 준비하고 `torch.manual_seed(0)` 후 `CNN()`과 `optim.Adam(lr=0.01)`을 만드세요. 최대 `max_epochs` 에폭 동안 `train_one_epoch` 후 검증 정확도를 구해, "
          "**더 높을 때만** 최고 기록과 `copy.deepcopy(model.state_dict())`를 저장하고, `patience`번 연속 나아지지 않으면 멈춥니다. "
          "최고 가중치를 되돌린 뒤 `{\"best_epoch\": 최고 에폭(0부터), \"epochs_run\": 실제 학습한 에폭 수, \"val\": 최고 검증 정확도, \"test\": 테스트 정확도}`(정확도는 소수 넷째 자리)를 반환하세요.",
          ["dl_project", "early_stopping", "state_dict"], 3,
          '''
          import copy
          ''' + ALL.lstrip("\n").replace("          import torch", "import torch", 1) + '''

          def final_pipeline(seed, max_epochs, patience):
              train, val, test = split_data(seed)
              train_loader, val_loader = make_loader(train, shuffle=True), make_loader(val)
              torch.manual_seed(0)
              model = CNN()
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              best, best_epoch, best_state, wait, epochs_run = -1.0, -1, None, 0, 0
              for epoch in range(max_epochs):
                  train_one_epoch(model, train_loader, optimizer)
                  epochs_run += 1
                  acc = evaluate(model, val_loader)
                  if acc > best:
                      best, best_epoch, wait = acc, epoch, 0
                      best_state = copy.deepcopy(model.state_dict())
                  else:
                      wait += 1
                      if wait >= patience:
                          break
              model.load_state_dict(best_state)
              return {
                  "best_epoch": best_epoch,
                  "epochs_run": epochs_run,
                  "val": round(best, 4),
                  "test": round(evaluate(model, make_loader(test)), 4),
              }
          ''', "final_pipeline", [[0, 12, 2], [1, 8, 3]],
          ["학습한 에폭 수는 break 전에 세어 두세요.", "반복이 끝나면 저장해 둔 최고 가중치를 모델에 다시 넣고 테스트합니다."], tol=3e-3, tl=150),
        X("d168_code_2", "저장한 모델로 추론(도전)",
          "`split_data(seed)`로 준비한 학습 데이터로 `torch.manual_seed(0)` 후 `fit(CNN(), 학습 DataLoader(섞기), 3)`을 하세요. state_dict를 `io.BytesIO`에 저장하고, "
          "`torch.manual_seed(1)` 후 새 `CNN()`에 불러온 뒤 두 모델의 테스트 예측(argmax)이 모두 같은지 확인합니다. "
          "`[예측이 모두 같은지, 불러온 모델의 테스트 정확도(소수 넷째 자리), 저장된 키 개수]`를 반환하세요.",
          ["state_dict", "inference"], 3,
          '''
          import io
          ''' + ALL.lstrip("\n").replace("          import torch", "import torch", 1) + '''

          def reload_and_predict(seed):
              train, _, test = split_data(seed)
              torch.manual_seed(0)
              model = fit(CNN(), make_loader(train, shuffle=True), 3)
              buffer = io.BytesIO()
              torch.save(model.state_dict(), buffer)
              buffer.seek(0)
              torch.manual_seed(1)
              loaded = CNN()
              state = torch.load(buffer)
              loaded.load_state_dict(state)
              model.eval()
              loaded.eval()
              with torch.no_grad():
                  same = torch.equal(model(test[0]).argmax(dim=1), loaded(test[0]).argmax(dim=1))
              return [same, round(evaluate(loaded, make_loader(test)), 4), len(state)]
          ''', "reload_and_predict", [[0], [1]],
          ["저장 뒤 `seek(0)`으로 처음으로 돌아가야 읽을 수 있습니다.", "두 모델 모두 eval 모드에서 예측을 비교하세요."],
          tol=3e-3, tl=90, required=False),
    ], review_title="168일 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day162, day163, day164, day165, day166, day167, day168])
