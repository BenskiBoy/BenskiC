from enum import Enum
from typing import Self

import sys

sys.path.append("..")
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
