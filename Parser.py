from typing import Self
from enum import Enum

from Lexer import Token


class UnaryOperatorNode(Enum):
    COMPLEMENT = "Complement"
    NEGATE = "Negate"


class BinaryOperatorNode(Enum):
    ADD = "Add"
    SUBTRACT = "Subtract"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"
    REMAINDER = "Remainder"
    AND = "And"
    OR = "Or"
    XOR = "Xor"
    LEFT_SHIFT_LOGICAL = "LeftShiftLogical"
    RIGHT_SHIFT_LOGICAL = "RightShiftLogical"
    LEFT_SHIFT_ARITHMETIC = "LeftShiftArithmetic"
    RIGHT_SHIFT_ARITHMETIC = "RightShiftArithmetic"


# TOKEN_PRECEDENCE = {
#     "ADD": 1,
#     "HYPHEN": 1,
#     "MULTIPLY": 2,
#     "DIVIDE": 2,
#     "REMAINDER": 2,
#     "LEFT_SHIFT": 3,
#     "RIGHT_SHIFT": 3,
#     "AND_BITWISE": 4,
#     "XOR_BITWISE": 5,
#     "OR_BITWISE": 6,
# }
TOKEN_PRECEDENCE = {
    "OR_BITWISE": 1,
    "XOR_BITWISE": 2,
    "AND_BITWISE": 3,
    "RIGHT_SHIFT": 4,
    "LEFT_SHIFT": 4,
    "ADD": 5,
    "HYPHEN": 5,
    "MULTIPLY": 6,
    "DIVIDE": 6,
    "REMAINDER": 6,
}

BINARY_TOKENS = [
    Token("ADD"),
    Token("HYPHEN"),
    Token("MULTIPLY"),
    Token("DIVIDE"),
    Token("REMAINDER"),
    Token("AND_BITWISE"),
    Token("OR_BITWISE"),
    Token("XOR_BITWISE"),
    Token("LEFT_SHIFT"),
    Token("RIGHT_SHIFT"),
]


class ASTNode:
    def __init__(
        self,
        type: str,
        children: list[Self] = [],
        operator: UnaryOperatorNode | BinaryOperatorNode = None,
    ) -> None:
        self.type = type
        self.children = children
        self.operator = operator

    def add_child(self, child: Self) -> None:
        self.children.append(child)

    def __repr__(self) -> str:
        if self.operator:
            return f"{self.type} {self.operator}, ({self.children})"
        return f"{self.type}({self.children})"


class Statement(ASTNode):
    def __init__(self, type, child: ASTNode) -> None:
        super().__init__(type, [child])


class ReturnNode(Statement):
    def __init__(self, child: ASTNode) -> None:
        super().__init__("RETURN", child)


class ExpressionNode(ASTNode):
    def __init__(
        self,
        type,
        children: list[ASTNode],
        operator: UnaryOperatorNode | BinaryOperatorNode = None,
    ) -> None:
        super().__init__(type, children, operator)


class ConstantNode(ExpressionNode):
    def __init__(self, value: str) -> None:
        super().__init__("CONSTANT", [])
        self.value = value

    def __repr__(self) -> str:
        return f"""CONSTANT({self.value})"""


class UnaryNode(ExpressionNode):
    def __init__(
        self,
        expression: ExpressionNode,
        operator: UnaryOperatorNode,
    ) -> None:
        super().__init__("UNARY", [expression], operator)
        self.operator = operator


class BinaryNode(ExpressionNode):
    def __init__(
        self,
        operator: BinaryOperatorNode,
        expression_1: ExpressionNode,
        expression_2: ExpressionNode,
    ) -> None:
        super().__init__("BinaryNode", [expression_1, expression_2], operator)
        self.operator = operator


class FunctionNode(ASTNode):
    def __init__(self, return_type: str, name: str, body: list[ASTNode]) -> None:
        super().__init__("FUNCTION", body)
        self.return_type = return_type
        self.name = name

    def assemble(self) -> str:
        return f"""
        .global {self.name}
        {self.name}:
        """

    def __str__(self) -> str:
        return f"""
Function(
    name = {self.name}
    return_type = {self.return_type}
    body = """


class ProgramNode(ASTNode):
    def __init__(self) -> None:
        super().__init__("PROGRAM", [])

    def __str__(self) -> str:
        return f"""
Program("""


