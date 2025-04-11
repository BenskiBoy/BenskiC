from enum import Enum
from typing import Self

import sys

sys.path.append("..")
from Lexer import Token


class UnaryOperatorNode(Enum):
    COMPLEMENT = "Complement"
    NEGATE = "Negate"
    NOT = "Not"
    INCREMENT = "Increment"
    DECREMENT = "Decrement"


class EqualAssignOperatorNode(Enum):
    EQUAL_ASSIGN = "EqualAssign"
    ADD_ASSIGN = "AddAssign"
    SUB_ASSIGN = "SubAssign"
    MULT_ASSIGN = "MultAssign"
    DIV_ASSIGN = "DivAssign"
    REM_ASSIGN = "RemAssign"
    AND_ASSIGN = "AndAssign"
    OR_ASSIGN = "OrAssign"
    XOR_ASSIGN = "XorAssign"
    LEFT_SHIFT_ASSIGN = "LeftShiftAssign"
    RIGHT_SHIFT_ASSIGN = "RightShiftAssign"


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
    ADD_ASSIGN = "AddAssign"
    SUB_ASSIGN = "SubAssign"
    MULT_ASSIGN = "MultAssign"
    DIV_ASSIGN = "DivAssign"
    REM_ASSIGN = "RemAssign"
    AND_ASSIGN = "AndAssign"
    OR_ASSIGN = "OrAssign"
    XOR_ASSIGN = "XorAssign"
    LEFT_SHIFT_ASSIGN = "LeftShiftAssign"
    RIGHT_SHIFT_ASSIGN = "RightShiftAssign"


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
    "ADD_ASSIGN": 3,
    "SUB_ASSIGN": 3,
    "MULT_ASSIGN": 3,
    "DIV_ASSIGN": 3,
    "REM_ASSIGN": 3,
    "AND_ASSIGN": 3,
    "OR_ASSIGN": 3,
    "XOR_ASSIGN": 3,
    "LEFT_SHIFT_ASSIGN": 3,
    "RIGHT_SHIFT_ASSIGN": 3,
    "QUESTION_MARK": 4,
    "OR_LOGICAL": 5,
    "AND_LOGICAL": 6,
    "OR_LOGICAL": 7,
    "AND_LOGICAL": 8,
    "OR_BITWISE": 9,
    "XOR_BITWISE": 10,
    "AND_BITWISE": 11,
    "NOT_EQUAL": 12,
    "EQUAL": 12,
    "GREATER_OR_EQUAL": 13,
    "LESS_OR_EQUAL": 13,
    "GREATER_THAN": 13,
    "LESS_THAN": 13,
    "RIGHT_SHIFT": 14,
    "LEFT_SHIFT": 14,
    "ADD": 15,
    "HYPHEN": 15,
    "MULTIPLY": 16,
    "DIVIDE": 16,
    "REMAINDER": 16,
    "INCREMENT": 17,
    "DOUBLE_HYPHEN": 17,
}

UNARY_TOKENS = [
    Token("TILDA"),
    Token("HYPHEN"),
    Token("NOT"),
    Token("INCREMENT"),
    Token("DOUBLE_HYPHEN"),
]

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
    Token("LEFT_SHIFT_ASSIGN"),
    Token("RIGHT_SHIFT_ASSIGN"),
    Token("ADD_ASSIGN"),
    Token("SUB_ASSIGN"),
    Token("MULT_ASSIGN"),
    Token("DIV_ASSIGN"),
    Token("REM_ASSIGN"),
    Token("AND_ASSIGN"),
    Token("OR_ASSIGN"),
    Token("XOR_ASSIGN"),
    Token("QUESTION_MARK"),
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


class LabeledStatementNode(Statement):
    """Represents a label attached to a statement."""

    def __init__(self, label: str, child: ReturnNode | ExpressionNode | None):
        super().__init__(child)
        self.label = label

    def __str__(self):
        return f"LABELED_STATEMENT({self.label}: {self.child})"

    def __repr__(self):
        return f"LABELED_STATEMENT({self.label}: {self.child})"


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


class GotoNode:
    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self):
        return f"GOTO({self.label})"


class IfNode:
    def __init__(
        self, condition: ExpressionNode, then: Statement, else_: Statement = None
    ) -> None:
        self.condition = condition
        self.then = then
        self.else_ = else_

    def __repr__(self):
        return f"IF({self.condition}, {self.then}, {self.else_})"


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
        postfix: bool = False,
    ) -> None:
        self.exp = exp
        self.operator = operator
        self.postfix = postfix

    def __repr__(self):
        return f"UNARY({self.operator} {self.exp} {"POSTFIX" if self.postfix else "PREFIX"})"


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
    def __init__(
        self,
        lvalue: ExpressionNode,
        rvalue: ExpressionNode,
        type: EqualAssignOperatorNode = EqualAssignOperatorNode.EQUAL_ASSIGN,
    ) -> None:
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.type = type

    def __repr__(self) -> str:
        return f"ASSIGNMENT({self.type} {self.lvalue}, {self.rvalue})"


class ConditionalNode(ExpressionNode):
    def __init__(
        self, condition: ExpressionNode, then: ExpressionNode, else_: ExpressionNode
    ) -> None:
        self.condition = condition
        self.then = then
        self.else_ = else_

    def __repr__(self) -> str:
        return f"CONDITION({self.condition}, {self.then}, {self.else_})"
