from enum import Enum
from typing import Self

import sys

sys.path.append("..")
from Lexer import Token


class UnaryOperatorNode(Enum):
    COMPLEMENT = "Complement"
    NEGATE = "Negate"
    NOT = "Not"


class BinaryOperatorNode(Enum):
    ADD = "Add"
    SUBTRACT = "Subtract"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"
    REMAINDER = "Remainder"
    AND_BITWISE = "AndBitwise"
    OR_BITWISE = "OrBitwise"
    XOR_BITWISE = "XorBitwise"
    LEFT_SHIFT_LOGICAL = "LeftShiftLogical"
    RIGHT_SHIFT_LOGICAL = "RightShiftLogical"
    LEFT_SHIFT_ARITHMETIC = "LeftShiftArithmetic"
    RIGHT_SHIFT_ARITHMETIC = "RightShiftArithmetic"
    AND_LOGICAL = "AndLogical"
    OR_LOGICAL = "OrLogical"
    EQUAL = "Equal"
    NOT_EQUAL = "NotEqual"
    LESS_THAN = "LessThan"
    GREATER_THAN = "GreaterThan"
    LESS_OR_EQUAL = "LessOrEqual"
    GREATER_OR_EQUAL = "GreaterOrEqual"


NON_SHORT_CIRCUIT_BINARY_OPERATORS = [
    BinaryOperatorNode.ADD,
    BinaryOperatorNode.SUBTRACT,
    BinaryOperatorNode.MULTIPLY,
    BinaryOperatorNode.DIVIDE,
    BinaryOperatorNode.REMAINDER,
    BinaryOperatorNode.AND_BITWISE,
    BinaryOperatorNode.OR_BITWISE,
    BinaryOperatorNode.XOR_BITWISE,
    BinaryOperatorNode.LEFT_SHIFT_LOGICAL,
    BinaryOperatorNode.RIGHT_SHIFT_LOGICAL,
    BinaryOperatorNode.LEFT_SHIFT_ARITHMETIC,
    BinaryOperatorNode.RIGHT_SHIFT_ARITHMETIC,
    BinaryOperatorNode.EQUAL,
    BinaryOperatorNode.NOT_EQUAL,
    BinaryOperatorNode.LESS_THAN,
    BinaryOperatorNode.GREATER_THAN,
    BinaryOperatorNode.LESS_OR_EQUAL,
    BinaryOperatorNode.GREATER_OR_EQUAL,
]
SHORT_CIRCUIT_BINARY_OPERATORS = [
    BinaryOperatorNode.AND_LOGICAL,
    BinaryOperatorNode.OR_LOGICAL,
]


TOKEN_PRECEDENCE = {
    "EQUAL_ASSIGN": 3,
    "OR_LOGICAL": 4,
    "AND_LOGICAL": 5,
    "OR_LOGICAL": 6,
    "AND_LOGICAL": 7,
    "OR_BITWISE": 8,
    "XOR_BITWISE": 9,
    "AND_BITWISE": 10,
    "NOT_EQUAL": 11,
    "EQUAL": 11,
    "GREATER_OR_EQUAL": 12,
    "LESS_OR_EQUAL": 12,
    "GREATER_THAN": 12,
    "LESS_THAN": 12,
    "RIGHT_SHIFT": 13,
    "LEFT_SHIFT": 13,
    "ADD": 14,
    "HYPHEN": 14,
    "MULTIPLY": 15,
    "DIVIDE": 15,
    "REMAINDER": 15,
}

BINARY_TOKENS = [
    Token("EQUAL_ASSIGN"),
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
    Token("AND_LOGICAL"),
    Token("OR_LOGICAL"),
    Token("EQUAL"),
    Token("NOT_EQUAL"),
    Token("LESS_OR_EQUAL"),
    Token("GREATER_OR_EQUAL"),
    Token("LESS_THAN"),
    Token("GREATER_THAN"),
]


class ProgramNode:
    def __init__(self) -> None:
        self.functions = []

    def repr(self) -> str:
        return f"PROGRAM({self.functions})"

    def __str__(self) -> str:
        return f"""
Program("""


class ExpressionNode:
    def __init__(
        self,
    ):
        pass

    def __repr__(self) -> str:
        return f"EXPRESSION({self.operator})"


class ReturnNode:
    def __init__(self, exp: ExpressionNode) -> None:
        self.exp = exp

    def __repr__(self):
        return f"RETURN({self.exp})"


class Statement:
    def __init__(self, child: ReturnNode | ExpressionNode | None) -> None:
        self.child = child

    def __repr__(self):
        return f"STATEMENT({self.child})"


class DeclarationNode:
    def __init__(self, identifier: str, exp: ExpressionNode | None) -> None:
        self.identifier = identifier
        self.exp = exp

    def __repr__(self) -> str:
        return f"DECLARATION({self.identifier} {self.exp})"


class BlockItemNode:
    def __init__(self, child: Statement | DeclarationNode) -> None:
        self.child = child

    def __repr__(self) -> str:
        return f"BLOCK_ITEM({self.child})"


class FunctionNode:
    def __init__(
        self, return_type: str, name: str, block_items: list[BlockItemNode]
    ) -> None:
        self.return_type = return_type
        self.name = name
        self.block_items = block_items

    def assemble(self) -> str:
        return f"""
        .global {self.name}
        {self.name}:
        """

    def __repr__(self):
        return f"FUNCTION({self.name} {self.return_type} {self.block_items})"

    def __str__(self) -> str:
        return f"""
Function(
    name = {self.name}
    return_type = {self.return_type}
    body = """


class ConstantNode(ExpressionNode):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"""CONSTANT({self.value})"""


class VarNode(ExpressionNode):
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def __repr__(self) -> str:
        return f"""VARIABLE({self.identifier})"""


class UnaryNode(ExpressionNode):
    def __init__(
        self,
        exp: ExpressionNode,
        operator: UnaryOperatorNode,
    ) -> None:
        self.exp = exp
        self.operator = operator

    def __repr__(self):
        return f"UNARY({self.operator} {self.exp})"


class BinaryNode(ExpressionNode):
    def __init__(
        self,
        operator: BinaryOperatorNode,
        exp_1: ExpressionNode,
        exp_2: ExpressionNode,
    ) -> None:
        self.operator = operator
        self.exp_1 = exp_1
        self.exp_2 = exp_2

    def __repr__(self):
        return f"BINARY({self.operator} {self.exp_1} {self.exp_2})"


class AssignmentNode(ExpressionNode):
    def __init__(self, lvalue: ExpressionNode, rvalue: ExpressionNode) -> None:
        self.lvalue = lvalue
        self.rvalue = rvalue

    def __repr__(self) -> str:
        return f"ASSIGNMENT({self.lvalue}, {self.rvalue})"
