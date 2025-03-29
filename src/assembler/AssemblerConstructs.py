COMMENT_INDICATOR = "#"


class Program:
    def __init__(self, program_name):
        self.globalls = []
        self.program_name = program_name

    def _gen_globals(self):
        res = ""
        for globall in self.globalls:
            res += f"   .global {globall}\n"
        return res

    def __str__(self):
        return f"""   {self._gen_globals()}"""


###########################################


class UnaryOperator:
    def __init__(self):
        pass


class UnaryOperatorNeg(UnaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"UnaryOperatorNeg"

    def __str__(self):
        return "negl"


class UnaryOperatorNot(UnaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"UnaryOperatorNot"

    def __str__(self):
        return "notl"


###########################################


class BinaryOperator:
    def __init__(self):
        pass


class BinaryOperatorAdd(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorAdd"

    def __str__(self):
        return "addl"


class BinaryOperatorSub(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorSub"

    def __str__(self):
        return "subl"


class BinaryOperatorMult(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorMult"

    def __str__(self):
        return "imull"


class BinaryOperatorAnd(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorAnd"

    def __str__(self):
        return "andl"


class BinaryOperatorOr(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorOr"

    def __str__(self):
        return "orl"


class BinaryOperatorXor(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorXor"

    def __str__(self):
        return "xorl"


class BinaryOperatorLeftShiftLogical(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorLeftShiftLogical"

    def __str__(self):
        return "shll"


class BinaryOperatorRightShiftLogical(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorRightShiftLogical"

    def __str__(self):
        return "shrl"


class BinaryOperatorLeftShiftArithmetic(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorLeftShiftArithmetic"

    def __str__(self):
        return "shll"


class BinaryOperatorRightShiftArithmetic(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorRightShiftArithmetic"

    def __str__(self):
        return "sarl"


###########################################


class ConditionCode:
    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"


class ConditionCodeEqual(ConditionCode):
    def __init__(self):
        pass

    def __repr__(self):
        return f"e"


class ConditionCodeNotEqual(ConditionCode):
    def __init__(self):
        pass

    def __repr__(self):
        return f"ne"


class ConditionCodeLess(ConditionCode):
    def __init__(self):
        pass

    def __repr__(self):
        return f"l"


class ConditionCodeLessOrEqual(ConditionCode):

    def __init__(self):
        pass

    def __repr__(self):
        return f"le"


class ConditionCodeGreater(ConditionCode):
    def __init__(self):
        pass

    def __repr__(self):
        return f"g"


class ConditionCodeGreaterOrEqual(ConditionCode):
    def __init__(self):
        pass

    def __repr__(self):
        return f"ge"


###########################################


class Reg:
    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"


class RegAX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%eax"

    def _repr_single_byte(self):
        return "%al"


class RegR10(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%r10d"

    def _repr_single_byte(self):
        return "%r10b"


class RegDX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%edx"

    def _repr_single_byte(self):
        return "%dl"


class RegCX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%ecx"


class RegR11(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%r11d"

    def _repr_single_byte(self):
        return "%r11b"


###########################################


class Operand:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


class OperandImmediate(Operand):
    def __init__(self, value: int):
        super().__init__("Imm", value)

    def __str__(self):
        return f"${self.value}"


class OperandReg(Operand):
    def __init__(self, register: Reg):
        super().__init__("Reg", register)


class OperandPseudo(Operand):
    def __init__(self, indentifier: str):
        super().__init__("Pseudo", indentifier)


class OperandStack(Operand):
    def __init__(self, value: int):
        super().__init__("Stack", value)

    def __str__(self):
        return f"{self.value}(%rbp)"


###########################################


class Instruction:
    def __init__(self, command: str, arg_1=None, arg_2=None, comment: str = "") -> None:
        self.command = command
        self.arg_1 = arg_1
        self.arg_2 = arg_2
        self.comment = comment

    def __repr__(self) -> str:
        if not self.arg_1:
            return f"{self.__class__.__name__} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"
        elif not self.arg_2:
            return f"{self.__class__.__name__} {repr(self.arg_1)} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"
        else:
            return f"{self.__class__.__name__} {repr(self.arg_1)}, {repr(self.arg_2)} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"

    def __str__(self) -> str:

        return f"   {self.command}   {str(self.arg_1)}{str(self.arg_2)} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionMov(Instruction):
    def __init__(self, src: Operand, dst: Operand, comment: str = "") -> None:
        super().__init__("movl", src, dst, comment=comment)

    def __str__(self):
        return f"   movl   {self.arg_1}, {self.arg_2} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionBinary(Instruction):
    def __init__(
        self,
        binary_operator: BinaryOperator,
        src: Operand,
        dst: Operand,
        comment: str = "",
    ) -> None:
        super().__init__(binary_operator, src, dst, comment=comment)
        self.binary_operator = binary_operator

    def __str__(self):
        return f"   {str(self.binary_operator)}   {self.arg_1}, {self.arg_2} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"

    def __repr__(self):
        return f"InstructionBinary {self.binary_operator.__class__.__name__}, {self.arg_1}, {self.arg_2} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionCmp(Instruction):
    def __init__(self, src: Operand, dst: Operand, comment: str = "") -> None:
        super().__init__("cmpl", src, dst, comment=comment)

    def __str__(self):
        return f"   cmpl   {self.arg_1}, {self.arg_2} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionIdiv(Instruction):
    def __init__(self, src: Operand, comment: str = "") -> None:
        super().__init__("idivl", src, comment=comment)

    def __str__(self):
        return f"   idivl   {self.arg_1} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionCdq(Instruction):
    def __init__(self, comment: str = ""):
        super().__init__("cdq", comment=comment)

    def __str__(self):
        return f"   cdq {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionJmp(Instruction):
    def __init__(self, label: str, comment: str = "") -> None:
        super().__init__("jmp", label, comment=comment)

    def __str__(self):
        return f"   jmp    .L{self.arg_1} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionJmpCC(Instruction):
    def __init__(
        self, condition_code: ConditionCode, label: str, comment: str = ""
    ) -> None:
        super().__init__(condition_code, label, comment=comment)

    def __str__(self):
        return f"   j{self.command}   .L{self.arg_1} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionSetCC(Instruction):
    def __init__(
        self, condition_code: ConditionCode, argument: str, comment: str = ""
    ) -> None:
        super().__init__(condition_code, argument, comment=comment)

    def __str__(self):
        if isinstance(self.arg_1, Reg):
            return f"   set{self.command}   {self.arg_1._repr_single_byte()} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"
        return f"   set{self.command}   {self.arg_1} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionLabel(Instruction):
    def __init__(self, label: str, comment: str = "") -> None:
        super().__init__("Label", label, comment=comment)

    def __str__(self):
        return (
            f".L{self.arg_1}: {COMMENT_INDICATOR if self.comment else ''}{self.comment}"
        )


class InstructionUnary(Instruction):
    def __init__(
        self, unary_operator: UnaryOperator, operand: Operand, comment: str = ""
    ) -> None:
        super().__init__("Unary", unary_operator, operand, comment=comment)

    def __str__(self):
        return f"   {self.arg_1}   {self.arg_2} {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionAllocateStack(Instruction):
    def __init__(self, value, comment: str = "") -> None:
        super().__init__("Unary", value, comment=comment)

    def __str__(self):
        return f"   subq   ${self.arg_1}, %rsp {COMMENT_INDICATOR if self.comment else ''}{self.comment}"


class InstructionRet(Instruction):
    def __init__(self, comment: str = "") -> None:
        super().__init__("ret", comment=comment)

    # def __repr__(self):
    #     return f"InstructionRet[]"

    def __str__(self):
        return f"""   movq    %rbp, %rsp
   popq    %rbp
   ret"""


###########################################


class Function:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Func[{self.name}]"

    def __str__(self):
        return f"""
{self.name}:
   pushq   %rbp
   movq    %rsp, %rbp
"""


###########################################
