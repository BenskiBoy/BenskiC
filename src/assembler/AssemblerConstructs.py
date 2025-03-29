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


class RegR10(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%r10d"


class RegDX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%edx"


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
    def __init__(self, command: str, arg_1=None, arg_2=None) -> None:
        self.command = command
        self.arg_1 = arg_1
        self.arg_2 = arg_2

    def __repr__(self) -> str:
        if not self.arg_1:
            return f"{self.__class__.__name__}"
        elif not self.arg_2:
            return f"{self.__class__.__name__} {repr(self.arg_1)}"
        else:
            return f"{self.__class__.__name__} {repr(self.arg_1)}, {repr(self.arg_2)}"

    def __str__(self) -> str:

        return f"   {self.command}   {str(self.arg_1)}{str(self.arg_2)}"


class InstructionMov(Instruction):
    def __init__(self, src: Operand, dst: Operand) -> None:
        super().__init__("movl", src, dst)

    def __str__(self):
        return f"   movl   {self.arg_1}, {self.arg_2}"


class InstructionBinary(Instruction):
    def __init__(
        self, binary_operator: BinaryOperator, src: Operand, dst: Operand
    ) -> None:
        super().__init__(binary_operator, src, dst)
        self.binary_operator = binary_operator

    def __str__(self):
        return f"   {str(self.binary_operator)}   {self.arg_1}, {self.arg_2}"

    def __repr__(self):
        return f"InstructionBinary {self.binary_operator.__class__.__name__}, {self.arg_1}, {self.arg_2}"


class InstructionCmp(Instruction):
    def __init__(self, src: Operand, dst: Operand) -> None:
        super().__init__("cmpl", src, dst)

    def __str__(self):
        return f"   cmpl   {self.arg_1}, {self.arg_2}"


class InstructionIdiv(Instruction):
    def __init__(self, src: Operand) -> None:
        super().__init__("idivl", src)

    def __str__(self):
        return f"   idivl   {self.arg_1}"


class InstructionCdq(Instruction):
    def __init__(self):
        super().__init__("cdq")

    def __str__(self):
        return "   cdq"


class InstructionJmp(Instruction):
    def __init__(self, label: str) -> None:
        super().__init__("jmp", label)

    def __str__(self):
        return f"   jmp    .L{self.arg_1}"


class InstructionJmpCC(Instruction):
    def __init__(self, condition_code: ConditionCode, label: str) -> None:
        super().__init__(condition_code, label)

    def __str__(self):
        return f"   j{self.command}   .L{self.arg_1}"


class InstructionSetCC(Instruction):
    def __init__(self, condition_code: ConditionCode, label: str) -> None:
        super().__init__(condition_code, label)

    def __str__(self):
        return f"   set{self.command}   {self.arg_1}"


class InstructionLabel(Instruction):
    def __init__(self, label: str) -> None:
        super().__init__("Label", label)

    def __str__(self):
        return f".L{self.arg_1}:"


class InstructionUnary(Instruction):
    def __init__(self, unary_operator: UnaryOperator, operand: Operand) -> None:
        super().__init__("Unary", unary_operator, operand)

    def __str__(self):
        return f"   {self.arg_1}   {self.arg_2}"


class InstructionAllocateStack(Instruction):
    def __init__(self, value) -> None:
        super().__init__("Unary", value)

    def __str__(self):
        return f"   subq   ${self.arg_1}, %rsp"


class InstructionRet(Instruction):
    def __init__(self) -> None:
        super().__init__("ret")

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
