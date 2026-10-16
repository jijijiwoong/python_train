"""Week 21 (Day 141-147): 합성곱 신경망(CNN)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, c, write_lessons  # noqa: E402

W = 21
CLS = {"required_syntax": ["class"]}

DIGITS_IMPORTS = '''
          import torch
          from sklearn.datasets import load_digits
          from sklearn.model_selection import train_test_split
          from torch import nn, optim
          from torch.utils.data import DataLoader, TensorDataset
'''
DIGITS_SRC = '''

          def digit_loaders(seed):
              digits = load_digits()
              X_train, X_test, y_train, y_test = train_test_split(
                  digits.images, digits.target, test_size=0.3, random_state=seed, stratify=digits.target)
              to_x = lambda a: torch.tensor(a, dtype=torch.float32).unsqueeze(1) / 16
              train = TensorDataset(to_x(X_train), torch.tensor(y_train))
              test = TensorDataset(to_x(X_test), torch.tensor(y_test))
              g = torch.Generator().manual_seed(0)
              return DataLoader(train, batch_size=64, shuffle=True, generator=g), DataLoader(test, batch_size=256)
'''
CNN_SRC = '''

          class SmallCNN(nn.Module):
              def __init__(self):
                  super().__init__()
                  self.conv1 = nn.Conv2d(1, 8, 3, padding=1)
                  self.conv2 = nn.Conv2d(8, 16, 3, padding=1)
                  self.pool = nn.MaxPool2d(2)
                  self.fc = nn.Linear(16 * 2 * 2, 10)

              def forward(self, x):
                  x = self.pool(torch.relu(self.conv1(x)))
                  x = self.pool(torch.relu(self.conv2(x)))
                  return self.fc(x.flatten(1))
'''

# ====================================================================== Day 141
day141 = D(
    141, "이미지 데이터와 텐서", W, ["image_tensor", "tensor_shape"],
    ["이미지를 (개수, 채널, 높이, 너비) 텐서로 표현할 수 있다.", "픽셀 값을 0~1로 정규화할 수 있다."],
    "이번 주는 이미지를 다루는 **합성곱 신경망**(CNN)을 배웁니다. 지난주까지 쓴 학습 루프는 그대로 쓰고 모델만 바뀝니다.",
    [("`unsqueeze(1)`을 (5, 8, 8) 텐서에 적용하면?", ["(1, 5, 8, 8)", "(5, 1, 8, 8)", "(5, 8, 1, 8)", "(5, 8, 8, 1)"], 1)],
    "이미지는 숫자 격자",
    "흑백 이미지는 밝기 숫자의 2차원 격자이고, 컬러 이미지는 빨강·초록·파랑 3장(채널)입니다. PyTorch는 이미지 묶음을 **(N, C, H, W)** 모양으로 다룹니다. "
    "N은 개수, C는 채널, H·W는 높이·너비입니다.\n\n"
    "scikit-learn의 `load_digits()`는 8×8 손글씨 숫자 1,797장(밝기 0~16)입니다. 인터넷 없이 바로 쓸 수 있어 이번 주 내내 사용합니다.",
    '''
    import torch
    from sklearn.datasets import load_digits

    digits = load_digits()
    print(digits.images.shape, digits.target[:10])
    X = torch.tensor(digits.images, dtype=torch.float32).unsqueeze(1) / 16
    print(X.shape, X.min().item(), X.max().item())
    for row in digits.images[0]:
        print("".join("#" if v > 8 else "." for v in row))
    ''',
    "값을 0~1로 나누어 주면(정규화) 학습이 안정적입니다. 일반 사진은 0~255라서 255로 나눕니다.",
    "이미지 텐서로 바꾸세요.", "숫자별 평균 이미지를 분석하세요.",
    ["이미지 묶음 = (N, C, H, W).", "흑백은 C = 1, 컬러는 C = 3.", "픽셀을 0~1로 정규화.", "digits: 8×8 손글씨 숫자, 값 0~16."],
    [("컬러 사진 32장(64×64)의 텐서 모양은?", ["(32, 64, 64, 3)", "(32, 3, 64, 64)", "(3, 32, 64, 64)", "(64, 64, 3, 32)"], 1),
     ("digits 픽셀의 최댓값은?", ["1", "16", "255", "8"], 1)],
    [
        X("d141_fill_1", "이미지 텐서",
          "digits 앞 `n`장을 (N, 1, 8, 8) 텐서로 바꾸고 16으로 나누어 `[모양 리스트, 최댓값]`을 반환하세요.", ["image_tensor"], 1,
          '''
          import torch
          from sklearn.datasets import load_digits


          def to_images(n):
              images = load_digits().images[:n]
              x = torch.tensor(images, dtype=torch.float32).unsqueeze(1) / 16
              return [list(x.shape), x.max().item()]
          ''', "to_images", [[5], [100]],
          ["채널 차원을 1번 위치에 추가하는 메서드입니다.", "digits의 최대 밝기로 나눕니다."], blanks=["unsqueeze(1)", "16"]),
        X("d141_code_1", "평균 이미지",
          "digits에서 숫자 `digit`인 이미지만 골라 `[장수, 평균 이미지의 전체 평균(소수 넷째 자리), 평균 이미지에서 가장 밝은 칸의 (행, 열)]`을 반환하세요. "
          "픽셀은 원래 값(0~16) 그대로 씁니다.",
          ["image_tensor", "tensor_ops"], 2,
          '''
          import torch
          from sklearn.datasets import load_digits


          def digit_profile(digit):
              digits = load_digits()
              images = torch.tensor(digits.images, dtype=torch.float32)
              chosen = images[torch.tensor(digits.target) == digit]
              mean_img = chosen.mean(dim=0)
              idx = mean_img.argmax().item()
              return [len(chosen), round(mean_img.mean().item(), 4), [idx // 8, idx % 8]]
          ''', "digit_profile", [[0], [1], [7]],
          ["정답 텐서와 비교한 bool 텐서로 이미지를 고를 수 있습니다.", "`argmax()`는 펼친 위치이므로 `// 8`, `% 8`로 행·열을 구합니다."]),
    ], review_title="21주차 시작")

# ====================================================================== Day 142
day142 = D(
    142, "합성곱 연산", W, ["conv", "image_tensor"],
    ["커널이 이미지 위를 움직이며 계산하는 합성곱을 설명할 수 있다.", "kernel_size, stride, padding에 따른 출력 크기를 구할 수 있다."],
    "어제는 이미지를 (N, C, H, W) 텐서로 만들었습니다.",
    [("흑백 이미지 10장(8×8)의 텐서 모양은?", ["(10, 8, 8)", "(10, 1, 8, 8)", "(1, 10, 8, 8)", "(8, 8, 10)"], 1)],
    "작은 창으로 훑기",
    "**합성곱**은 작은 가중치 격자(**커널**, 필터)를 이미지 위에서 한 칸씩 옮기며, 겹친 부분끼리 곱해 더한 값을 출력합니다. "
    "같은 커널을 모든 위치에 쓰므로 \"어디에 있든 같은 무늬\"를 찾을 수 있고, 가중치 수도 적습니다.\n\n"
    "출력 크기 = (H + 2 × padding - kernel) ÷ stride + 1 (나눗셈은 버림)\n\n"
    "`nn.Conv2d(입력 채널, 출력 채널, kernel_size, stride=1, padding=0)`. 출력 채널 수만큼 서로 다른 커널을 학습합니다.",
    '''
    import torch
    import torch.nn.functional as F
    from torch import nn

    image = torch.tensor([[0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1]], dtype=torch.float32)
    edge = torch.tensor([[-1, 1], [-1, 1]], dtype=torch.float32)
    print(F.conv2d(image.reshape(1, 1, 4, 4), edge.reshape(1, 1, 2, 2))[0, 0])

    conv = nn.Conv2d(1, 6, kernel_size=3, padding=1)
    print(conv.weight.shape, conv(torch.zeros(2, 1, 8, 8)).shape)
    ''',
    "위 커널은 왼쪽이 어둡고 오른쪽이 밝은 **세로 경계**에서만 큰 값을 냅니다. CNN은 이런 커널을 손으로 정하지 않고 학습으로 찾습니다.",
    "합성곱 층의 출력 모양을 구하세요.", "커널을 직접 적용하세요.",
    ["합성곱 = 커널을 옮기며 곱해서 더하기.", "같은 커널을 모든 위치에 공유.", "출력 = (H + 2p - k) // s + 1.",
     "`nn.Conv2d(in, out, k, stride, padding)`."],
    [("8×8 입력, kernel 3, padding 0, stride 1의 출력 크기는?", ["8", "6", "5", "3"], 1),
     ("8×8 입력, kernel 3, padding 1의 출력 크기는?", ["8", "6", "10", "4"], 0)],
    [
        X("d142_fill_1", "출력 모양",
          "크기 h×h 흑백 이미지 1장에 `nn.Conv2d(1, 4, k, stride=s, padding=p)`를 적용한 출력 모양을 리스트로 반환하세요.", ["conv"], 1,
          '''
          import torch
          from torch import nn


          def conv_shape(h, k, s, p):
              conv = nn.Conv2d(1, 4, k, stride=s, padding=p)
              return list(conv(torch.zeros(1, 1, h, h)).shape)
          ''', "conv_shape", [[8, 3, 1, 0], [8, 3, 1, 1], [28, 5, 2, 2], [7, 2, 2, 0]],
          ["2차원 합성곱 층 클래스 이름입니다.", "가장자리를 채우는 옵션을 인자 p로 지정합니다."],
          blanks=["Conv2d", "padding=p"], tol=None),
        X("d142_code_1", "커널 적용",
          "2차원 목록 `image`와 `kernel`을 `F.conv2d`로 합성곱(stride 1, padding 0)한 2차원 결과를 반환하세요. 두 텐서 모두 (1, 1, 높이, 너비) 모양으로 바꿔야 합니다.",
          ["conv"], 2,
          '''
          import torch
          import torch.nn.functional as F


          def apply_kernel(image, kernel):
              x = torch.tensor(image, dtype=torch.float32)
              k = torch.tensor(kernel, dtype=torch.float32)
              out = F.conv2d(x.reshape(1, 1, *x.shape), k.reshape(1, 1, *k.shape))
              return out[0, 0]
          ''', "apply_kernel",
          [[[[0, 0, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1]], [[-1, 1], [-1, 1]]],
           [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0], [0, -1]]],
           [[[1, 1, 1, 1], [0, 0, 0, 0], [1, 1, 1, 1]], [[1], [-1]]]],
          ["`x.reshape(1, 1, *x.shape)`처럼 앞에 개수·채널 차원을 붙이세요.", "결과의 `[0, 0]`이 2차원 특성 맵입니다."]),
    ])

# ====================================================================== Day 143
day143 = D(
    143, "풀링과 특성 맵", W, ["pooling", "conv"],
    ["최대 풀링으로 특성 맵 크기를 줄일 수 있다.", "합성곱·풀링을 거친 뒤의 모양을 계산해 선형 층 입력 크기를 정할 수 있다."],
    "어제는 합성곱의 출력 크기를 계산했습니다.",
    [("합성곱 층의 출력 채널 수가 뜻하는 것은?", ["커널(필터)의 개수", "이미지 개수", "패딩 크기", "stride"], 0)],
    "줄이고 펼치기",
    "**최대 풀링** `nn.MaxPool2d(2)`는 2×2 칸마다 가장 큰 값만 남겨 높이·너비를 절반으로 줄입니다. 계산량이 줄고, 위치가 조금 달라져도 같은 결과가 나옵니다.\n\n"
    "CNN은 보통 [합성곱 → ReLU → 풀링]을 몇 번 반복해 **특성 맵**을 만들고, `flatten(1)`으로 (N, C×H×W)로 펼쳐 선형 층에 넣습니다. "
    "선형 층의 입력 수는 이 펼친 크기여야 합니다.",
    '''
    import torch
    from torch import nn

    x = torch.tensor([[1, 3, 2, 0], [4, 2, 1, 1], [0, 1, 5, 6], [2, 2, 7, 8]], dtype=torch.float32)
    print(nn.MaxPool2d(2)(x.reshape(1, 1, 4, 4))[0, 0])

    images = torch.zeros(5, 1, 8, 8)
    h = nn.MaxPool2d(2)(torch.relu(nn.Conv2d(1, 8, 3, padding=1)(images)))
    print(h.shape, h.flatten(1).shape)
    ''',
    "모양 계산이 헷갈리면 가짜 입력 `torch.zeros(1, 1, 8, 8)`을 층에 통과시켜 `shape`을 출력해 보는 것이 가장 확실합니다.",
    "최대 풀링을 적용하세요.", "층마다 특성 맵 모양을 기록하세요.",
    ["MaxPool2d(2): 2×2마다 최댓값, 크기 절반.", "[합성곱 → ReLU → 풀링] 반복.", "`flatten(1)`로 (N, C×H×W).",
     "선형 층 입력 수 = 펼친 크기."],
    [("(4, 16, 8, 8)에 MaxPool2d(2)를 적용하면?", ["(4, 16, 4, 4)", "(4, 8, 8, 8)", "(2, 16, 8, 8)", "(4, 16, 16, 16)"], 0),
     ("(4, 16, 2, 2)를 `flatten(1)` 하면?", ["(4, 64)", "(64,)", "(4, 16)", "(256,)"], 0)],
    [
        X("d143_fill_1", "최대 풀링",
          "2차원 목록 이미지에 2×2 최대 풀링을 적용한 2차원 결과를 반환하세요.", ["pooling"], 1,
          '''
          import torch
          from torch import nn


          def max_pool(image):
              x = torch.tensor(image, dtype=torch.float32).reshape(1, 1, len(image), -1)
              return nn.MaxPool2d(2)(x)[0, 0]
          ''', "max_pool", [[[[1, 3, 2, 0], [4, 2, 1, 1], [0, 1, 5, 6], [2, 2, 7, 8]]], [[[1, 2], [3, 4]]]],
          ["최대 풀링 층 클래스 이름입니다.", "(개수, 채널, 높이, 너비) 순서로 앞 두 차원을 1로 만듭니다."],
          blanks=["MaxPool2d", "reshape(1, 1"]),
        X("d143_code_1", "특성 맵 추적",
          "`torch.zeros(1, 1, h, h)`를 `Conv2d(1, 4, 3, padding=1)` → ReLU → `MaxPool2d(2)` → `Conv2d(4, 8, 3)` → ReLU → `MaxPool2d(2)` 순서로 통과시키며 "
          "**각 풀링 직후**의 모양 두 개와 마지막에 `flatten(1)`한 모양을 `[모양1, 모양2, 펼친 모양]`으로 반환하세요.",
          ["pooling", "conv"], 2,
          '''
          import torch
          from torch import nn


          def trace_shapes(h):
              x = torch.zeros(1, 1, h, h)
              pool = nn.MaxPool2d(2)
              x = pool(torch.relu(nn.Conv2d(1, 4, 3, padding=1)(x)))
              first = list(x.shape)
              x = pool(torch.relu(nn.Conv2d(4, 8, 3)(x)))
              return [first, list(x.shape), list(x.flatten(1).shape)]
          ''', "trace_shapes", [[8], [16], [28]],
          ["풀링 층은 매개변수가 없어 하나를 두 번 써도 됩니다.", "두 번째 합성곱은 padding이 없어 크기가 2 줄어듭니다."], tol=None),
    ])

# ====================================================================== Day 144
CNN_STARTER = c('''
    import torch
    from torch import nn


    class TinyCNN(nn.Module):
        def __init__(self):
            super().__init__()
            # self.conv, self.pool, self.fc를 만드세요
            pass

        def forward(self, x):
            # conv → ReLU → pool → flatten → fc
            pass


    def cnn_info(seed, n):
        torch.manual_seed(seed)
        model = TinyCNN()
        with torch.no_grad():
            out = model(torch.ones(n, 1, 8, 8))
        n_params = sum(p.numel() for p in model.parameters())
        return [list(out.shape), n_params, [round(v, 4) for v in out[0].tolist()]]
''')
day144 = D(
    144, "CNN 모델 구성", W, ["cnn", "nn_module", "conv", "pooling"],
    ["합성곱·풀링·선형 층으로 CNN 클래스를 만들 수 있다.", "CNN과 MLP의 매개변수 수를 비교할 수 있다."],
    "어제는 합성곱과 풀링을 지난 특성 맵의 모양을 따라가 보았습니다. 오늘은 이것을 모델 클래스로 묶습니다.",
    [("선형 층의 입력 수를 정하는 가장 확실한 방법은?", ["추측", "가짜 입력을 통과시켜 모양 확인", "항상 64", "이미지 개수"], 1)],
    "CNN 클래스",
    "이번 주에 쓸 기본 CNN입니다. 8×8 이미지가 [합성곱(8채널) → 풀링] 후 4×4, [합성곱(16채널) → 풀링] 후 2×2가 되어 16×2×2 = 64개로 펼쳐집니다.\n\n"
    "같은 크기의 MLP(64 → 64 → 10)와 비교하면 CNN은 매개변수가 훨씬 적으면서도 이미지에서 더 좋은 성능을 냅니다.",
    '''
    import torch
    from torch import nn

    class SmallCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 8, 3, padding=1)
            self.conv2 = nn.Conv2d(8, 16, 3, padding=1)
            self.pool = nn.MaxPool2d(2)
            self.fc = nn.Linear(16 * 2 * 2, 10)

        def forward(self, x):
            x = self.pool(torch.relu(self.conv1(x)))
            x = self.pool(torch.relu(self.conv2(x)))
            return self.fc(x.flatten(1))

    count = lambda m: sum(p.numel() for p in m.parameters())
    mlp = nn.Sequential(nn.Flatten(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))
    print(SmallCNN()(torch.zeros(3, 1, 8, 8)).shape, count(SmallCNN()), count(mlp))
    ''',
    "`nn.Flatten()`은 `flatten(1)`의 층 버전이라 Sequential 안에 넣을 수 있습니다.",
    "CNN의 펼치기 부분을 완성하세요.", "작은 CNN 클래스를 직접 작성하세요.",
    ["CNN = [합성곱 → ReLU → 풀링] × 몇 번 + 선형 층.", "펼친 크기 = 채널 × 높이 × 너비.", "CNN은 가중치 공유로 매개변수가 적다.",
     "`nn.Flatten()`은 Sequential용 펼치기."],
    [("16채널 2×2 특성 맵을 펼친 크기는?", ["16", "32", "64", "4"], 2),
     ("CNN의 매개변수가 적은 이유는?", ["커널을 모든 위치에서 공유", "층이 적어서", "풀링 때문만", "활성화 함수 때문"], 0)],
    [
        X("d144_fill_1", "펼치기",
          "SmallCNN의 빈칸을 채우고 `n`장 입력의 출력 모양과 매개변수 수를 `[모양, 매개변수 수]`로 반환하세요.", ["cnn"], 1,
          '''
          import torch
          from torch import nn
          ''' + CNN_SRC + '''

          def small_cnn_info(n):
              model = SmallCNN()
              return [list(model(torch.zeros(n, 1, 8, 8)).shape), sum(p.numel() for p in model.parameters())]
          ''', "small_cnn_info", [[2], [5]],
          ["16채널 × 2 × 2입니다.", "배치 차원(0번)은 남기고 1번부터 펼칩니다."], blanks=["16 * 2 * 2", "flatten(1)"], tol=None),
        X("d144_code_1", "TinyCNN",
          "`TinyCNN`을 완성하세요. `__init__`에서 `self.conv = nn.Conv2d(1, 4, 3, padding=1)`, `self.pool = nn.MaxPool2d(2)`, `self.fc = nn.Linear(4 * 4 * 4, 10)`을 **이 순서로** 만들고, "
          "`forward`는 conv → ReLU → pool → `flatten(1)` → fc를 계산합니다. `cnn_info`는 이미 작성되어 있습니다.",
          ["cnn", "nn_module"], 2,
          '''
          import torch
          from torch import nn


          class TinyCNN(nn.Module):
              def __init__(self):
                  super().__init__()
                  self.conv = nn.Conv2d(1, 4, 3, padding=1)
                  self.pool = nn.MaxPool2d(2)
                  self.fc = nn.Linear(4 * 4 * 4, 10)

              def forward(self, x):
                  x = self.pool(torch.relu(self.conv(x)))
                  return self.fc(x.flatten(1))


          def cnn_info(seed, n):
              torch.manual_seed(seed)
              model = TinyCNN()
              with torch.no_grad():
                  out = model(torch.ones(n, 1, 8, 8))
              n_params = sum(p.numel() for p in model.parameters())
              return [list(out.shape), n_params, [round(v, 4) for v in out[0].tolist()]]
          ''', "cnn_info", [[0, 2], [3, 1]],
          ["8×8에 padding 1 합성곱은 크기 유지, 풀링 후 4×4입니다.", "forward 마지막은 펼친 뒤 `self.fc`에 넣습니다."],
          starter=CNN_STARTER, checks=CLS),
    ])

# ====================================================================== Day 145
EVAL_SRC = '''

          def evaluate(model, loader):
              model.eval()
              correct = 0
              with torch.no_grad():
                  for xb, yb in loader:
                      correct += (model(xb).argmax(dim=1) == yb).sum().item()
              model.train()
              return correct / len(loader.dataset)
'''
day145 = D(
    145, "CNN 학습과 평가", W, ["cnn", "training_loop", "dataloader"],
    ["손글씨 숫자를 CNN으로 학습시키고 테스트 정확도를 구할 수 있다."],
    "어제는 CNN 클래스를 만들었습니다. 오늘은 실제로 학습시킵니다. 학습 루프는 지난주와 **똑같습니다**.",
    [("SmallCNN의 마지막 선형 층 입력 수는?", ["16", "64", "10", "128"], 1)],
    "손글씨 숫자 학습",
    "데이터를 학습 70%, 테스트 30%로 나누고 DataLoader로 감싼 뒤, Adam과 CrossEntropyLoss로 몇 에폭 학습합니다. "
    "평가는 `model.eval()`과 `torch.no_grad()` 안에서 맞힌 개수를 세면 됩니다.",
    '''
    import torch
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split
    from torch import nn, optim
    from torch.utils.data import DataLoader, TensorDataset

    digits = load_digits()
    X = torch.tensor(digits.images, dtype=torch.float32).unsqueeze(1) / 16
    y = torch.tensor(digits.target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=64, shuffle=True,
                        generator=torch.Generator().manual_seed(0))
    torch.manual_seed(0)
    model = nn.Sequential(nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(8 * 4 * 4, 10))
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    for epoch in range(5):
        for xb, yb in loader:
            loss = nn.CrossEntropyLoss()(model(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            acc = (model(X_test).argmax(dim=1) == y_test).float().mean().item()
        model.train()
        print(epoch, round(acc, 3))
    ''',
    "5 에폭 만에 약 95%를 맞힙니다. 에폭마다 테스트 정확도를 찍어 보면 언제 성능이 멈추는지 알 수 있습니다.",
    "평가 함수를 완성하세요.", "SmallCNN을 학습시키세요.",
    ["학습 루프는 모델 종류와 상관없이 같다.", "평가: eval + no_grad + argmax.", "에폭마다 정확도를 보면 학습 진행을 알 수 있다.",
     "작은 CNN으로도 손글씨 숫자 약 95%."],
    [("평가할 때 `torch.no_grad()`를 쓰는 이유는?", ["기울기 계산이 필요 없어 빠르고 메모리 절약", "정확도가 올라간다", "드롭아웃을 끈다", "학습률을 줄인다"], 0),
     ("맞힌 개수를 세는 식은?", ["`(pred == y).sum()`", "`pred.sum()`", "`y.mean()`", "`len(pred)`"], 0)],
    [
        X("d145_fill_1", "평가 함수",
          "모델과 DataLoader를 받아 정확도를 반환하는 `evaluate`를 완성하세요. 확인용으로 무작위 모델의 정확도를 계산합니다.", ["cnn", "dataloader"], 1,
          '''
          import torch
          from torch import nn
          from torch.utils.data import DataLoader, TensorDataset
          ''' + EVAL_SRC + '''

          def random_model_accuracy(seed):
              torch.manual_seed(seed)
              X, y = torch.randn(40, 4), torch.randint(0, 3, (40,))
              model = nn.Linear(4, 3)
              return evaluate(model, DataLoader(TensorDataset(X, y), batch_size=16))
          ''', "random_model_accuracy", [[0], [1]],
          ["기울기 기록을 끄는 구역입니다.", "가장 큰 로짓의 위치가 예측 클래스입니다."], blanks=["no_grad", "argmax(dim=1)"]),
        X("d145_code_1", "숫자 인식 CNN",
          "주어진 `digit_loaders(seed)`, `SmallCNN`, `evaluate`를 사용하세요. `torch.manual_seed(0)` 후 SmallCNN과 `optim.Adam(lr=0.01)`을 만들고 CrossEntropyLoss로 `epochs` 에폭 학습한 뒤 "
          "`[학습 정확도, 테스트 정확도]`(소수 넷째 자리)를 반환하세요.",
          ["cnn", "training_loop"], 3,
          DIGITS_IMPORTS + DIGITS_SRC + CNN_SRC + EVAL_SRC + '''

          def train_digits(seed, epochs):
              train_loader, test_loader = digit_loaders(seed)
              torch.manual_seed(0)
              model = SmallCNN()
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              for _ in range(epochs):
                  for xb, yb in train_loader:
                      loss = nn.CrossEntropyLoss()(model(xb), yb)
                      optimizer.zero_grad()
                      loss.backward()
                      optimizer.step()
              return [round(evaluate(model, train_loader), 4), round(evaluate(model, test_loader), 4)]
          ''', "train_digits", [[0, 6], [1, 4]],
          ["학습 루프는 지난주와 같습니다.", "정확도는 주어진 `evaluate`를 두 DataLoader에 각각 부르면 됩니다."], tol=3e-3, tl=90),
    ])

# ====================================================================== Day 146
day146 = D(
    146, "배치 정규화와 eval 모드", W, ["batchnorm", "dropout"],
    ["배치 정규화가 학습·평가 모드에서 다른 통계를 쓰는 것을 설명할 수 있다.", "eval 모드에서 샘플 하나를 예측할 수 있다."],
    "어제는 CNN으로 손글씨 숫자를 학습시켰습니다. 더 깊은 CNN에는 **배치 정규화**가 거의 항상 들어갑니다.",
    [("평가 전에 부르는 모드 전환 메서드는?", ["`train()`", "`eval()`", "`step()`", "`zero_grad()`"], 1)],
    "층 사이에서 정규화하기",
    "**배치 정규화**(`nn.BatchNorm1d`, `nn.BatchNorm2d`)는 층의 출력을 배치 평균 0, 표준편차 1로 맞춰 깊은 신경망 학습을 빠르고 안정적으로 만듭니다.\n\n"
    "- 학습 모드: **현재 배치**의 평균·분산으로 정규화하고, 이동 평균 `running_mean`·`running_var`를 갱신(momentum 0.1)\n"
    "- 평가 모드: 쌓아 둔 **이동 평균**으로 정규화 → 샘플 하나만 넣어도 동작\n\n그래서 `model.eval()`을 잊으면 예측이 배치 구성에 따라 달라집니다.",
    '''
    import torch
    from torch import nn

    bn = nn.BatchNorm1d(2)
    x = torch.tensor([[1.0, 10.0], [3.0, 30.0], [5.0, 50.0]])
    out = bn(x).detach()
    print(out.mean(dim=0).abs().round(decimals=4), bn.running_mean)
    bn.eval()
    print(bn(torch.tensor([[3.0, 30.0]])).detach().round(decimals=3))
    ''',
    "이동 평균은 한 번만 갱신되어 아직 실제 평균(3, 30)과 멀기 때문에 마지막 출력이 0 근처가 아닙니다. 학습을 여러 번 하면 점점 가까워집니다. 합성곱 뒤에는 `nn.BatchNorm2d(채널 수)`, 선형 층 뒤에는 `nn.BatchNorm1d(특성 수)`를 씁니다. 보통 [층 → 배치 정규화 → ReLU] 순서입니다.",
    "배치 정규화의 통계를 확인하세요.", "eval 모드로 샘플 하나를 예측하세요.",
    ["배치 정규화: 배치 평균 0·표준편차 1로.", "학습 모드: 배치 통계 + 이동 평균 갱신.", "평가 모드: 이동 평균 사용.",
     "Conv 뒤 BatchNorm2d, Linear 뒤 BatchNorm1d."],
    [("BatchNorm이 평가 모드에서 쓰는 통계는?", ["현재 배치", "이동 평균(running)", "0과 1", "테스트 전체"], 1),
     ("Conv2d(…, 16, …) 뒤에 붙이는 배치 정규화는?", ["`BatchNorm1d(16)`", "`BatchNorm2d(16)`", "`BatchNorm2d(1)`", "`Dropout(16)`"], 1)],
    [
        X("d146_fill_1", "이동 평균",
          "`nn.BatchNorm1d`에 2차원 목록을 학습 모드로 한 번 통과시킨 뒤 `running_mean`을 소수 넷째 자리 리스트로 반환하세요.", ["batchnorm"], 1,
          '''
          import torch
          from torch import nn


          def running_after_one(rows):
              x = torch.tensor(rows, dtype=torch.float32)
              bn = nn.BatchNorm1d(x.shape[1])
              bn(x)
              return [round(v, 4) for v in bn.running_mean.tolist()]
          ''', "running_after_one", [[[[1, 10], [3, 30], [5, 50]]], [[[0, 2, 4], [2, 2, 0]]]],
          ["선형 층 출력용 배치 정규화 클래스입니다.", "이동 평균 속성 이름입니다(`running_…`)."], blanks=["BatchNorm1d", "running_mean"]),
        X("d146_code_1", "샘플 하나 예측",
          "`torch.manual_seed(seed)` 후 `nn.Sequential(nn.Linear(2, 4), nn.BatchNorm1d(4), nn.ReLU(), nn.Linear(4, 1))`을 만드세요. "
          "학습 모드에서 `rows` 배치를 20번 통과시켜 이동 평균을 쌓은 뒤(`torch.no_grad()` 안, 학습은 하지 않음), `eval()`로 바꿔 `sample` 하나의 출력을 소수 넷째 자리로 반환하세요.",
          ["batchnorm"], 2,
          '''
          import torch
          from torch import nn


          def predict_one(seed, rows, sample):
              torch.manual_seed(seed)
              model = nn.Sequential(nn.Linear(2, 4), nn.BatchNorm1d(4), nn.ReLU(), nn.Linear(4, 1))
              X = torch.tensor(rows, dtype=torch.float32)
              with torch.no_grad():
                  for _ in range(20):
                      model(X)
                  model.eval()
                  out = model(torch.tensor([sample], dtype=torch.float32))
              return round(out.item(), 4)
          ''', "predict_one", [[0, [[1, 2], [3, 4], [5, 0]], [2, 2]], [1, [[0, 0], [1, 1]], [0.5, 0.5]]],
          ["모델을 만들 때는 학습 모드이므로 그대로 20번 통과시키면 이동 평균이 쌓입니다.", "샘플 하나는 `[sample]`로 감싸 (1, 2) 모양으로 만듭니다."],
          tol=1e-3),
    ])

# ====================================================================== Day 147 (review)
BNCNN_SRC = '''

          class BNCNN(nn.Module):
              def __init__(self):
                  super().__init__()
                  self.features = nn.Sequential(
                      nn.Conv2d(1, 8, 3, padding=1), nn.BatchNorm2d(8), nn.ReLU(), nn.MaxPool2d(2),
                      nn.Conv2d(8, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),
                  )
                  self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.2), nn.Linear(64, 10))

              def forward(self, x):
                  return self.classifier(self.features(x))
'''
day147 = D(
    147, "21주차 누적 복습", W, ["cnn", "conv", "pooling", "batchnorm", "image_tensor"],
    ["배치 정규화와 드롭아웃이 들어간 CNN을 학습·평가하고, 틀린 예측을 분석할 수 있다."],
    "| 날 | 주제 | 핵심 |\n|---|---|---|\n| 141 | 이미지 텐서 | (N, C, H, W), 0~1 정규화 |\n| 142 | 합성곱 | 커널, (H + 2p - k) // s + 1 |\n"
    "| 143 | 풀링 | MaxPool2d, flatten(1) |\n| 144 | CNN 클래스 | 합성곱 블록 + 선형 층 |\n| 145 | 학습·평가 | eval, no_grad, argmax |\n"
    "| 146 | 배치 정규화 | 학습=배치 통계, 평가=이동 평균 |",
    [("28×28 입력에 kernel 5, padding 0 합성곱을 하면?", ["28", "24", "23", "14"], 1),
     ("배치 정규화가 들어간 모델을 평가할 때 꼭 필요한 것은?", ["`model.eval()`", "학습률 감소", "`shuffle=False`", "드롭아웃 제거"], 0)],
    "블록으로 정리한 CNN",
    "층이 많아지면 `nn.Sequential`로 **특성 추출부**(features)와 **분류부**(classifier)를 나누어 정리합니다. 다음 다음 주 전이 학습에서 이 구분이 중요해집니다.\n\n"
    "도전 문제에서는 합성곱을 반복문으로 직접 구현해 `F.conv2d`와 같은지 확인합니다.",
    '''
    import torch
    from torch import nn

    features = nn.Sequential(nn.Conv2d(1, 8, 3, padding=1), nn.BatchNorm2d(8), nn.ReLU(), nn.MaxPool2d(2))
    classifier = nn.Sequential(nn.Flatten(), nn.Linear(8 * 4 * 4, 10))
    x = torch.zeros(2, 1, 8, 8)
    print(features(x).shape, classifier(features(x)).shape)
    ''',
    None,
    "합성곱 출력 크기 공식을 쓰세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["이미지 = (N, C, H, W) 텐서.", "CNN = 합성곱·배치 정규화·ReLU·풀링 블록 + 분류부.", "평가 땐 eval + no_grad.",
     "다음 주: 순서가 있는 데이터를 위한 RNN."],
    [("특성 추출부와 분류부를 나누면 좋은 점은?", ["구조가 읽기 쉽고 부분 재사용이 쉽다", "학습이 필요 없다", "정확도가 항상 오른다", "매개변수가 0이 된다"], 0),
     ("합성곱 커널 3×3, 입력 채널 8, 출력 채널 16의 가중치 수(편향 제외)는?", ["144", "1152", "72", "384"], 1)],
    [
        X("d147_fill_1", "출력 크기 공식",
          "입력 크기 h, 커널 k, stride s, padding p로 합성곱 출력 크기를 공식으로 계산해 반환하세요.", ["conv"], 1,
          '''
          def out_size(h, k, s, p):
              return (h + 2 * p - k) // s + 1
          ''', "out_size", [[8, 3, 1, 0], [28, 5, 1, 2], [32, 3, 2, 1], [7, 2, 2, 0]],
          ["패딩은 양쪽에 붙으므로 2배를 더합니다.", "나눗셈은 버림(몫)입니다."], blanks=["2 * p", "//"], tol=None),
        X("d147_code_1", "BN-CNN 학습과 오답 분석",
          "주어진 `digit_loaders(seed)`, `BNCNN`, `evaluate`를 사용하세요. `torch.manual_seed(0)` 후 BNCNN과 `optim.Adam(lr=0.01)`으로 `epochs` 에폭 학습한 뒤, "
          "`model.eval()` 상태에서 테스트 데이터를 예측해 `{\"accuracy\": 테스트 정확도(소수 넷째 자리), \"wrong\": 틀린 개수, \"most_missed\": 가장 많이 틀린 정답 숫자}`를 반환하세요. "
          "가장 많이 틀린 숫자가 여럿이면 작은 숫자를 고릅니다.",
          ["cnn", "batchnorm", "confusion_matrix"], 3,
          DIGITS_IMPORTS + DIGITS_SRC + BNCNN_SRC + EVAL_SRC + '''

          def analyze(seed, epochs):
              train_loader, test_loader = digit_loaders(seed)
              torch.manual_seed(0)
              model = BNCNN()
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              for _ in range(epochs):
                  for xb, yb in train_loader:
                      loss = nn.CrossEntropyLoss()(model(xb), yb)
                      optimizer.zero_grad()
                      loss.backward()
                      optimizer.step()
              accuracy = evaluate(model, test_loader)
              model.eval()
              missed = torch.zeros(10, dtype=torch.long)
              with torch.no_grad():
                  for xb, yb in test_loader:
                      wrong = model(xb).argmax(dim=1) != yb
                      missed += torch.bincount(yb[wrong], minlength=10)
              return {"accuracy": round(accuracy, 4), "wrong": missed.sum().item(), "most_missed": missed.argmax().item()}
          ''', "analyze", [[0, 3], [2, 2]],
          ["틀린 위치의 정답만 골라 `torch.bincount(..., minlength=10)`로 세면 숫자별 오답 수가 됩니다.", "`argmax()`는 같은 값이면 앞쪽(작은 숫자)을 고릅니다."],
          tol=3e-3, tl=90),
        X("d147_code_2", "합성곱 직접 구현(도전)",
          "반복문으로 합성곱(stride 1, padding 0)을 직접 계산해 2차원 리스트로 만들고, `F.conv2d` 결과와 같은지(`torch.allclose`) 비교해 `[직접 계산 결과, 같은지]`를 반환하세요. "
          "각 위치의 값은 겹친 부분을 원소별로 곱해 더한 값입니다.",
          ["conv"], 3,
          '''
          import torch
          import torch.nn.functional as F


          def manual_conv(image, kernel):
              x = torch.tensor(image, dtype=torch.float32)
              k = torch.tensor(kernel, dtype=torch.float32)
              kh, kw = k.shape
              out_h, out_w = x.shape[0] - kh + 1, x.shape[1] - kw + 1
              out = torch.zeros(out_h, out_w)
              for i in range(out_h):
                  for j in range(out_w):
                      out[i, j] = (x[i:i + kh, j:j + kw] * k).sum()
              ref = F.conv2d(x.reshape(1, 1, *x.shape), k.reshape(1, 1, kh, kw))[0, 0]
              return [out.tolist(), torch.allclose(out, ref)]
          ''', "manual_conv",
          [[[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 0], [0, -1]]],
           [[[0, 1, 0, 2], [3, 0, 1, 1], [2, 2, 0, 1], [1, 0, 3, 0]], [[1, 1, 1], [0, 0, 0], [-1, -1, -1]]]],
          ["출력 크기는 입력 크기 - 커널 크기 + 1입니다.", "`x[i:i + kh, j:j + kw]`로 겹친 부분을 잘라 커널과 곱해 더하세요."],
          required=False),
    ], review_title="21주차 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day141, day142, day143, day144, day145, day146, day147])
