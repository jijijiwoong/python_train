"""Week 22 (Day 148-154): 순환 신경망과 시퀀스 모델."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dl_common import D, X, c, write_lessons  # noqa: E402

W = 22

SINE_SRC = '''

          def sine_windows(n_points, window):
              t = torch.linspace(0, 8 * torch.pi, n_points)
              series = torch.sin(t)
              X = torch.stack([series[i:i + window] for i in range(n_points - window)]).unsqueeze(-1)
              y = series[window:].unsqueeze(-1)
              return X, y
'''
SEQ_MODEL_SRC = '''

          class SeqModel(nn.Module):
              def __init__(self, cell="rnn", hidden=16):
                  super().__init__()
                  layer = nn.LSTM if cell == "lstm" else nn.RNN
                  self.rnn = layer(1, hidden, batch_first=True)
                  self.head = nn.Linear(hidden, 1)

              def forward(self, x):
                  out, _ = self.rnn(x)
                  return self.head(out[:, -1])
'''
TRAIN_SEQ_SRC = '''

          def train_seq(cell, epochs):
              X, y = sine_windows(200, 10)
              X_train, y_train, X_test, y_test = X[:150], y[:150], X[150:], y[150:]
              torch.manual_seed(0)
              model = SeqModel(cell)
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              for _ in range(epochs):
                  loss = nn.MSELoss()(model(X_train), y_train)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              with torch.no_grad():
                  test_loss = nn.MSELoss()(model(X_test), y_test)
              return [round(loss.item(), 4), round(test_loss.item(), 4)]
'''
TEXT_SRC = '''

          POS = ["정말 재미있는 영화", "배우 연기가 최고", "다시 보고 싶은 영화", "음악이 정말 좋다",
                 "최고의 영화 추천", "재미있고 감동적인 이야기", "연기가 훌륭하다", "감동적인 음악과 연기"]
          NEG = ["정말 지루한 영화", "연기가 너무 어색하다", "다시는 보고 싶지 않다", "음악이 시끄럽고 별로",
                 "최악의 영화", "지루하고 뻔한 이야기", "시간이 아까운 영화", "어색한 연기와 지루한 전개"]


          def build_vocab(sentences):
              words = sorted({w for s in sentences for w in s.split()})
              return {"<pad>": 0, "<unk>": 1, **{w: i + 2 for i, w in enumerate(words)}}


          def encode(sentences, vocab, max_len):
              rows = []
              for s in sentences:
                  ids = [vocab.get(w, 1) for w in s.split()][:max_len]
                  rows.append(ids + [0] * (max_len - len(ids)))
              return torch.tensor(rows)
'''
BAG_SRC = '''

          class MeanEmbedding(nn.Module):
              def __init__(self, vocab_size, dim, n_classes):
                  super().__init__()
                  self.emb = nn.Embedding(vocab_size, dim, padding_idx=0)
                  self.fc = nn.Linear(dim, n_classes)

              def forward(self, ids):
                  mask = (ids != 0).unsqueeze(-1).float()
                  pooled = (self.emb(ids) * mask).sum(dim=1) / mask.sum(dim=1)
                  return self.fc(pooled)
'''

# ====================================================================== Day 148
day148 = D(
    148, "시퀀스 데이터와 윈도우", W, ["sequence", "tensor_shape"],
    ["시계열을 고정 길이 윈도우와 다음 값 정답으로 바꿀 수 있다.", "RNN 입력 모양 (N, 길이, 특성)을 만들 수 있다."],
    "이번 주는 **순서가 중요한 데이터**(시계열, 문장)를 다룹니다. CNN이 공간의 무늬를 봤다면 RNN은 시간의 흐름을 봅니다.",
    [("CNN이 이미지에서 같은 커널을 모든 위치에 쓰는 것을 무엇이라 하나?", ["가중치 공유", "드롭아웃", "정규화", "풀링"], 0)],
    "윈도우 만들기",
    "\"지난 5일의 값으로 내일 값을 예측\"하려면 시계열을 길이 5짜리 조각(**윈도우**)과 그 다음 값(정답)의 쌍으로 바꿉니다.\n\n"
    "값이 n개, 윈도우 길이가 w이면 쌍은 n - w개입니다. RNN은 입력을 **(N, 길이, 특성 수)** 모양으로 받으므로(`batch_first=True`일 때) "
    "값 하나짜리 시계열은 마지막에 `unsqueeze(-1)`로 특성 차원 1을 붙입니다.",
    '''
    import torch

    series = torch.arange(1, 9, dtype=torch.float32)
    w = 3
    X = torch.stack([series[i:i + w] for i in range(len(series) - w)])
    y = series[w:]
    print(X)
    print(y)
    print(X.unsqueeze(-1).shape)
    ''',
    "시계열은 섞어서 나누면 미래 정보가 학습에 새어 들어갑니다. 학습·테스트는 **앞부분과 뒷부분**으로 나누세요.",
    "윈도우를 만드세요.", "RNN 입력 모양으로 준비하세요.",
    ["시계열 → (윈도우, 다음 값) 쌍.", "쌍의 개수 = n - w.", "RNN 입력 = (N, 길이, 특성).", "시계열은 시간 순서로 분할."],
    [("값 10개, 윈도우 4이면 쌍의 수는?", ["4", "6", "7", "10"], 1),
     ("`batch_first=True` RNN의 입력 모양은?", ["(길이, N, 특성)", "(N, 길이, 특성)", "(N, 특성)", "(특성, 길이)"], 1)],
    [
        X("d148_fill_1", "윈도우",
          "값 목록을 길이 `w` 윈도우 텐서 X와 다음 값 텐서 y로 바꿔 `[X, y]`를 반환하세요.", ["sequence"], 1,
          '''
          import torch


          def windows(values, w):
              series = torch.tensor(values, dtype=torch.float32)
              X = torch.stack([series[i:i + w] for i in range(len(series) - w)])
              y = series[w:]
              return [X, y]
          ''', "windows", [[[1, 2, 3, 4, 5], 2], [[10, 20, 30, 40], 3], [[0, 1, 0, 1, 0, 1], 4]],
          ["여러 텐서를 새 차원으로 쌓는 함수입니다.", "정답은 w번째 값부터 끝까지입니다."], blanks=["stack", "series[w:]"]),
        X("d148_code_1", "RNN 입력 준비",
          "값 목록으로 길이 `w` 윈도우를 만들어 X는 (N, w, 1), y는 (N, 1) 모양으로 바꾸세요. 앞 `train`개 쌍을 학습용으로 나누고 "
          "`[X 모양, y 모양, 학습 X 개수, 테스트의 첫 윈도우(펼친 리스트), 테스트의 첫 정답]`을 반환합니다.",
          ["sequence", "tensor_shape"], 2,
          '''
          import torch


          def prepare(values, w, train):
              series = torch.tensor(values, dtype=torch.float32)
              X = torch.stack([series[i:i + w] for i in range(len(series) - w)]).unsqueeze(-1)
              y = series[w:].unsqueeze(-1)
              X_train, X_test, y_test = X[:train], X[train:], y[train:]
              return [list(X.shape), list(y.shape), len(X_train), X_test[0].flatten().tolist(), y_test[0].item()]
          ''', "prepare", [[[1, 2, 3, 4, 5, 6, 7, 8], 3, 3], [list(range(0, 50, 5)), 4, 4]],
          ["윈도우를 만든 뒤 `unsqueeze(-1)`로 특성 차원을 붙입니다.", "시간 순서대로 앞 `train`개, 나머지로 나눕니다."]),
    ], review_title="22주차 시작")

# ====================================================================== Day 149
day149 = D(
    149, "RNN과 은닉 상태", W, ["rnn", "sequence"],
    ["RNN이 은닉 상태를 이어 가며 시퀀스를 처리하는 방식을 설명할 수 있다.", "nn.RNN의 출력과 마지막 은닉 상태의 모양을 구할 수 있다."],
    "어제는 시계열을 (N, 길이, 특성) 윈도우로 만들었습니다.",
    [("값 하나짜리 시계열 윈도우 20개(길이 5)의 RNN 입력 모양은?", ["(20, 5)", "(20, 5, 1)", "(5, 20, 1)", "(1, 20, 5)"], 1)],
    "기억을 이어 가는 층",
    "**RNN**은 시퀀스를 한 칸씩 읽으며 **은닉 상태** h를 갱신합니다.\n\n"
    "h_t = tanh(x_t·W_ih + b_ih + h_{t-1}·W_hh + b_hh)\n\n"
    "같은 가중치를 모든 시점에 쓰고, h에 지금까지 읽은 내용이 요약됩니다. `nn.RNN(입력 특성, 은닉 크기, batch_first=True)`를 부르면 "
    "`out`(모든 시점의 h, 모양 (N, 길이, 은닉))과 `h_n`(마지막 h, 모양 (층 수, N, 은닉))을 돌려줍니다.",
    '''
    import torch
    from torch import nn

    torch.manual_seed(0)
    rnn = nn.RNN(input_size=1, hidden_size=3, batch_first=True)
    x = torch.randn(4, 5, 1)
    out, h_n = rnn(x)
    print(out.shape, h_n.shape)
    print(torch.allclose(out[:, -1], h_n[0]))
    print(rnn.weight_ih_l0.shape, rnn.weight_hh_l0.shape)
    ''',
    "`out[:, -1]`(마지막 시점의 출력)과 `h_n[0]`은 같은 값입니다. 다음 값 예측처럼 시퀀스 전체를 하나로 요약할 때 이 값을 씁니다.",
    "RNN 출력 모양을 확인하세요.", "RNN 계산을 직접 펼쳐 보세요.",
    ["RNN = 은닉 상태를 이어 가며 한 칸씩 처리.", "모든 시점이 같은 가중치 공유.", "out: (N, 길이, 은닉), h_n: (층, N, 은닉).",
     "`out[:, -1]` = 마지막 은닉 상태."],
    [("hidden_size 8, 입력 (2, 10, 1)인 RNN의 out 모양은?", ["(2, 10, 8)", "(2, 8)", "(10, 2, 8)", "(1, 2, 8)"], 0),
     ("RNN 은닉 상태 계산에 쓰는 기본 활성화 함수는?", ["ReLU", "tanh", "시그모이드", "softmax"], 1)],
    [
        X("d149_fill_1", "RNN 모양",
          "`nn.RNN(1, hidden, batch_first=True)`에 `torch.zeros(n, length, 1)`을 넣고 `[out 모양, h_n 모양]`을 반환하세요.", ["rnn"], 1,
          '''
          import torch
          from torch import nn


          def rnn_shapes(n, length, hidden):
              rnn = nn.RNN(1, hidden, batch_first=True)
              out, h_n = rnn(torch.zeros(n, length, 1))
              return [list(out.shape), list(h_n.shape)]
          ''', "rnn_shapes", [[4, 5, 3], [1, 10, 8], [2, 3, 16]],
          ["입력의 첫 차원이 배치라고 알려 주는 옵션입니다.", "RNN은 출력과 마지막 은닉 상태 두 개를 돌려줍니다."],
          blanks=["batch_first=True", "out, h_n"], tol=None),
        X("d149_code_1", "RNN 펼치기",
          "`torch.manual_seed(seed)` 후 `nn.RNN(1, 3, batch_first=True)`를 만들고, 시퀀스 `values`(샘플 1개)를 반복문으로 직접 계산하세요. "
          "h는 0에서 시작하고 매 시점 `h = tanh(x @ W_ih.T + b_ih + h @ W_hh.T + b_hh)`입니다(가중치는 `rnn.weight_ih_l0` 등). "
          "`[마지막 h(소수 넷째 자리 리스트), nn.RNN의 h_n과 같은지]`를 반환하세요.",
          ["rnn"], 3,
          '''
          import torch
          from torch import nn


          def unroll(seed, values):
              torch.manual_seed(seed)
              rnn = nn.RNN(1, 3, batch_first=True)
              x = torch.tensor(values, dtype=torch.float32).reshape(1, -1, 1)
              h = torch.zeros(1, 3)
              with torch.no_grad():
                  for t in range(x.shape[1]):
                      from_x = x[:, t] @ rnn.weight_ih_l0.T + rnn.bias_ih_l0
                      from_h = h @ rnn.weight_hh_l0.T + rnn.bias_hh_l0
                      h = torch.tanh(from_x + from_h)
                  _, h_n = rnn(x)
              return [[round(v, 4) for v in h[0].tolist()], torch.allclose(h, h_n[0], atol=1e-6)]
          ''', "unroll", [[0, [1.0, 0.5, -1.0]], [3, [0.2, 0.4, 0.6, 0.8]]],
          ["시퀀스를 (1, 길이, 1) 모양으로 만들고 `x[:, t]`로 t 시점 입력 (1, 1)을 꺼냅니다.", "비교용 h_n은 `rnn(x)`로 구하고 `h_n[0]`과 비교하세요."]),
    ])

# ====================================================================== Day 150
day150 = D(
    150, "RNN으로 시계열 예측", W, ["rnn", "sequence", "training_loop"],
    ["RNN의 마지막 출력을 선형 층에 넣어 다음 값을 예측할 수 있다.", "시계열 모델을 학습시키고 테스트 오차를 구할 수 있다."],
    "어제는 RNN의 출력 모양과 은닉 상태를 확인했습니다. 오늘은 사인파의 다음 값을 예측합니다.",
    [("RNN의 `out[:, -1]`은 무엇과 같은가?", ["첫 시점 출력", "마지막 은닉 상태", "입력", "가중치"], 1)],
    "다음 값 예측 모델",
    "모델 구조는 간단합니다. RNN이 윈도우를 읽고, 마지막 시점의 출력을 선형 층에 넣어 숫자 하나를 냅니다. 손실은 MSE입니다.\n\n"
    "아래 `SeqModel`은 이번 주 계속 쓸 모델로, `cell=\"lstm\"`을 주면 내일 배울 LSTM으로 바뀝니다.",
    '''
    import torch
    from torch import nn, optim

    t = torch.linspace(0, 8 * torch.pi, 200)
    series = torch.sin(t)
    X = torch.stack([series[i:i + 10] for i in range(190)]).unsqueeze(-1)
    y = series[10:].unsqueeze(-1)

    class SeqModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.rnn = nn.RNN(1, 16, batch_first=True)
            self.head = nn.Linear(16, 1)

        def forward(self, x):
            out, _ = self.rnn(x)
            return self.head(out[:, -1])

    torch.manual_seed(0)
    model = SeqModel()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    for epoch in range(150):
        loss = nn.MSELoss()(model(X[:150]), y[:150])
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        print(round(loss.item(), 4), round(nn.MSELoss()(model(X[150:]), y[150:]).item(), 4))
    ''',
    "`out, _ = self.rnn(x)`처럼 쓰지 않을 반환값은 `_`로 받습니다.",
    "마지막 시점 출력을 고르세요.", "사인파 예측 모델을 학습시키세요.",
    ["시계열 예측 = RNN + 마지막 출력 + 선형 층.", "손실은 MSE.", "학습은 앞부분, 평가는 뒷부분.", "모델 구조만 바뀌고 학습 루프는 같다."],
    [("`out`이 (N, 10, 16)일 때 `out[:, -1]`의 모양은?", ["(N, 16)", "(N, 10)", "(10, 16)", "(N, 1)"], 0),
     ("다음 값(실수) 예측에 쓰는 손실은?", ["CrossEntropyLoss", "MSELoss", "정확도", "BCE"], 1)],
    [
        X("d150_fill_1", "마지막 출력",
          "SeqModel의 forward에서 마지막 시점 출력을 골라 선형 층에 넣도록 완성하고, `n`개 윈도우(길이 `length`)를 넣은 출력 모양을 반환하세요.", ["rnn"], 1,
          '''
          import torch
          from torch import nn
          ''' + SEQ_MODEL_SRC + '''

          def output_shape(n, length):
              return list(SeqModel()(torch.zeros(n, length, 1)).shape)
          ''', "output_shape", [[4, 10], [1, 3]],
          ["RNN이 돌려주는 두 값 중 첫 번째만 씁니다.", "모든 배치의 마지막 시점은 `[:, -1]`로 고릅니다."],
          blanks=["out, _", "out[:, -1]"], tol=None),
        X("d150_code_1", "사인파 예측",
          "주어진 `sine_windows`, `SeqModel`을 사용하세요. `sine_windows(200, 10)`의 앞 150개로 학습, 뒤로 평가합니다. "
          "`torch.manual_seed(0)` 후 `SeqModel(cell)`과 `optim.Adam(lr=0.01)`으로 전체 배치를 `epochs`번 학습하고 "
          "`[마지막 학습 손실, 테스트 손실]`(소수 넷째 자리)을 반환하세요.",
          ["rnn", "training_loop"], 3,
          '''
          import torch
          from torch import nn, optim
          ''' + SINE_SRC + SEQ_MODEL_SRC + TRAIN_SEQ_SRC, "train_seq", [["rnn", 150], ["rnn", 50]],
          ["학습 데이터는 `X[:150]`, `y[:150]`입니다.", "테스트 손실은 `torch.no_grad()` 안에서 계산하세요."], tol=2e-3, tl=90),
    ])

# ====================================================================== Day 151
day151 = D(
    151, "LSTM", W, ["lstm", "rnn"],
    ["LSTM이 긴 시퀀스에서 RNN보다 유리한 이유를 설명할 수 있다.", "nn.LSTM의 반환값 (out, (h, c))를 다룰 수 있다."],
    "어제는 RNN으로 사인파를 예측했습니다. 시퀀스가 길어지면 RNN은 앞쪽 정보를 잘 잊어버립니다.",
    [("RNN이 매 시점 갱신하는 값은?", ["학습률", "은닉 상태", "손실", "가중치"], 1)],
    "오래 기억하는 셀",
    "RNN은 기울기가 시점을 거슬러 갈수록 작아져(**기울기 소실**) 먼 과거를 학습하기 어렵습니다. **LSTM**은 은닉 상태 h 외에 **셀 상태** c를 두고, "
    "세 개의 **게이트**(입력·망각·출력)가 무엇을 기억하고 잊을지 정합니다.\n\n"
    "`nn.LSTM`은 `nn.RNN`과 사용법이 같지만 `out, (h_n, c_n)`을 돌려주고, 게이트 때문에 매개변수가 RNN의 4배입니다.",
    '''
    import torch
    from torch import nn

    rnn = nn.RNN(1, 8, batch_first=True)
    lstm = nn.LSTM(1, 8, batch_first=True)
    count = lambda m: sum(p.numel() for p in m.parameters())
    print(count(rnn), count(lstm))
    out, (h_n, c_n) = lstm(torch.zeros(2, 5, 1))
    print(out.shape, h_n.shape, c_n.shape)
    ''',
    "GRU(`nn.GRU`)는 게이트를 둘로 줄인 LSTM의 가벼운 버전으로, 반환값은 RNN과 같습니다.",
    "LSTM의 반환값을 받으세요.", "RNN과 LSTM을 비교하세요.",
    ["RNN은 긴 시퀀스에서 기울기 소실.", "LSTM = 은닉 상태 + 셀 상태 + 게이트 3개.", "반환값: `out, (h_n, c_n)`.",
     "매개변수는 RNN의 4배."],
    [("LSTM이 RNN에 추가로 가진 상태는?", ["셀 상태", "학습률", "드롭아웃", "패딩"], 0),
     ("같은 크기에서 LSTM 매개변수는 RNN의 몇 배?", ["2배", "3배", "4배", "같다"], 2)],
    [
        X("d151_fill_1", "LSTM 반환값",
          "`nn.LSTM(1, hidden, batch_first=True)`에 `torch.zeros(n, length, 1)`을 넣고 `[out 모양, h_n 모양, c_n 모양]`을 반환하세요.", ["lstm"], 1,
          '''
          import torch
          from torch import nn


          def lstm_shapes(n, length, hidden):
              lstm = nn.LSTM(1, hidden, batch_first=True)
              out, (h_n, c_n) = lstm(torch.zeros(n, length, 1))
              return [list(out.shape), list(h_n.shape), list(c_n.shape)]
          ''', "lstm_shapes", [[2, 5, 8], [1, 3, 4]],
          ["LSTM 층 클래스 이름입니다.", "두 번째 반환값은 (은닉 상태, 셀 상태) 튜플입니다."], blanks=["LSTM(", "(h_n, c_n)"], tol=None),
        X("d151_code_1", "RNN 대 LSTM",
          "주어진 `train_seq(cell, epochs)`로 `\"rnn\"`과 `\"lstm\"`을 각각 `epochs`번 학습해 "
          "`{\"rnn\": [학습 손실, 테스트 손실], \"lstm\": [...], \"better\": 테스트 손실이 더 작은 쪽 이름}`을 반환하세요.",
          ["lstm", "rnn"], 2,
          '''
          import torch
          from torch import nn, optim
          ''' + SINE_SRC + SEQ_MODEL_SRC + TRAIN_SEQ_SRC + '''

          def compare_cells(epochs):
              results = {cell: train_seq(cell, epochs) for cell in ["rnn", "lstm"]}
              results["better"] = min(["rnn", "lstm"], key=lambda cell: results[cell][1])
              return results
          ''', "compare_cells", [[100], [40]],
          ["딕셔너리 컴프리헨션으로 두 셀을 한 번에 학습시킬 수 있습니다.", "테스트 손실은 각 결과의 두 번째 값입니다."], tol=2e-3, tl=120),
    ])

# ====================================================================== Day 152
day152 = D(
    152, "토큰화와 임베딩", W, ["embedding", "text_processing"],
    ["문장을 단어 번호 시퀀스로 바꾸고 길이를 맞출 수 있다.", "nn.Embedding으로 번호를 벡터로 바꿀 수 있다."],
    "어제까지는 숫자 시계열을 다뤘습니다. 오늘부터 **문장**을 신경망에 넣는 방법을 배웁니다.",
    [("LSTM의 반환값 형태는?", ["`out, h_n`", "`out, (h_n, c_n)`", "`(out, h_n, c_n)`", "`out`만"], 1)],
    "단어를 숫자로",
    "1. **토큰화**: 문장을 단어(토큰)로 나누기. 여기서는 공백 기준 `split()`\n"
    "2. **어휘 사전**: 단어 → 번호. 0은 길이를 맞추는 `<pad>`, 1은 사전에 없는 단어 `<unk>`로 예약\n"
    "3. **패딩**: 짧은 문장 뒤를 0으로 채워 길이를 맞춤\n"
    "4. **임베딩** `nn.Embedding(사전 크기, 차원, padding_idx=0)`: 번호마다 학습되는 벡터 하나\n\n"
    "임베딩 벡터는 학습 중에 비슷한 뜻의 단어끼리 가까워지도록 조정됩니다.",
    '''
    import torch
    from torch import nn

    sentences = ["영화 정말 재미있다", "영화 지루하다"]
    words = sorted({w for s in sentences for w in s.split()})
    vocab = {"<pad>": 0, "<unk>": 1, **{w: i + 2 for i, w in enumerate(words)}}
    print(vocab)
    ids = [[vocab.get(w, 1) for w in s.split()] for s in sentences + ["영화 최고"]]
    padded = torch.tensor([row + [0] * (3 - len(row)) for row in ids])
    print(padded)
    emb = nn.Embedding(len(vocab), 4, padding_idx=0)
    print(emb(padded).shape, emb.weight[0].tolist())
    ''',
    "`padding_idx=0`인 임베딩은 0번 벡터가 항상 0이고 학습되지 않습니다. 패딩이 결과에 섞이지 않게 해 줍니다.",
    "어휘 사전을 만드세요.", "문장을 번호 텐서로 바꾸세요.",
    ["토큰화 → 어휘 사전 → 번호 → 패딩.", "0 = `<pad>`, 1 = `<unk>`.", "`nn.Embedding(사전 크기, 차원, padding_idx=0)`.",
     "임베딩 출력 = (N, 길이, 차원)."],
    [("사전에 없는 단어에 주는 번호는?", ["0", "1", "-1", "오류"], 1),
     ("(3, 5) 번호 텐서를 차원 8 임베딩에 넣으면?", ["(3, 5)", "(3, 5, 8)", "(3, 8)", "(8, 5)"], 1)],
    [
        X("d152_fill_1", "어휘 사전",
          "문장 목록의 단어를 가나다순으로 정렬해 2번부터 번호를 매기고, 0번 `<pad>`, 1번 `<unk>`를 포함한 사전을 반환하세요.", ["embedding", "dict"], 1,
          '''
          def build_vocab(sentences):
              words = sorted({w for s in sentences for w in s.split()})
              return {"<pad>": 0, "<unk>": 1, **{w: i + 2 for i, w in enumerate(words)}}
          ''', "build_vocab", [[["영화 정말 재미있다", "영화 지루하다"]], [["a b", "b c a"]]],
          ["중복 없는 단어를 정렬해야 합니다.", "번호 0, 1이 예약되어 있으니 2부터 시작합니다."],
          blanks=["sorted", "i + 2"], tol=None),
        X("d152_code_1", "번호 텐서",
          "`sentences`로 어휘 사전을 만들고(0 `<pad>`, 1 `<unk>`, 나머지는 가나다순 2부터), `queries` 문장들을 번호로 바꾸세요. "
          "길이는 `max_len`으로 맞춥니다(길면 자르고 짧으면 0으로 채움). `[사전 크기, 번호 텐서]`를 반환하세요.",
          ["embedding", "text_processing"], 2,
          '''
          import torch


          def to_ids(sentences, queries, max_len):
              words = sorted({w for s in sentences for w in s.split()})
              vocab = {"<pad>": 0, "<unk>": 1, **{w: i + 2 for i, w in enumerate(words)}}
              rows = []
              for q in queries:
                  ids = [vocab.get(w, 1) for w in q.split()][:max_len]
                  rows.append(ids + [0] * (max_len - len(ids)))
              return [len(vocab), torch.tensor(rows)]
          ''', "to_ids",
          [[["영화 정말 재미있다", "영화 지루하다"], ["영화 최고", "정말 정말 재미있다 영화"], 3],
           [["a b c"], ["c b a", "d"], 2]],
          ["사전에 없는 단어는 `vocab.get(w, 1)`로 1번이 됩니다.", "자를 때는 `[:max_len]`, 채울 때는 `[0] * (max_len - len(ids))`."], tol=None),
    ])

# ====================================================================== Day 153
TEXT_IMPORTS = '''
          import torch
          from torch import nn, optim
'''
day153 = D(
    153, "텍스트 분류 모델", W, ["embedding", "multiclass", "training_loop"],
    ["임베딩 평균으로 문장 벡터를 만들 수 있다.", "작은 감성 분류 모델을 학습시키고 새 문장을 예측할 수 있다."],
    "어제는 문장을 번호 텐서로 바꾸고 임베딩에 넣었습니다. 오늘은 영화평이 긍정인지 부정인지 분류합니다.",
    [("`nn.Embedding(..., padding_idx=0)`에서 0번 벡터는?", ["무작위", "항상 0", "항상 1", "가장 크다"], 1)],
    "임베딩 평균 분류기",
    "가장 간단한 문장 분류기는 단어 임베딩의 **평균**을 문장 벡터로 쓰고 선형 층으로 분류하는 것입니다. 패딩 위치는 평균에서 빼야 하므로 **마스크**를 씁니다.\n\n"
    "`mask = (ids != 0)` → 패딩이 아닌 곳만 1. 문장 벡터 = (임베딩 × 마스크)의 합 ÷ 마스크의 합.\n\n"
    "단어 순서를 무시하지만 데이터가 적을 때 잘 동작합니다. 순서가 중요하면 임베딩 뒤에 LSTM을 둡니다.",
    '''
    import torch
    from torch import nn

    emb = nn.Embedding(5, 2, padding_idx=0)
    with torch.no_grad():
        emb.weight[:] = torch.tensor([[0, 0], [1, 1], [2, 0], [0, 4], [3, 3]], dtype=torch.float32)
    ids = torch.tensor([[2, 3, 0, 0], [4, 1, 1, 0]])
    mask = (ids != 0).unsqueeze(-1).float()
    print(mask.squeeze(-1))
    print((emb(ids) * mask).sum(dim=1) / mask.sum(dim=1))
    ''',
    "마스크 없이 평균을 내면 패딩이 많은 짧은 문장일수록 벡터가 0 쪽으로 끌려갑니다.",
    "마스크 평균을 완성하세요.", "감성 분류기를 학습시키세요.",
    ["문장 벡터 = 단어 임베딩의 평균.", "마스크로 패딩 제외.", "평균 벡터 → 선형 층 → 클래스.", "순서가 중요하면 LSTM 추가."],
    [("`ids != 0`으로 만든 마스크의 역할은?", ["패딩 위치 제외", "단어 순서 기록", "정답 표시", "학습률 조절"], 0),
     ("임베딩 평균 분류기가 무시하는 정보는?", ["단어 종류", "단어 순서", "문장 길이 전부", "어휘"], 1)],
    [
        X("d153_fill_1", "마스크 평균",
          "MeanEmbedding의 빈칸을 채우고, `torch.manual_seed(seed)` 후 만든 모델에 번호 텐서를 넣은 출력(소수 넷째 자리)을 반환하세요.", ["embedding"], 1,
          TEXT_IMPORTS + BAG_SRC + '''

          def bag_output(seed, ids):
              torch.manual_seed(seed)
              model = MeanEmbedding(6, 3, 2)
              with torch.no_grad():
                  return model(torch.tensor(ids)).round(decimals=4)
          ''', "bag_output", [[0, [[2, 3, 0], [5, 1, 1]]], [1, [[4, 0, 0]]]],
          ["패딩이 아닌 위치를 고르는 비교 연산입니다.", "단어 수로 나누어야 평균이 됩니다."], blanks=["ids != 0", "mask.sum(dim=1)"]),
        X("d153_code_1", "영화평 분류",
          "주어진 POS(정답 1)·NEG(정답 0) 문장과 `build_vocab`, `encode`, `MeanEmbedding`을 사용하세요. 학습 문장은 `POS + NEG`, 길이 6으로 인코딩합니다. "
          "`torch.manual_seed(seed)` 후 `MeanEmbedding(사전 크기, 8, 2)`와 `optim.Adam(lr=0.05)`로 전체 배치를 100번 학습하고, "
          "`tests` 문장의 예측 클래스 리스트와 학습 정확도를 `[예측, 학습 정확도]`로 반환하세요.",
          ["embedding", "training_loop"], 3,
          TEXT_IMPORTS + TEXT_SRC + BAG_SRC + '''

          def sentiment(seed, tests):
              vocab = build_vocab(POS + NEG)
              X = encode(POS + NEG, vocab, 6)
              y = torch.tensor([1] * len(POS) + [0] * len(NEG))
              torch.manual_seed(seed)
              model = MeanEmbedding(len(vocab), 8, 2)
              optimizer = optim.Adam(model.parameters(), lr=0.05)
              for _ in range(100):
                  loss = nn.CrossEntropyLoss()(model(X), y)
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              with torch.no_grad():
                  train_acc = (model(X).argmax(dim=1) == y).float().mean().item()
                  pred = model(encode(tests, vocab, 6)).argmax(dim=1)
              return [pred.tolist(), train_acc]
          ''', "sentiment", [[0, ["정말 재미있는 이야기", "지루한 연기"]], [1, ["최고의 음악", "어색하고 지루한 영화", "처음 보는 단어"]]],
          ["정답은 POS 개수만큼 1, NEG 개수만큼 0입니다.", "새 문장도 같은 사전과 길이로 `encode`해야 합니다."], tol=1e-3),
    ])

# ====================================================================== Day 154 (review)
TREND_SRC = '''

          def trend_data(seed, n=200, length=12):
              g = torch.Generator().manual_seed(seed)
              slope = torch.rand(n, 1, generator=g) * 2 - 1
              t = torch.arange(length, dtype=torch.float32)
              X = (slope * t / length + 0.3 * torch.randn(n, length, generator=g)).unsqueeze(-1)
              y = (slope.squeeze(1) > 0).long()
              return X, y


          class TrendLSTM(nn.Module):
              def __init__(self):
                  super().__init__()
                  self.lstm = nn.LSTM(1, 16, batch_first=True)
                  self.fc = nn.Linear(16, 2)

              def forward(self, x):
                  out, _ = self.lstm(x)
                  return self.fc(out[:, -1])
'''
day154 = D(
    154, "22주차 누적 복습", W, ["sequence", "rnn", "lstm", "embedding"],
    ["LSTM으로 시퀀스 분류 모델을 학습하고, LSTM 셀의 계산을 설명할 수 있다."],
    "| 날 | 주제 | 핵심 |\n|---|---|---|\n| 148 | 윈도우 | (N, 길이, 특성), 시간 순서 분할 |\n| 149 | RNN | 은닉 상태, `out`, `h_n` |\n"
    "| 150 | 예측 | `out[:, -1]` → 선형 층 |\n| 151 | LSTM | 셀 상태, 게이트, `out, (h, c)` |\n| 152 | 임베딩 | 사전, 패딩, `nn.Embedding` |\n"
    "| 153 | 텍스트 분류 | 마스크 평균 |",
    [("시계열을 학습·테스트로 나누는 올바른 방법은?", ["무작위로 섞어서", "앞부분과 뒷부분으로", "홀짝으로", "나누지 않는다"], 1),
     ("문장 길이를 맞추기 위해 채우는 번호는?", ["0(`<pad>`)", "1(`<unk>`)", "-1", "사전 크기"], 0)],
    "시퀀스 분류와 패딩 도구",
    "다음 값 예측(회귀)뿐 아니라 시퀀스 전체에 레이블을 붙이는 **시퀀스 분류**도 같은 구조입니다. 마지막 출력 → 선형 층 → 클래스 로짓.\n\n"
    "길이가 다른 텐서 목록은 `nn.utils.rnn.pad_sequence(목록, batch_first=True)`로 한 번에 0을 채워 묶을 수 있습니다.",
    '''
    import torch
    from torch import nn

    seqs = [torch.tensor([3, 4, 5]), torch.tensor([6]), torch.tensor([7, 8])]
    print(nn.utils.rnn.pad_sequence(seqs, batch_first=True))
    cell = nn.LSTMCell(1, 2)
    print(cell.weight_ih.shape, cell.weight_hh.shape)
    ''',
    "도전 문제의 `nn.LSTMCell`은 한 시점만 계산하는 LSTM입니다. 가중치는 입력·망각·후보(g)·출력 게이트 순서로 4묶음이 세로로 붙어 있습니다.",
    "길이가 다른 시퀀스를 패딩하세요.", "첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    ["시퀀스 = 윈도우 → RNN/LSTM → 마지막 출력 → 선형 층.", "LSTM은 긴 의존성에 강하다.", "텍스트 = 사전 → 패딩 → 임베딩.",
     "다음 주: 학습된 모델을 저장하고 재사용하는 전이 학습."],
    [("`pad_sequence`가 채우는 기본값은?", ["0", "1", "-1", "평균"], 0),
     ("LSTMCell의 `weight_ih` 행 수가 은닉 크기의 4배인 이유는?", ["게이트·후보 4묶음", "층이 4개", "배치 4", "우연"], 0)],
    [
        X("d154_fill_1", "패딩 묶기",
          "정수 목록들을 텐서로 바꿔 `pad_sequence`로 묶은 결과를 반환하세요(배치 차원이 앞).", ["sequence"], 1,
          '''
          import torch
          from torch import nn


          def pad(lists):
              seqs = [torch.tensor(x) for x in lists]
              return nn.utils.rnn.pad_sequence(seqs, batch_first=True)
          ''', "pad", [[[[3, 4, 5], [6], [7, 8]]], [[[1], [2, 2, 2, 2]]]],
          ["길이가 다른 시퀀스를 0으로 채워 묶는 함수입니다.", "배치 차원을 앞에 두는 옵션입니다."],
          blanks=["pad_sequence", "batch_first=True"], tol=None),
        X("d154_code_1", "추세 분류 LSTM",
          "주어진 `trend_data(seed)`는 오르는 추세(1)와 내리는 추세(0)의 시퀀스 200개입니다. 앞 150개로 학습, 뒤 50개로 평가하세요. "
          "`torch.manual_seed(0)` 후 `TrendLSTM`과 `optim.Adam(lr=0.01)`, CrossEntropyLoss로 전체 배치를 `epochs`번 학습하고 "
          "`[마지막 학습 손실, 테스트 정확도]`(소수 넷째 자리)를 반환하세요.",
          ["lstm", "sequence", "training_loop"], 3,
          '''
          import torch
          from torch import nn, optim
          ''' + TREND_SRC + '''

          def train_trend(seed, epochs):
              X, y = trend_data(seed)
              torch.manual_seed(0)
              model = TrendLSTM()
              optimizer = optim.Adam(model.parameters(), lr=0.01)
              for _ in range(epochs):
                  loss = nn.CrossEntropyLoss()(model(X[:150]), y[:150])
                  optimizer.zero_grad()
                  loss.backward()
                  optimizer.step()
              with torch.no_grad():
                  acc = (model(X[150:]).argmax(dim=1) == y[150:]).float().mean()
              return [round(loss.item(), 4), round(acc.item(), 4)]
          ''', "train_trend", [[0, 60], [1, 40]],
          ["학습은 `X[:150]`, 평가는 `X[150:]`입니다.", "정확도는 `torch.no_grad()` 안에서 argmax를 비교해 구합니다."], tol=2e-3, tl=90),
        X("d154_code_2", "LSTM 셀 직접 계산(도전)",
          "`torch.manual_seed(seed)` 후 `nn.LSTMCell(1, 2)`를 만들고, 입력 `x`(값 하나)와 h = c = 0에서 한 시점을 직접 계산하세요. "
          "`gates = x @ W_ih.T + b_ih + h @ W_hh.T + b_hh`를 4등분(`chunk(4, dim=1)`)해 i, f, g, o로 쓰고, "
          "`c = σ(f)·c + σ(i)·tanh(g)`, `h = σ(o)·tanh(c)`입니다. `[h(소수 넷째 자리 리스트), LSTMCell 결과와 같은지]`를 반환하세요.",
          ["lstm"], 3,
          '''
          import torch
          from torch import nn


          def lstm_step(seed, x):
              torch.manual_seed(seed)
              cell = nn.LSTMCell(1, 2)
              inp = torch.tensor([[float(x)]])
              h = c = torch.zeros(1, 2)
              with torch.no_grad():
                  gates = inp @ cell.weight_ih.T + cell.bias_ih + h @ cell.weight_hh.T + cell.bias_hh
                  i, f, g, o = gates.chunk(4, dim=1)
                  c = torch.sigmoid(f) * c + torch.sigmoid(i) * torch.tanh(g)
                  h = torch.sigmoid(o) * torch.tanh(c)
                  h_ref, _ = cell(inp)
              return [[round(v, 4) for v in h[0].tolist()], torch.allclose(h, h_ref, atol=1e-6)]
          ''', "lstm_step", [[0, 1.0], [2, -0.5]],
          ["입력은 (1, 1) 모양 텐서로 만드세요.", "`cell(inp)`은 h와 c를 돌려주니 첫 번째 값과 비교합니다."], required=False),
    ], review_title="22주차 돌아보기")

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day148, day149, day150, day151, day152, day153, day154])
