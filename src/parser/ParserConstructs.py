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


class ProgramNode(ASTNode):
    def __init__(self) -> None:
        super().__init__("PROGRAM", [])

    def __str__(self) -> str:
        return f"""
Program("""


class ReturnNode(ASTNode):
    def __init__(self, child: ASTNode) -> None:
        super().__init__("RETURN", [child])


class ExpressionNode(ASTNode):
    def __init__(
        self,
        type,
        children: list[ASTNode],
        operator: UnaryOperatorNode | BinaryOperatorNode = None,
    ) -> None:
        super().__init__(type, children, operator)


class Statement(ASTNode):
    def __init__(self, type, child: ReturnNode | ExpressionNode | None) -> None:
        super().__init__(type, [child])


class DeclarationNode(ASTNode):
    def __init__(self, identifier: str, expression: ExpressionNode | None) -> None:
        super().__init__("DECLARATION", [expression])
        self.identifier = identifier

    def __repr__(self) -> str:
        return f"DECLARATION({self.identifier} {self.children[0]})"


class BlockItemNode(ASTNode):
    def __init__(self, child: Statement | DeclarationNode) -> None:
        super().__init__(type, [child])
        self.child = child

    def __repr__(self) -> str:
        return f"BLOCK_ITEM({self.child})"


class FunctionNode(ASTNode):
    def __init__(self, return_type: str, name: str, body: list[BlockItemNode]) -> None:
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


class ConstantNode(ExpressionNode):
    def __init__(self, value: str) -> None:
        super().__init__("CONSTANT", [])
        self.value = value

    def __repr__(self) -> str:
        return f"""CONSTANT({self.value})"""


class VarNode(ExpressionNode):
    def __init__(self, identifier: str) -> None:
        super().__init__("VARIABLE", [])
        self.identifier = identifier

    def __repr__(self) -> str:
        return f"""VARIABLE({self.identifier})"""


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


class AssignmentNode(ExpressionNode):
    def __init__(self, lvalue: ExpressionNode, rvalue: ExpressionNode) -> None:
        super().__init__("ASSIGNMENT", [lvalue, rvalue])

    def __repr__(self) -> str:
        return f"ASSIGNMENT({self.children[0]}, {self.children[1]})"
