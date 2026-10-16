"""Error types recorded for submissions and test results (01_design/db_schema.md §5)."""
from enum import StrEnum


class ErrorType(StrEnum):
    NONE = "none"
    SYNTAX_ERROR = "syntax_error"
    INDENTATION_ERROR = "indentation_error"
    NAME_ERROR = "name_error"
    TYPE_ERROR = "type_error"
    VALUE_ERROR = "value_error"
    INDEX_ERROR = "index_error"
    KEY_ERROR = "key_error"
    ATTRIBUTE_ERROR = "attribute_error"
    ZERO_DIVISION = "zero_division"
    EOF_ERROR = "eof_error"
    RUNTIME_ERROR = "runtime_error"
    WRONG_ANSWER = "wrong_answer"
    WRONG_EXCEPTION = "wrong_exception"
    TIMEOUT = "timeout"
    OUTPUT_LIMIT = "output_limit"
    UNFILLED_BLANK = "unfilled_blank"
    EMPTY_CODE = "empty_code"
    STATIC_CHECK_FAILED = "static_check_failed"
    NOT_RUN = "not_run"
    INTERNAL_ERROR = "internal_error"

    @property
    def label(self) -> str:
        return LABELS[self]

    @property
    def is_user_mistake(self) -> bool:
        """False for outcomes that should not count toward "repeated mistake" statistics."""
        return self not in (ErrorType.NONE, ErrorType.NOT_RUN, ErrorType.INTERNAL_ERROR)


LABELS: dict[ErrorType, str] = {
    ErrorType.NONE: "통과",
    ErrorType.SYNTAX_ERROR: "문법 오류",
    ErrorType.INDENTATION_ERROR: "들여쓰기 오류",
    ErrorType.NAME_ERROR: "이름 오류",
    ErrorType.TYPE_ERROR: "자료형 오류",
    ErrorType.VALUE_ERROR: "값 오류",
    ErrorType.INDEX_ERROR: "인덱스 범위 오류",
    ErrorType.KEY_ERROR: "키 오류",
    ErrorType.ATTRIBUTE_ERROR: "속성 오류",
    ErrorType.ZERO_DIVISION: "0으로 나누기",
    ErrorType.EOF_ERROR: "입력 부족",
    ErrorType.RUNTIME_ERROR: "기타 실행 오류",
    ErrorType.WRONG_ANSWER: "오답",
    ErrorType.WRONG_EXCEPTION: "예외 불일치",
    ErrorType.TIMEOUT: "시간 초과",
    ErrorType.OUTPUT_LIMIT: "출력 초과",
    ErrorType.UNFILLED_BLANK: "빈칸 미완성",
    ErrorType.EMPTY_CODE: "코드 없음",
    ErrorType.STATIC_CHECK_FAILED: "조건 미충족",
    ErrorType.NOT_RUN: "실행 안 됨",
    ErrorType.INTERNAL_ERROR: "내부 오류",
}

# Checked in order: the first exception class name found in the MRO wins,
# so subclasses (IndentationError) must come before their bases (SyntaxError).
_EXCEPTION_MAP: list[tuple[str, ErrorType]] = [
    ("IndentationError", ErrorType.INDENTATION_ERROR),  # includes TabError
    ("SyntaxError", ErrorType.SYNTAX_ERROR),
    ("NameError", ErrorType.NAME_ERROR),                # includes UnboundLocalError
    ("TypeError", ErrorType.TYPE_ERROR),
    ("ValueError", ErrorType.VALUE_ERROR),
    ("IndexError", ErrorType.INDEX_ERROR),
    ("KeyError", ErrorType.KEY_ERROR),
    ("AttributeError", ErrorType.ATTRIBUTE_ERROR),
    ("ZeroDivisionError", ErrorType.ZERO_DIVISION),
    ("EOFError", ErrorType.EOF_ERROR),
]

_HINTS: dict[ErrorType, str] = {
    ErrorType.SYNTAX_ERROR: "괄호·따옴표·콜론(:)이 빠지지 않았는지 확인하세요.",
    ErrorType.INDENTATION_ERROR: "블록 안의 코드는 같은 칸(보통 공백 4칸)만큼 들여써야 합니다.",
    ErrorType.NAME_ERROR: "변수·함수 이름의 철자와, 사용하기 전에 값을 정의했는지 확인하세요.",
    ErrorType.TYPE_ERROR: "서로 다른 자료형(예: 문자열과 숫자)을 함께 계산하고 있지 않은지 확인하세요.",
    ErrorType.VALUE_ERROR: "형 변환하려는 값의 형태가 올바른지 확인하세요 (예: int('abc')는 불가).",
    ErrorType.INDEX_ERROR: "인덱스는 0부터 시작하고, 길이보다 작아야 합니다.",
    ErrorType.ZERO_DIVISION: "나누는 값이 0이 되는 경우를 확인하세요.",
    ErrorType.EOF_ERROR: "input()을 입력 줄 수보다 많이 호출했습니다.",
    ErrorType.TIMEOUT: "반복문이 끝나는 조건이 있는지 확인하세요 (무한 루프).",
    ErrorType.OUTPUT_LIMIT: "출력이 너무 많습니다. 반복문 안의 print를 확인하세요.",
}


def classify_exception(mro: list[str]) -> ErrorType:
    """Map an exception (given as its MRO class names) to an ErrorType."""
    names = set(mro)
    for name, error_type in _EXCEPTION_MAP:
        if name in names:
            return error_type
    return ErrorType.RUNTIME_ERROR


def hint_for(error_type: ErrorType) -> str | None:
    """A short, generic Korean tip for an error type (never exercise-specific)."""
    return _HINTS.get(error_type)