class Parser:
    def __init__(self, tokens: list[Token], debug) -> None:
        self.tokens = tokens
        self.ast = None
        self.debug = debug

    def parse(self) -> ASTNode:
        program_node = ProgramNode()

        tokens = self.tokens
        while tokens:
            tokens, function = self.parse_function(tokens)
            program_node.add_child(function)

        return program_node

    def parse_function(self, tokens: list[Token]) -> ASTNode:

        tokens, _ = self.expect(Token("INT"), tokens)
        return_type = "INT"
        tokens, token = self.expect(Token("IDENTIFIER"), tokens)
        name = token.value

        tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

        tokens, _ = self.expect(Token("VOID"), tokens)
        tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
        tokens, _ = self.expect(Token("OPEN_BRACE"), tokens)
        tokens, body = self.parse_statement(tokens)
        tokens, _ = self.expect(Token("CLOSE_BRACE"), tokens)
        return tokens, FunctionNode(return_type, name, [body])

    def parse_statement(self, tokens) -> ASTNode:
        tokens, _ = self.expect(Token("RETURN"), tokens)
        tokens, expression = self.parse_expression(tokens)
        tokens, _ = self.expect(Token("SEMICOLON"), tokens)

        return tokens, ReturnNode(expression)

    def parse_expression(self, tokens, min_prec: int = 0) -> ASTNode:
        tokens, left = self.parse_factor(tokens)
        next_token = tokens[0]

        while (
            next_token in BINARY_TOKENS
            and TOKEN_PRECEDENCE[next_token.type] >= min_prec
        ):
            operator = self.parse_binary_operator(
                next_token, left.operator == UnaryOperatorNode.NEGATE
            )
            tokens = tokens[1:]
            tokens, right = self.parse_expression(
                tokens, TOKEN_PRECEDENCE[next_token.type] + 1
            )
            left = BinaryNode(operator, left, right)

            next_token = tokens[0]

        return tokens, left

    def parse_factor(self, tokens) -> ASTNode:
        next_token = tokens[0]
        if next_token.type == "CONSTANT":
            return self.parse_constant(tokens)
        elif next_token.type == "TILDA" or next_token.type == "HYPHEN":
            tokens, operator = self.parse_unary(tokens)
            tokens, inner_expression = self.parse_factor(tokens)

            return tokens, UnaryNode(inner_expression, operator)

        elif next_token.type == "OPEN_PAREN":
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            return tokens, expression
        else:
            raise Exception(f"Syntax Error: Unexpected token {next_token}")

    def parse_unary(self, tokens) -> tuple[list[ASTNode], str]:
        unary_operator = None
        if tokens[0].value == "~":
            unary_operator = UnaryOperatorNode.COMPLEMENT
        elif tokens[0].value == "-":
            unary_operator = UnaryOperatorNode.NEGATE
        else:
            raise Exception(f"Unrecognised Unary Operator {tokens[0].value}")

        return tokens[1:], unary_operator

    def parse_binary_operator(
        self, token, negated_left_value
    ) -> (
        BinaryOperatorNode
    ):  # if the left value is negated, then the left shift is arithmetic
        if token == Token("ADD"):
            return BinaryOperatorNode.ADD
        elif token == Token("HYPHEN"):
            return BinaryOperatorNode.SUBTRACT
        elif token == Token("MULTIPLY"):
            return BinaryOperatorNode.MULTIPLY
        elif token == Token("DIVIDE"):
            return BinaryOperatorNode.DIVIDE
        elif token == Token("REMAINDER"):
            return BinaryOperatorNode.REMAINDER
        elif token == Token("AND_BITWISE"):
            return BinaryOperatorNode.AND
        elif token == Token("OR_BITWISE"):
            return BinaryOperatorNode.OR
        elif token == Token("XOR_BITWISE"):
            return BinaryOperatorNode.XOR
        elif token == Token("LEFT_SHIFT"):
            if negated_left_value:
                return BinaryOperatorNode.LEFT_SHIFT_ARITHMETIC
            else:
                return BinaryOperatorNode.LEFT_SHIFT_LOGICAL
        elif token == Token("RIGHT_SHIFT"):
            if negated_left_value:
                return BinaryOperatorNode.RIGHT_SHIFT_ARITHMETIC
            else:
                return BinaryOperatorNode.RIGHT_SHIFT_LOGICAL
        else:
            raise Exception(f"Unrecognised Binary Operator {token.value}")

    def parse_constant(self, tokens) -> ASTNode:
        tokens, constant_token = self.expect(Token("CONSTANT"), tokens)

        return tokens, ConstantNode(constant_token.value)

    def expect(self, expected: Token, tokens: list[Token]) -> bool:
        if tokens[0].type == expected.type:
            return tokens[1:], tokens[0]
        raise Exception(f"Syntax Error: Expected {expected}, got {tokens[0]}")


def pretty_print(ast, level: int = 0, prev_content: str = "  ") -> None:
    print(" " * level + str(ast))
    print(" " * level + str(ast.children))
