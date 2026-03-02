"""A tiny DostLang-style language implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DostLangError(Exception):
    """Base exception for all language errors."""


class DostLangParseError(DostLangError):
    """Raised when parsing fails."""


class DostLangRuntimeError(DostLangError):
    """Raised when runtime execution fails."""


@dataclass
class Token:
    token_type: str
    value: str
    line: int
    col: int


@dataclass
class Literal:
    value: Any


@dataclass
class Variable:
    name: str


@dataclass
class UnaryOp:
    op: str
    expr: Any


@dataclass
class BinaryOp:
    left: Any
    op: str
    right: Any


@dataclass
class PrintStmt:
    expr: Any


@dataclass
class AssignStmt:
    name: str
    expr: Any
    declare: bool


@dataclass
class IfStmt:
    condition: Any
    then_body: list[Any]
    else_body: list[Any]


@dataclass
class WhileStmt:
    condition: Any
    body: list[Any]


@dataclass
class ExecutionResult:
    output: list[str]
    variables: dict[str, Any]


KEYWORDS = {
    "dost_bol",
    "yeh_ha",
    "agar",
    "warna",
    "jabtak",
    "sach",
    "jhoot",
    "aur",
    "ya",
    "nahi",
}


class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.idx = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._at_end():
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "#":
                self._skip_comment()
                continue
            if ch == "\n" or ch == ";":
                tokens.append(self._make_token("NEWLINE", "\n"))
                self._advance()
                continue
            if ch.isalpha() or ch == "_":
                tokens.append(self._identifier())
                continue
            if ch.isdigit():
                tokens.append(self._number())
                continue
            if ch == '"':
                tokens.append(self._string())
                continue

            two_char = ch + self._peek_next()
            if two_char in {"==", "!=", "<=", ">="}:
                token = self._make_token("SYMBOL", two_char)
                self._advance()
                self._advance()
                tokens.append(token)
                continue
            if ch in "+-*/(){}=<>" or ch == "!":
                tokens.append(self._make_token("SYMBOL", ch))
                self._advance()
                continue

            raise DostLangParseError(
                f"Unexpected character '{ch}' at line {self.line}, col {self.col}"
            )
        tokens.append(self._make_token("EOF", ""))
        return tokens

    def _identifier(self) -> Token:
        start_idx = self.idx
        start_line = self.line
        start_col = self.col
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        text = self.source[start_idx : self.idx]
        token_type = "KEYWORD" if text in KEYWORDS else "IDENT"
        return Token(token_type=token_type, value=text, line=start_line, col=start_col)

    def _number(self) -> Token:
        start_idx = self.idx
        start_line = self.line
        start_col = self.col
        while not self._at_end() and self._peek().isdigit():
            self._advance()
        text = self.source[start_idx : self.idx]
        return Token(token_type="INT", value=text, line=start_line, col=start_col)

    def _string(self) -> Token:
        start_line = self.line
        start_col = self.col
        self._advance()  # opening quote
        chars: list[str] = []
        while not self._at_end():
            ch = self._peek()
            if ch == '"':
                self._advance()
                break
            if ch == "\\":
                self._advance()
                if self._at_end():
                    raise DostLangParseError(
                        f"Unterminated string at line {start_line}, col {start_col}"
                    )
                esc = self._peek()
                mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                chars.append(mapping.get(esc, esc))
                self._advance()
                continue
            chars.append(ch)
            self._advance()
        else:
            raise DostLangParseError(
                f"Unterminated string at line {start_line}, col {start_col}"
            )

        return Token(token_type="STRING", value="".join(chars), line=start_line, col=start_col)

    def _make_token(self, token_type: str, value: str) -> Token:
        return Token(token_type=token_type, value=value, line=self.line, col=self.col)

    def _skip_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _peek(self) -> str:
        return self.source[self.idx]

    def _peek_next(self) -> str:
        if self.idx + 1 >= len(self.source):
            return "\0"
        return self.source[self.idx + 1]

    def _advance(self) -> None:
        if self._at_end():
            return
        if self.source[self.idx] == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.idx += 1

    def _at_end(self) -> bool:
        return self.idx >= len(self.source)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse_program(self, stop_on_block_end: bool = False) -> list[Any]:
        statements: list[Any] = []
        while not self._check("EOF"):
            self._consume_newlines()
            if stop_on_block_end and self._check_symbol("}"):
                break
            if self._check("EOF"):
                break
            statements.append(self._statement())
            self._consume_newlines()
        return statements

    def _statement(self) -> Any:
        if self._match_keyword("dost_bol"):
            return PrintStmt(self._expression())

        if self._match_keyword("yeh_ha"):
            name_token = self._consume("IDENT", "Expected variable name after 'yeh_ha'.")
            self._consume_symbol("=", "Expected '=' after variable name.")
            return AssignStmt(name=name_token.value, expr=self._expression(), declare=True)

        if self._match_keyword("agar"):
            condition = self._expression()
            then_body = self._block()
            else_body: list[Any] = []
            self._consume_newlines()
            if self._match_keyword("warna"):
                else_body = self._block()
            return IfStmt(condition=condition, then_body=then_body, else_body=else_body)

        if self._match_keyword("jabtak"):
            condition = self._expression()
            body = self._block()
            return WhileStmt(condition=condition, body=body)

        if self._check("IDENT") and self._check_next_symbol("="):
            name_token = self._advance()
            self._consume_symbol("=", "Expected '=' after variable name.")
            return AssignStmt(name=name_token.value, expr=self._expression(), declare=False)

        token = self._peek()
        raise DostLangParseError(
            f"Unexpected token '{token.value}' at line {token.line}, col {token.col}"
        )

    def _block(self) -> list[Any]:
        self._consume_newlines()
        self._consume_symbol("{", "Expected '{' to start block.")
        self._consume_newlines()
        body = self.parse_program(stop_on_block_end=True)
        self._consume_symbol("}", "Expected '}' to close block.")
        return body

    def _expression(self) -> Any:
        return self._or()

    def _or(self) -> Any:
        expr = self._and()
        while self._match_keyword("ya"):
            expr = BinaryOp(left=expr, op="ya", right=self._and())
        return expr

    def _and(self) -> Any:
        expr = self._equality()
        while self._match_keyword("aur"):
            expr = BinaryOp(left=expr, op="aur", right=self._equality())
        return expr

    def _equality(self) -> Any:
        expr = self._comparison()
        while self._match_symbol("==") or self._match_symbol("!="):
            op = self._previous().value
            expr = BinaryOp(left=expr, op=op, right=self._comparison())
        return expr

    def _comparison(self) -> Any:
        expr = self._term()
        while (
            self._match_symbol("<")
            or self._match_symbol("<=")
            or self._match_symbol(">")
            or self._match_symbol(">=")
        ):
            op = self._previous().value
            expr = BinaryOp(left=expr, op=op, right=self._term())
        return expr

    def _term(self) -> Any:
        expr = self._factor()
        while self._match_symbol("+") or self._match_symbol("-"):
            op = self._previous().value
            expr = BinaryOp(left=expr, op=op, right=self._factor())
        return expr

    def _factor(self) -> Any:
        expr = self._unary()
        while self._match_symbol("*") or self._match_symbol("/"):
            op = self._previous().value
            expr = BinaryOp(left=expr, op=op, right=self._unary())
        return expr

    def _unary(self) -> Any:
        if self._match_symbol("-"):
            return UnaryOp(op="-", expr=self._unary())
        if self._match_keyword("nahi"):
            return UnaryOp(op="nahi", expr=self._unary())
        return self._primary()

    def _primary(self) -> Any:
        if self._match("INT"):
            return Literal(int(self._previous().value))
        if self._match("STRING"):
            return Literal(self._previous().value)
        if self._match_keyword("sach"):
            return Literal(True)
        if self._match_keyword("jhoot"):
            return Literal(False)
        if self._match("IDENT"):
            return Variable(self._previous().value)
        if self._match_symbol("("):
            expr = self._expression()
            self._consume_symbol(")", "Expected ')' after expression.")
            return expr

        token = self._peek()
        raise DostLangParseError(
            f"Expected expression at line {token.line}, col {token.col}"
        )

    def _match(self, token_type: str) -> bool:
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _match_keyword(self, value: str) -> bool:
        if self._check("KEYWORD") and self._peek().value == value:
            self._advance()
            return True
        return False

    def _match_symbol(self, value: str) -> bool:
        if self._check("SYMBOL") and self._peek().value == value:
            self._advance()
            return True
        return False

    def _consume(self, token_type: str, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        token = self._peek()
        raise DostLangParseError(f"{message} Found '{token.value}' at {token.line}:{token.col}")

    def _consume_symbol(self, value: str, message: str) -> Token:
        if self._check("SYMBOL") and self._peek().value == value:
            return self._advance()
        token = self._peek()
        raise DostLangParseError(f"{message} Found '{token.value}' at {token.line}:{token.col}")

    def _consume_newlines(self) -> None:
        while self._match("NEWLINE"):
            pass

    def _check(self, token_type: str) -> bool:
        return self._peek().token_type == token_type

    def _check_symbol(self, value: str) -> bool:
        return self._check("SYMBOL") and self._peek().value == value

    def _check_next_symbol(self, value: str) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        next_token = self.tokens[self.current + 1]
        return next_token.token_type == "SYMBOL" and next_token.value == value

    def _advance(self) -> Token:
        if not self._check("EOF"):
            self.current += 1
        return self.tokens[self.current - 1]

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]


class Interpreter:
    def __init__(self, max_steps: int = 100_000):
        self.variables: dict[str, Any] = {}
        self.output: list[str] = []
        self.steps = 0
        self.max_steps = max_steps

    def execute(self, program: list[Any]) -> ExecutionResult:
        for stmt in program:
            self._execute_stmt(stmt)
        return ExecutionResult(output=self.output, variables=dict(self.variables))

    def _execute_stmt(self, stmt: Any) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise DostLangRuntimeError(
                f"Step limit exceeded ({self.max_steps}). Possible infinite loop."
            )

        if isinstance(stmt, PrintStmt):
            value = self._eval_expr(stmt.expr)
            self.output.append(str(value))
            return

        if isinstance(stmt, AssignStmt):
            value = self._eval_expr(stmt.expr)
            if not stmt.declare and stmt.name not in self.variables:
                raise DostLangRuntimeError(
                    f"Variable '{stmt.name}' is not declared. Use 'yeh_ha {stmt.name} = ...'"
                )
            self.variables[stmt.name] = value
            return

        if isinstance(stmt, IfStmt):
            branch = stmt.then_body if self._is_truthy(self._eval_expr(stmt.condition)) else stmt.else_body
            for item in branch:
                self._execute_stmt(item)
            return

        if isinstance(stmt, WhileStmt):
            while self._is_truthy(self._eval_expr(stmt.condition)):
                for item in stmt.body:
                    self._execute_stmt(item)
            return

        raise DostLangRuntimeError(f"Unsupported statement: {stmt!r}")

    def _eval_expr(self, expr: Any) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Variable):
            if expr.name not in self.variables:
                raise DostLangRuntimeError(f"Undefined variable '{expr.name}'.")
            return self.variables[expr.name]
        if isinstance(expr, UnaryOp):
            value = self._eval_expr(expr.expr)
            if expr.op == "-":
                return -self._ensure_number(value)
            if expr.op == "nahi":
                return not self._is_truthy(value)
            raise DostLangRuntimeError(f"Unsupported unary operator '{expr.op}'.")
        if isinstance(expr, BinaryOp):
            left = self._eval_expr(expr.left)
            right = self._eval_expr(expr.right)
            return self._apply_binary(left, expr.op, right)
        raise DostLangRuntimeError(f"Unsupported expression: {expr!r}")

    def _apply_binary(self, left: Any, op: str, right: Any) -> Any:
        if op == "+":
            return left + right
        if op == "-":
            return self._ensure_number(left) - self._ensure_number(right)
        if op == "*":
            return self._ensure_number(left) * self._ensure_number(right)
        if op == "/":
            denominator = self._ensure_number(right)
            if denominator == 0:
                raise DostLangRuntimeError("Division by zero.")
            return self._ensure_number(left) / denominator
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return self._ensure_number(left) < self._ensure_number(right)
        if op == "<=":
            return self._ensure_number(left) <= self._ensure_number(right)
        if op == ">":
            return self._ensure_number(left) > self._ensure_number(right)
        if op == ">=":
            return self._ensure_number(left) >= self._ensure_number(right)
        if op == "aur":
            return self._is_truthy(left) and self._is_truthy(right)
        if op == "ya":
            return self._is_truthy(left) or self._is_truthy(right)
        raise DostLangRuntimeError(f"Unsupported operator '{op}'.")

    def _ensure_number(self, value: Any) -> int | float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise DostLangRuntimeError(f"Expected number, got {type(value).__name__}.")
        return value

    def _is_truthy(self, value: Any) -> bool:
        return bool(value)


def parse_source(source: str) -> list[Any]:
    tokens = Tokenizer(source).tokenize()
    parser = Parser(tokens)
    return parser.parse_program()


def run_source(
    source: str, *, variables: dict[str, Any] | None = None, max_steps: int = 100_000
) -> ExecutionResult:
    program = parse_source(source)
    interpreter = Interpreter(max_steps=max_steps)
    if variables:
        interpreter.variables.update(variables)
    return interpreter.execute(program)
