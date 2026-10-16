"""Week 23 (Day 155-161): 전이 학습 (인터넷 없이 digits 0~4로 사전 학습 → 5~9에 재사용)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, write_lessons  # noqa: E402

W = 23

IMPORTS = '''
          import torch
          from sklearn.datasets import load_digits
          from torch import nn, optim
'''
NET_SRC = '''

          class Net(nn.Module):
              def __init__(self, n_out):
                  super().__init__()
                  self.features = nn.Sequential(
                      nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                      nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(),
                  )
                  self.fc = nn.Linear(64, n_out)

              def forward(self, x):
                  return self.fc(self.features(x))
'''
TOOLS_SRC = '''

          def all_digits():
              digits = load_digits()
              X = torch.tensor(digits.images, dtype=torch.float32).unsqueeze(1) / 16
              return X, torch.tensor(digits.target)


          def fit(model, X, y, epochs, lr=0.01):
              params = [p for p in model.parameters() if p.requires_grad]
              optimizer = optim.Adam(params, lr=lr)
              for _ in range(epochs):
                  loss = nn.CrossEntropyLoss()(model(X), y)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return loss.item()


          def accuracy(model, X, y):
              model.eval()
              with torch.no_grad():
                  acc = (model(X).argmax(dim=1) == y).float().mean().item()
              model.train()
              return acc


          def pretrained():
              X, y = all_digits()
              keep = y < 5
              torch.manual_seed(0)
              model = Net(5)
              fit(model, X[keep], y[keep], 60)
              return model


          def few_shot(seed, per_class):
              X, y = all_digits()
              g = torch.Generator().manual_seed(seed)
              train_idx, test_idx = [], []
              for digit in range(5, 10):
                  idx = torch.nonzero(y == digit).flatten()
                  idx = idx[torch.randperm(len(idx), generator=g)]
                  train_idx += idx[:per_class].tolist()
                  test_idx += idx[per_class:].tolist()
              return X[train_idx], y[train_idx] - 5, X[test_idx], y[test_idx] - 5
'''
BASE = IMPORTS + NET_SRC + TOOLS_SRC

# ====================================================================== Day 155
day155 = D(
    155, "state_dict와 모델 저장", W, ["state_dict", "nn_module"],
    ["state_dict로 모델의 가중치를 꺼내고 저장·불러오기를 할 수 있다."],
    "이번 주는 **전이 학습**을 배웁니다. 이미 학습된 모델의 지식을 새 문제에 재사용하는 방법입니다. 그 첫걸음은 학습한 가중치를 저장하고 불러오는 것입니다.",
    [("BatchNorm이 평가 모드에서 쓰는 통계는?", ["현재 배치", "이동 평균", "0", "테스트 전체"], 1)],
    "가중치 꺼내고 넣기",
    "`model.state_dict()`는 \"층 이름 → 가중치 텐서\" 딕셔너리입니다.\n\n"
    "- 저장: `torch.save(model.state_dict(), \"model.pt\")`\n"
    "- 불러오기: 같은 구조의 모델을 만든 뒤 `model.load_state_dict(torch.load(\"model.pt\"))`\n\n"
    "모델 객체 전체가 아니라 state_dict를 저장하는 것이 권장 방법입니다. 아래 예제는 파일 대신 메모리(`io.BytesIO`)에 저장합니다.",
    '''
    import io
    import torch
    from torch import nn

    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(2, 3), nn.ReLU(), nn.Linear(3, 1))
    print({k: list(v.shape) for k, v in model.state_dict().items()})

    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer)
    buffer.seek(0)
    copy = nn.Sequential(nn.Linear(2, 3), nn.ReLU(), nn.Linear(3, 1))
    copy.load_state_dict(torch.load(buffer))
    x = torch.ones(1, 2)
    print(torch.equal(model(x), copy(x)))
    ''',
    "Sequential 안의 층은 번호로 이름이 붙습니다(`0.weight`, `2.bias`). ReLU처럼 가중치 없는 층은 state_dict에 나타나지 않습니다.",
    "가중치를 복사하세요.", "저장 전후를 비교하세요.",
    ["`state_dict()` = 이름 → 가중치 딕셔너리.", "`torch.save` / `torch.load`로 저장·불러오기.", "불러올 땐 같은 구조의 모델에 `load_state_dict`.",
     "가중치 없는 층은 state_dict에 없다."],
    [("state_dict를 모델에 넣는 메서드는?", ["`load_state_dict`", "`set_weights`", "`torch.load`", "`copy`"], 0),
     ("`nn.Sequential(nn.Linear(2, 3), nn.ReLU(), nn.Linear(3, 1))`의 state_dict 키 개수는?", ["2", "3", "4", "6"], 2)],
    [
        X("d155_fill_1", "가중치 복사",
          "시드가 다른 두 모델을 만들고, 두 번째 모델에 첫 번째 모델의 가중치를 넣은 뒤 `[state_dict 키 목록, 복사 후 출력이 같은지]`를 반환하세요.", ["state_dict"], 1,
          '''
          import torch
          from torch import nn


          def copy_weights(seed):
              torch.manual_seed(seed)
              a = nn.Linear(3, 2)
              b = nn.Linear(3, 2)
              b.load_state_dict(a.state_dict())
              x = torch.ones(1, 3)
              return [list(a.state_dict().keys()), torch.equal(a(x), b(x))]
          ''', "copy_weights", [[0], [5]],
          ["가중치를 넣는 메서드 이름입니다.", "가중치 딕셔너리를 꺼내는 메서드입니다."],
          blanks=["load_state_dict", "state_dict()"], tol=None),
        X("d155_code_1", "저장과 불러오기",
          "`torch.manual_seed(seed)` 후 `nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))`을 만들어 `io.BytesIO`에 state_dict를 저장하세요. "
          "`torch.manual_seed(seed + 1)` 후 같은 구조의 새 모델을 만들고, `x = torch.ones(1, 2)`에 대해 "
          "`[불러오기 전 출력이 같은지, 불러온 뒤 출력이 같은지, 저장된 텐서 원소 수 합계]`를 반환하세요.",
          ["state_dict"], 2,
          '''
          import io
          import torch
          from torch import nn


          def save_and_load(seed):
              make = lambda: nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1))
              torch.manual_seed(seed)
              model = make()
              buffer = io.BytesIO()
              torch.save(model.state_dict(), buffer)
              torch.manual_seed(seed + 1)
              other = make()
              x = torch.ones(1, 2)
              before = torch.equal(model(x), other(x))
              buffer.seek(0)
              state = torch.load(buffer)
              other.load_state_dict(state)
              after = torch.equal(model(x), other(x))
              return [before, after, sum(v.numel() for v in state.values())]
          ''', "save_and_load", [[0], [3]],
          ["저장 뒤 읽기 전에 `buffer.seek(0)`으로 처음으로 되돌려야 합니다.", "원소 수는 불러온 딕셔너리의 값마다 `numel()`을 더합니다."], tol=None),
    ], review_title="23주차 시작")

# ====================================================================== Day 156
day156 = D(
    156, "층 고정하기", W, ["transfer", "state_dict"],
    ["requires_grad를 꺼서 층을 고정(freeze)할 수 있다.", "학습 가능한 매개변수만 옵티마이저에 넘길 수 있다."],
    "어제는 가중치를 저장하고 불러왔습니다. 불러온 가중치를 **그대로 둔 채** 일부만 학습하려면 어떻게 할까요?",
    [("`torch.save`로 보통 저장하는 것은?", ["모델 클래스 코드", "`model.state_dict()`", "옵티마이저 코드", "손실 함수"], 1)],
    "얼려 두기",
    "매개변수의 `requires_grad`를 `False`로 바꾸면 기울기가 계산되지 않아 학습 중에도 값이 변하지 않습니다. 이것을 층을 **고정**(freeze)한다고 합니다.\n\n"
    "```\nfor p in model.features.parameters():\n    p.requires_grad = False\n```\n\n"
    "옵티마이저에는 `requires_grad`가 True인 매개변수만 넘기는 것이 깔끔합니다. 학습할 매개변수가 줄어 빠르고, 데이터가 적어도 과적합이 덜합니다.",
    '''
    import torch
    from torch import nn

    model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
    for p in model[0].parameters():
        p.requires_grad = False
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(trainable, total)
    print([name for name, p in model.named_parameters() if p.requires_grad])
    ''',
    "이번 주 실습 모델 `Net`은 특성 추출부 `features`(합성곱 블록)와 분류부 `fc`로 나뉘어 있어 `model.features`만 골라 고정하기 쉽습니다.",
    "층을 고정하세요.", "고정한 층이 정말 변하지 않는지 확인하세요.",
    ["`requires_grad = False` → 고정.", "옵티마이저에는 학습할 매개변수만.", "고정하면 빠르고 과적합이 줄어든다.",
     "특성 추출부/분류부를 나누면 고정이 쉽다."],
    [("고정된 매개변수의 특징은?", ["기울기가 계산되지 않는다", "0이 된다", "삭제된다", "두 배가 된다"], 0),
     ("학습 가능한 매개변수만 고르는 조건은?", ["`p.requires_grad`", "`p.grad is None`", "`p.numel() > 0`", "`p.is_leaf`"], 0)],
    [
        X("d156_fill_1", "고정과 개수",
          "`nn.Sequential(nn.Linear(n_in, 8), nn.ReLU(), nn.Linear(8, 2))`의 첫 층을 고정하고 `[학습 가능 수, 전체 수]`를 반환하세요.", ["transfer"], 1,
          '''
          from torch import nn


          def freeze_first(n_in):
              model = nn.Sequential(nn.Linear(n_in, 8), nn.ReLU(), nn.Linear(8, 2))
              for p in model[0].parameters():
                  p.requires_grad = False
              trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
              return [trainable, sum(p.numel() for p in model.parameters())]
          ''', "freeze_first", [[4], [10]],
          ["기울기 계산 여부를 정하는 속성에 False를 넣습니다.", "학습 가능한 것만 세는 조건입니다."],
          blanks=["requires_grad = False", "if p.requires_grad"], tol=None),
        X("d156_code_1", "고정 확인",
          "주어진 `Net`, `fit`, `few_shot`을 사용하세요. `torch.manual_seed(0)` 후 `Net(5)`를 만들고 `features`를 고정합니다. "
          "학습 전 `features`와 `fc`의 state_dict를 복사해 둔 뒤(`{k: v.clone() ...}`), `few_shot(seed, 10)`의 학습 데이터로 `fit(model, X, y, 20)` 하세요. "
          "`[학습 가능 매개변수 수, features가 그대로인지, fc가 바뀌었는지]`를 반환합니다.",
          ["transfer"], 2,
          BASE + '''

          def check_freeze(seed):
              torch.manual_seed(0)
              model = Net(5)
              for p in model.features.parameters():
                  p.requires_grad = False
              feat_before = {k: v.clone() for k, v in model.features.state_dict().items()}
              fc_before = {k: v.clone() for k, v in model.fc.state_dict().items()}
              X, y, _, _ = few_shot(seed, 10)
              fit(model, X, y, 20)
              same = all(torch.equal(v, model.features.state_dict()[k]) for k, v in feat_before.items())
              changed = any(not torch.equal(v, model.fc.state_dict()[k]) for k, v in fc_before.items())
              trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
              return [trainable, same, changed]
          ''', "check_freeze", [[0], [1]],
          ["`clone()`으로 복사해야 학습 뒤 값과 비교할 수 있습니다.", "`torch.equal`로 키마다 비교하고 `all`, `any`로 모으세요."], tol=None, tl=90),
    ])

# ====================================================================== Day 157
day157 = D(
    157, "특성 추출기 재사용", W, ["transfer", "cnn"],
    ["사전 학습된 특성 추출부를 고정하고 새 분류부만 학습할 수 있다.", "데이터가 적을 때 전이 학습이 유리함을 확인할 수 있다."],
    "어제는 층을 고정했습니다. 오늘은 **다른 과제에서 학습한** 특성 추출부를 가져와 새 과제에 씁니다.",
    [("고정할 층의 매개변수에 설정하는 값은?", ["`requires_grad = True`", "`requires_grad = False`", "`lr = 0`", "`eval()`"], 1)],
    "남의 지식 빌려 쓰기",
    "이번 주 실험 설정입니다.\n\n- **원래 과제**: 숫자 0~4 분류(데이터 충분). `pretrained()`가 이 과제로 학습된 `Net(5)`를 돌려줌\n"
    "- **새 과제**: 숫자 5~9 분류인데 숫자마다 학습 데이터가 몇 장뿐. `few_shot(seed, 장수)`가 학습·테스트 데이터를 돌려줌\n\n"
    "0~4에서 배운 \"선·곡선·모서리 감지\" 합성곱 필터가 5~9에도 쓸모 있으리라 기대하고 `features`는 고정해 재사용, 분류부 `fc`만 새로 만들어 학습합니다. "
    "실제로는 ImageNet으로 학습된 ResNet 같은 모델을 같은 방식으로 씁니다.",
    '''
    import torch
    from torch import nn

    class Net(nn.Module):
        def __init__(self, n_out):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(),
            )
            self.fc = nn.Linear(64, n_out)

        def forward(self, x):
            return self.fc(self.features(x))

    model = Net(5)
    for p in model.features.parameters():
        p.requires_grad = False
    model.fc = nn.Linear(64, 5)
    print([name for name, p in model.named_parameters() if p.requires_grad])
    ''',
    "실습 결과를 꼭 확인하세요. 이 작은 실험에서는 처음부터 학습한 모델이 비슷하거나 더 좋기도 합니다. 8×8 숫자는 단순해서 작은 CNN도 금방 배우고, 원래 과제 데이터도 900장 정도라 특성이 0~4에 치우쳐 있기 때문입니다. "
    "전이 학습의 효과는 원래 과제가 크고 다양할수록(ImageNet 120만 장 등), 새 과제가 어려울수록 커집니다. 대신 학습할 매개변수가 크게 줄어 빠르게 학습된다는 장점은 여기서도 확인할 수 있습니다.",
    "분류부를 새로 바꾸세요.", "처음부터 학습과 전이 학습을 비교하세요.",
    ["전이 학습 = 다른 과제에서 학습한 특성 추출부 재사용.", "특성 추출부 고정 + 새 분류부 학습.", "효과는 원래 과제가 크고 다양할수록 크다. 실험으로 확인할 것.",
     "실무에서는 ImageNet 사전 학습 모델을 같은 방식으로."],
    [("전이 학습에서 보통 새로 만드는 부분은?", ["특성 추출부", "마지막 분류 층", "입력 데이터", "손실 함수"], 1),
     ("전이 학습이 특히 유리한 상황은?", ["새 과제 데이터가 적을 때", "데이터가 무한할 때", "모델이 작을 때", "항상 불리"], 0)],
    [
        X("d157_fill_1", "새 분류부",
          "사전 학습 모델의 `features`를 고정하고 `fc`를 `n_out`개 출력의 새 선형 층으로 바꾼 뒤, 학습 가능한 매개변수 이름 목록을 반환하세요.", ["transfer"], 1,
          '''
          import torch
          from torch import nn
          ''' + NET_SRC + '''

          def new_head(n_out):
              model = Net(5)
              for p in model.features.parameters():
                  p.requires_grad = False
              model.fc = nn.Linear(64, n_out)
              return [name for name, p in model.named_parameters() if p.requires_grad]
          ''', "new_head", [[5], [3]],
          ["특성 추출부의 매개변수를 고정하는 속성입니다.", "펼친 특성 64개를 받는 새 선형 층을 `model.fc`에 넣습니다."],
          blanks=["requires_grad = False", "model.fc = nn.Linear(64, n_out)"], tol=None),
        X("d157_code_1", "처음부터 대 전이",
          "주어진 도구를 사용해 `few_shot(seed, per_class)` 데이터로 두 모델을 비교하세요. "
          "① 처음부터: `torch.manual_seed(1)` 후 `Net(5)`를 `fit(..., 40)`. "
          "② 전이: `pretrained()`의 `features`를 고정하고 `torch.manual_seed(1)` 후 `fc`를 `nn.Linear(64, 5)`로 바꿔 `fit(..., 40)`. "
          "`{\"scratch\": 테스트 정확도, \"transfer\": 테스트 정확도, \"trainable\": [처음부터 모델의 학습 가능 매개변수 수, 전이 모델의 수]}`(정확도는 소수 넷째 자리)를 반환하세요.",
          ["transfer", "cnn"], 3,
          BASE + '''

          def compare_transfer(seed, per_class):
              X_train, y_train, X_test, y_test = few_shot(seed, per_class)
              torch.manual_seed(1)
              scratch = Net(5)
              fit(scratch, X_train, y_train, 40)
              model = pretrained()
              for p in model.features.parameters():
                  p.requires_grad = False
              torch.manual_seed(1)
              model.fc = nn.Linear(64, 5)
              fit(model, X_train, y_train, 40)
              count = lambda m: sum(p.numel() for p in m.parameters() if p.requires_grad)
              return {
                  "scratch": round(accuracy(scratch, X_test, y_test), 4),
                  "transfer": round(accuracy(model, X_test, y_test), 4),
                  "trainable": [count(scratch), count(model)],
              }
          ''', "compare_transfer", [[0, 5], [1, 10]],
          ["두 모델 모두 같은 `fit` 함수로 학습합니다(고정된 매개변수는 `fit`이 알아서 뺍니다).", "`fc`를 바꾸기 직전에 시드를 1로 다시 고정해야 결과가 같습니다."],
          tol=3e-3, tl=120),
    ])

# ====================================================================== Day 158
day158 = D(
    158, "미세 조정", W, ["fine_tuning", "transfer", "optimizer"],
    ["고정을 풀고 전체 모델을 작은 학습률로 미세 조정할 수 있다.", "매개변수 그룹으로 층마다 다른 학습률을 줄 수 있다."],
    "어제는 특성 추출부를 고정하고 분류부만 학습했는데, 결과가 기대만큼 좋지는 않았습니다. 0~4에 맞춰진 특성을 새 과제에 맞게 **살짝 고치면** 어떨까요?",
    [("새로 만든 `nn.Linear`의 `requires_grad` 기본값은?", ["False", "True", "None", "0"], 1)],
    "살짝만 고치기",
    "**미세 조정**(fine-tuning)은 사전 학습된 가중치에서 출발해 전체(또는 일부)를 **작은 학습률**로 더 학습하는 것입니다. 큰 학습률을 쓰면 애써 배운 특성이 망가집니다.\n\n"
    "옵티마이저에 **매개변수 그룹**을 넘기면 부분마다 학습률을 다르게 줄 수 있습니다.\n\n"
    "```\noptim.Adam([\n    {\"params\": model.features.parameters(), \"lr\": 0.001},\n    {\"params\": model.fc.parameters(), \"lr\": 0.01},\n])\n```",
    '''
    import torch
    from torch import nn, optim

    model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
    optimizer = optim.Adam([
        {"params": model[0].parameters(), "lr": 0.001},
        {"params": model[2].parameters(), "lr": 0.01},
    ])
    for group in optimizer.param_groups:
        print(group["lr"], sum(p.numel() for p in group["params"]))
    ''',
    "흔한 순서: ① 분류부만 학습(추출부 고정) → ② 고정을 풀고 전체를 작은 학습률로 미세 조정.",
    "매개변수 그룹을 만드세요.", "고정 학습 뒤 미세 조정을 이어 하세요.",
    ["미세 조정 = 사전 학습 가중치에서 작은 학습률로 추가 학습.", "큰 학습률은 배운 특성을 망가뜨린다.",
     "매개변수 그룹으로 부분별 학습률.", "분류부 먼저, 그다음 전체."],
    [("미세 조정에서 사전 학습된 층에 주는 학습률은?", ["더 크게", "더 작게", "0", "무작위"], 1),
     ("옵티마이저의 그룹별 학습률을 확인하는 곳은?", ["`optimizer.param_groups`", "`model.lr`", "`optimizer.state_dict`만", "`scheduler`"], 0)],
    [
        X("d158_fill_1", "매개변수 그룹",
          "Sequential 모델의 첫 층은 `lr_body`, 마지막 층은 `lr_head`인 Adam을 만들고 그룹마다 `[학습률, 매개변수 수]`를 반환하세요.", ["fine_tuning", "optimizer"], 1,
          '''
          from torch import nn, optim


          def groups(lr_body, lr_head):
              model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
              optimizer = optim.Adam([
                  {"params": model[0].parameters(), "lr": lr_body},
                  {"params": model[2].parameters(), "lr": lr_head},
              ])
              return [[g["lr"], sum(p.numel() for p in g["params"])] for g in optimizer.param_groups]
          ''', "groups", [[0.001, 0.01], [0.0005, 0.1]],
          ["각 그룹은 \"params\"와 \"lr\" 키를 가진 딕셔너리입니다.", "옵티마이저가 가진 그룹 목록 속성입니다."],
          blanks=['"params": model[0].parameters()', "param_groups"], tol=1e-9),
        X("d158_code_1", "두 단계 학습",
          "`few_shot(seed, 10)` 데이터로 ① `pretrained()`의 `features`를 고정하고 `torch.manual_seed(1)` 후 `fc`를 `nn.Linear(64, 5)`로 바꿔 `fit(..., 30)`. "
          "이때 테스트 정확도를 기록합니다. ② 고정을 풀고(`requires_grad = True`) Adam 그룹(`features` lr 0.001, `fc` lr 0.005)으로 전체 배치를 30번 더 학습합니다. "
          "`{\"frozen\": ①의 정확도, \"finetuned\": ②의 정확도}`(소수 넷째 자리)를 반환하세요.",
          ["fine_tuning", "transfer"], 3,
          BASE + '''

          def two_stage(seed):
              X_train, y_train, X_test, y_test = few_shot(seed, 10)
              model = pretrained()
              for p in model.features.parameters():
                  p.requires_grad = False
              torch.manual_seed(1)
              model.fc = nn.Linear(64, 5)
              fit(model, X_train, y_train, 30)
              frozen = accuracy(model, X_test, y_test)
              for p in model.features.parameters():
                  p.requires_grad = True
              optimizer = optim.Adam([
                  {"params": model.features.parameters(), "lr": 0.001},
                  {"params": model.fc.parameters(), "lr": 0.005},
              ])
              for _ in range(30):
                  loss = nn.CrossEntropyLoss()(model(X_train), y_train)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              return {"frozen": round(frozen, 4), "finetuned": round(accuracy(model, X_test, y_test), 4)}
          ''', "two_stage", [[0], [2]],
          ["①은 어제 문제와 같습니다.", "②는 주어진 `fit` 대신 매개변수 그룹 옵티마이저로 학습 루프를 직접 씁니다."], tol=3e-3, tl=120),
    ])

# ====================================================================== Day 159
AUG_SRC = '''

          def augment(x, g):
              shifts = torch.randint(-1, 2, (len(x), 2), generator=g).tolist()
              moved = torch.stack([torch.roll(img, shifts=s, dims=(1, 2)) for img, s in zip(x, shifts)])
              return moved + 0.05 * torch.randn(moved.shape, generator=g)
'''
day159 = D(
    159, "데이터 증강", W, ["augmentation", "overfitting"],
    ["이동·잡음 같은 증강으로 학습 데이터를 늘릴 수 있다.", "과제에 맞지 않는 증강(예: 숫자 좌우 반전)을 구분할 수 있다."],
    "어제는 미세 조정을 했습니다. 데이터가 적을 때 쓸 수 있는 또 다른 방법은 데이터를 **조금씩 바꿔서 늘리는 것**입니다.",
    [("미세 조정할 때 사전 학습된 층의 학습률은?", ["크게", "작게", "0", "분류부와 같게"], 1)],
    "조금씩 바꿔 보여 주기",
    "**데이터 증강**은 학습할 때마다 이미지를 무작위로 살짝 바꿔(이동, 회전, 잡음, 밝기 등) 모델이 사소한 차이에 흔들리지 않게 합니다. 테스트 데이터는 바꾸지 않습니다.\n\n"
    "- `torch.roll(x, shifts, dims)`: 텐서를 밀기(끝은 반대쪽으로 넘어옴)\n- `x + 0.05 * torch.randn(...)`: 약한 잡음\n- `torch.flip(x, dims=(3,))`: 좌우 반전\n\n"
    "증강은 정답이 바뀌지 않는 범위에서만 써야 합니다. 고양이 사진은 좌우 반전해도 고양이지만, 숫자 \"2\"를 뒤집으면 더 이상 2가 아닙니다.",
    '''
    import torch

    x = torch.arange(9, dtype=torch.float32).reshape(1, 1, 3, 3)
    print(torch.roll(x, shifts=(0, 1), dims=(2, 3))[0, 0])
    print(torch.flip(x, dims=(3,))[0, 0])
    g = torch.Generator().manual_seed(0)
    print(torch.randint(-1, 2, (2,), generator=g).tolist())
    ''',
    "증강은 **테스트에서 만날 변화**에 대비하는 것입니다. 오늘 실습에서 원래 테스트 정확도는 비슷하지만, 이미지가 1칸만 어긋나도 증강 없이 학습한 모델은 크게 무너집니다. "
    "실무에서는 `torchvision.transforms`의 RandomCrop, RandomRotation 등을 씁니다.",
    "이미지를 밀어 보세요.", "증강 유무를 비교하세요.",
    ["증강 = 정답이 그대로인 범위의 무작위 변형.", "학습 때만 적용, 테스트는 그대로. 효과는 변화된 입력에 대한 견고함.", "`torch.roll`, 잡음, `torch.flip`.",
     "과제에 맞지 않는 증강은 오히려 해롭다."],
    [("데이터 증강을 적용하는 데이터는?", ["학습 데이터", "테스트 데이터", "둘 다", "검증 데이터만"], 0),
     ("손글씨 숫자에 부적절한 증강은?", ["1칸 이동", "약한 잡음", "좌우 반전", "약간의 밝기 변화"], 2)],
    [
        X("d159_fill_1", "이미지 밀기",
          "2차원 목록 이미지를 (1, 1, H, W)로 바꾸고 `torch.roll`로 아래로 `dy`, 오른쪽으로 `dx`만큼 민 2차원 결과를 반환하세요.", ["augmentation"], 1,
          '''
          import torch


          def shift(image, dy, dx):
              x = torch.tensor(image, dtype=torch.float32).reshape(1, 1, len(image), -1)
              return torch.roll(x, shifts=(dy, dx), dims=(2, 3))[0, 0]
          ''', "shift", [[[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 0, 1], [[[1, 2], [3, 4]], 1, 0], [[[1, 2, 3], [4, 5, 6]], -1, -1]],
          ["텐서를 미는 함수 이름입니다.", "높이·너비는 (N, C, H, W)의 2, 3번 차원입니다."], blanks=["roll", "dims=(2, 3)"]),
        X("d159_code_1", "증강 효과",
          "주어진 `augment(x, g)`(이미지마다 -1~1칸 무작위 이동 + 약한 잡음)를 사용하세요. `few_shot(seed, 10)` 데이터로 처음부터 `Net(5)`를 두 번 학습합니다"
          "(각각 `torch.manual_seed(1)` 후 모델 생성, `optim.Adam(lr=0.01)`, `g = torch.Generator().manual_seed(0)`, 전체 배치 100번). "
          "증강 버전은 매 스텝 `augment(X_train, g)`를 입력으로 씁니다. 평가는 원래 테스트 이미지와, 모두 아래·오른쪽으로 1칸 민 이미지(`torch.roll(X_test, shifts=(1, 1), dims=(2, 3))`) 두 가지로 합니다. "
          "`{\"plain\": [원래 정확도, 이동 정확도], \"augmented\": [...]}`(소수 넷째 자리)를 반환하세요.",
          ["augmentation", "training_loop"], 3,
          BASE + AUG_SRC + '''

          def compare_augment(seed):
              X_train, y_train, X_test, y_test = few_shot(seed, 10)
              X_moved = torch.roll(X_test, shifts=(1, 1), dims=(2, 3))
              results = {}
              for name in ["plain", "augmented"]:
                  torch.manual_seed(1)
                  model = Net(5)
                  optimizer = optim.Adam(model.parameters(), lr=0.01)
                  g = torch.Generator().manual_seed(0)
                  for _ in range(100):
                      inputs = augment(X_train, g) if name == "augmented" else X_train
                      loss = nn.CrossEntropyLoss()(model(inputs), y_train)
                      optimizer.zero_grad()
                      loss.backward()
                      optimizer.step()
                  results[name] = [round(accuracy(model, X_test, y_test), 4), round(accuracy(model, X_moved, y_test), 4)]
              return results
          ''', "compare_augment", [[0], [1]],
          ["두 버전은 학습 입력만 다르고 나머지는 같습니다.", "정확도는 원래 테스트와 이동한 테스트에 각각 `accuracy`를 부르면 됩니다."], tol=3e-3, tl=120),
    ])

# ====================================================================== Day 160
day160 = D(
    160, "조기 종료와 체크포인트", W, ["early_stopping", "state_dict", "overfitting"],
    ["검증 손실이 나아지지 않으면 학습을 멈출 수 있다.", "가장 좋았던 시점의 가중치를 저장했다가 되돌릴 수 있다."],
    "어제는 증강으로 과적합을 줄였습니다. 학습을 **언제 멈출지**도 과적합을 막는 중요한 방법입니다.",
    [("데이터 증강을 테스트 데이터에도 적용하나?", ["예", "아니요", "가끔", "항상 두 배로"], 1)],
    "제때 멈추기",
    "학습을 오래 하면 학습 손실은 계속 줄지만 **검증 손실**은 어느 순간부터 다시 커집니다(과적합). **조기 종료**는 검증 손실이 `patience` 에폭 연속으로 "
    "최저 기록을 깨지 못하면 멈춥니다.\n\n그리고 최저 기록일 때의 가중치를 `copy.deepcopy(model.state_dict())`로 저장해 두었다가(**체크포인트**), "
    "끝나면 `load_state_dict`로 되돌립니다. 파일로 저장하면 학습이 중간에 끊겨도 이어서 할 수 있습니다.",
    '''
    losses = [0.9, 0.7, 0.6, 0.62, 0.61, 0.65, 0.58, 0.6]
    best, best_epoch, wait, patience = float("inf"), -1, 0, 2
    for epoch, loss in enumerate(losses):
        if loss < best:
            best, best_epoch, wait = loss, epoch, 0
        else:
            wait += 1
            if wait >= patience:
                print("멈춤:", epoch)
                break
    print("최고:", best_epoch, best)
    ''',
    "`state_dict()`는 실제 가중치와 연결된 딕셔너리라서 그냥 저장하면 학습하면서 함께 바뀝니다. 반드시 `copy.deepcopy`로 복사하세요.",
    "조기 종료 규칙을 완성하세요.", "체크포인트로 최고 시점을 되돌리세요.",
    ["검증 손실이 나아지지 않으면 멈춘다.", "patience = 기다려 줄 에폭 수.", "최고 시점 가중치를 `deepcopy`로 저장.",
     "끝나면 `load_state_dict`로 복원."],
    [("조기 종료가 보는 지표는?", ["학습 손실", "검증 손실", "학습률", "에폭 수"], 1),
     ("`state_dict()`를 저장할 때 `deepcopy`가 필요한 이유는?", ["그냥 두면 학습하며 함께 바뀌어서", "속도 때문에", "파일 크기 때문에", "필요 없다"], 0)],
    [
        X("d160_fill_1", "멈출 시점",
          "검증 손실 목록과 patience로 조기 종료를 흉내 내 `[멈춘 에폭(끝까지 가면 None), 최고 에폭]`을 반환하세요.", ["early_stopping"], 1,
          '''
          def early_stop(losses, patience):
              best, best_epoch, wait = float("inf"), -1, 0
              for epoch, loss in enumerate(losses):
                  if loss < best:
                      best, best_epoch, wait = loss, epoch, 0
                  else:
                      wait += 1
                      if wait >= patience:
                          return [epoch, best_epoch]
              return [None, best_epoch]
          ''', "early_stop", [[[0.9, 0.7, 0.6, 0.62, 0.61, 0.65], 2], [[1.0, 0.8, 0.9, 0.7, 0.75], 2], [[3, 2, 1], 1]],
          ["더 좋아지면 기다린 횟수를 0으로 되돌립니다.", "기다린 횟수가 patience에 닿으면 멈춥니다."],
          blanks=["wait = loss, epoch, 0", "wait >= patience"], tol=None),
        X("d160_code_1", "체크포인트 복원",
          "`few_shot(seed, 10)`의 학습 데이터 50개 중 번호가 5의 배수인 10개(`torch.arange(len(y)) % 5 == 0`)는 검증, 나머지 40개는 학습에 씁니다. `torch.manual_seed(1)` 후 `Net(5)`와 `optim.Adam(lr=0.01)`로 "
          "전체 배치를 최대 100 에폭 학습하며, 에폭마다 검증 손실(`torch.no_grad()`)이 최저면 `copy.deepcopy(model.state_dict())`로 저장하고, "
          "patience 5로 조기 종료하세요. 끝나면 최고 가중치를 되돌리고 `[최고 에폭, 멈춘 에폭(끝까지면 99), 테스트 정확도]`를 반환합니다.",
          ["early_stopping", "state_dict"], 3,
          '''
          import copy''' + BASE + '''

          def train_with_checkpoint(seed):
              X, y, X_test, y_test = few_shot(seed, 10)
              val = torch.arange(len(y)) % 5 == 0
              X_tr, y_tr, X_val, y_val = X[~val], y[~val], X[val], y[val]
              torch.manual_seed(1)
              model = Net(5)
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              best, best_epoch, best_state, wait = float("inf"), -1, None, 0
              for epoch in range(100):
                  loss = nn.CrossEntropyLoss()(model(X_tr), y_tr)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
                  with torch.no_grad():
                      val_loss = nn.CrossEntropyLoss()(model(X_val), y_val).item()
                  if val_loss < best:
                      best, best_epoch, wait = val_loss, epoch, 0
                      best_state = copy.deepcopy(model.state_dict())
                  else:
                      wait += 1
                      if wait >= 5:
                          break
              model.load_state_dict(best_state)
              return [best_epoch, epoch, round(accuracy(model, X_test, y_test), 4)]
          ''', "train_with_checkpoint", [[0], [3]],
          ["bool 마스크와 `~`(반대)로 검증·학습을 나눌 수 있습니다. 숫자마다 2장씩 검증에 들어갑니다.",
           "멈춘 뒤 저장해 둔 최고 가중치를 모델에 다시 넣은 다음 정확도를 구합니다."],
          tol=3e-3, tl=90),
    ])

# ====================================================================== Day 161 (review)
day161 = D(
    161, "23주차 누적 복습", W, ["transfer", "state_dict", "fine_tuning", "early_stopping", "augmentation"],
    ["사전 학습 모델을 저장·불러오기·고정·교체해 새 과제에 적용하는 전 과정을 수행할 수 있다."],
    "| 날 | 주제 | 핵심 |\n|---|---|---|\n| 155 | 저장 | `state_dict`, `torch.save`, `load_state_dict` |\n| 156 | 고정 | `requires_grad = False` |\n"
    "| 157 | 특성 재사용 | 추출부 고정 + 새 분류부 |\n| 158 | 미세 조정 | 작은 학습률, 매개변수 그룹 |\n| 159 | 증강 | roll, 잡음, 과제에 맞는 변형 |\n"
    "| 160 | 조기 종료 | patience, deepcopy 체크포인트 |",
    [("전이 학습에서 사전 학습 모델을 불러오는 메서드는?", ["`load_state_dict`", "`fit`", "`freeze`", "`deepcopy`"], 0),
     ("학습 데이터가 매우 적을 때 먼저 시도할 방법은?", ["추출부 고정 + 분류부만 학습", "모든 층 큰 학습률", "층 더 쌓기", "증강 금지"], 0)],
    "추출부를 특징 생성기로",
    "고정한 특성 추출부는 이미지를 64개 숫자로 바꾸는 \"특징 생성기\"이기도 합니다. 이 특징을 3단계에서 배운 scikit-learn 모델에 넣을 수도 있습니다(도전 문제).\n\n"
    "`with torch.no_grad(): feats = model.features(X).numpy()`처럼 NumPy 배열로 꺼내면 됩니다.",
    '''
    import torch
    from torch import nn

    features = nn.Sequential(nn.Conv2d(1, 4, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten())
    with torch.no_grad():
        feats = features(torch.zeros(3, 1, 8, 8)).numpy()
    print(type(feats).__name__, feats.shape)
    ''',
    None,
    "학습 가능한 층 이름을 확인하세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["저장 → 불러오기 → 고정 → 분류부 교체 → 학습.", "필요하면 작은 학습률로 미세 조정.", "증강·조기 종료로 과적합 방지.",
     "다음 주: 4단계 종합 프로젝트."],
    [("특성 추출부 출력을 scikit-learn에 넣으려면?", ["`.numpy()`로 변환", "그대로", "`.item()`", "`state_dict()`"], 0),
     ("고정한 층에도 해야 하는 것은?", ["평가 때 `eval()` 호출", "학습률 키우기", "`requires_grad = True`", "삭제"], 0)],
    [
        X("d161_fill_1", "학습할 층",
          "Net의 `features` 중 **마지막 합성곱 층**(`features[3]`)만 고정을 풀고 나머지 features는 고정했을 때 학습 가능한 매개변수 이름 목록을 반환하세요.", ["transfer"], 1,
          '''
          import torch
          from torch import nn
          ''' + NET_SRC + '''

          def trainable_names():
              model = Net(5)
              for p in model.features.parameters():
                  p.requires_grad = False
              for p in model.features[3].parameters():
                  p.requires_grad = True
              return [name for name, p in model.named_parameters() if p.requires_grad]
          ''', "trainable_names", [[]],
          ["먼저 features 전체를 False로 바꿉니다.", "그다음 `features[3]`만 다시 True로 바꿉니다."],
          blanks=["requires_grad = False", "features[3]"], tol=None),
        X("d161_code_1", "전이 학습 전 과정",
          "① `pretrained()`의 state_dict를 `io.BytesIO`에 저장 ② `torch.manual_seed(2)` 후 새 `Net(5)`를 만들어 불러오기 ③ `features` 고정 "
          "④ `torch.manual_seed(1)` 후 `fc`를 `nn.Linear(64, 5)`로 교체 ⑤ `few_shot(seed, per_class)` 학습 데이터로 `fit(..., 40)`. "
          "`[학습 가능 매개변수 수, 테스트 정확도(소수 넷째 자리)]`를 반환하세요.",
          ["transfer", "state_dict"], 3,
          '''
          import io''' + BASE + '''

          def transfer_pipeline(seed, per_class):
              buffer = io.BytesIO()
              torch.save(pretrained().state_dict(), buffer)
              buffer.seek(0)
              torch.manual_seed(2)
              model = Net(5)
              model.load_state_dict(torch.load(buffer))
              for p in model.features.parameters():
                  p.requires_grad = False
              torch.manual_seed(1)
              model.fc = nn.Linear(64, 5)
              X_train, y_train, X_test, y_test = few_shot(seed, per_class)
              fit(model, X_train, y_train, 40)
              trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
              return [trainable, round(accuracy(model, X_test, y_test), 4)]
          ''', "transfer_pipeline", [[0, 5], [1, 3]],
          ["저장 뒤 `buffer.seek(0)`을 잊지 마세요.", "단계 순서와 시드 위치를 문제 그대로 지켜야 같은 결과가 나옵니다."], tol=3e-3, tl=120),
        X("d161_code_2", "특징 + 로지스틱 회귀(도전)",
          "`few_shot(seed, 10)` 데이터에서 ① 원본 픽셀 64개, ② `pretrained().features`가 만든 특징 64개를 각각 `LogisticRegression(max_iter=1000)`으로 학습해 "
          "`{\"pixels\": 테스트 정확도, \"features\": 테스트 정확도}`(소수 넷째 자리)를 반환하세요. 특징은 `eval()`과 `torch.no_grad()` 안에서 만들고 `.numpy()`로 바꿉니다.",
          ["transfer", "logistic_regression"], 3,
          '''
          from sklearn.linear_model import LogisticRegression''' + BASE + '''

          def features_vs_pixels(seed):
              X_train, y_train, X_test, y_test = few_shot(seed, 10)
              model = pretrained()
              model.eval()
              with torch.no_grad():
                  f_train, f_test = model.features(X_train).numpy(), model.features(X_test).numpy()
              results = {}
              for name, (A, B) in {"pixels": (X_train.flatten(1).numpy(), X_test.flatten(1).numpy()),
                                   "features": (f_train, f_test)}.items():
                  clf = LogisticRegression(max_iter=1000).fit(A, y_train.numpy())
                  results[name] = round(clf.score(B, y_test.numpy()), 4)
              return results
          ''', "features_vs_pixels", [[0], [1]],
          ["원본 픽셀은 `X.flatten(1).numpy()`로 (N, 64) 배열이 됩니다.", "두 경우 모두 같은 분류기 설정으로 학습·평가합니다."],
          tol=3e-3, tl=120, required=False),
    ], review_title="23주차 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day155, day156, day157, day158, day159, day160, day161])
