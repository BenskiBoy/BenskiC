from Tacky import *

from collections import defaultdict

###########################################


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


###########################################


class Operand:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__} {repr(self.value)}"


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
        if not self.arg_2:
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


class AssemblyParser:

    def __init__(self, program_name: str) -> None:
        self.program_name = program_name.replace("./", "")

        self.instructions = defaultdict(list)
        self.stack_tracker = defaultdict(dict)

    def generate_stack_pntr(self, pseudo_name: str, function_name: str = "") -> int:
        if (
            function_name not in self.stack_tracker.keys()
            or pseudo_name not in self.stack_tracker[function_name]
        ):
            self.stack_tracker[function_name][
                pseudo_name
            ] = -4  # if function name doesn't exist, neitgher will pseudoname
            return self.stack_tracker[function_name][pseudo_name]
        else:
            self.stack_tracker[function_name][pseudo_name] = (
                self.get_function_stack_size(function_name) - 4
            )
            return self.stack_tracker[function_name][pseudo_name]

        # if (
        #     function_name not in self.stack_tracker.keys()
        #     or pseudo_name not in self.stack_tracker[function_name]
        # ):
        #     self.stack_tracker[function_name][
        #         pseudo_name
        #     ] = -4  # if function name doesn't exist, neitgher will pseudoname
        #     return self.stack_tracker[function_name][pseudo_name]
        # else:
        #     self.stack_tracker[function_name][pseudo_name] -= 4
        #     return self.stack_tracker[function_name][pseudo_name]

    def get_function_stack_size(self, function_name: str) -> int:
        max_size = 0
        for pseudo_name in self.stack_tracker[function_name].keys():
            if self.stack_tracker[function_name][pseudo_name] > max_size:
                max_size = self.stack_tracker[function_name][pseudo_name]
        return max_size

    def _parse_unary(self, op: str) -> UnaryOperator:
        if op == "NEGATE":
            return UnaryOperatorNeg()
        elif op == "COMPLEMENT":
            return UnaryOperatorNot()
        else:
            raise Exception(f"Unknown Unary Op {op}")

    def _parse_operand(self, node: IRNode):
        if isinstance(node, IRConstantNode):
            return OperandImmediate(node.value)
        elif isinstance(node, IRVarNode):
            return OperandPseudo(node.src)

    def parse_unary(self, node: UnaryNode):

        return [
            InstructionMov(
                self._parse_operand(node.src), self._parse_operand(node.dst)
            ),
            InstructionUnary(self._parse_unary(node.op), self._parse_operand(node.dst)),
        ]

    def parse_return(self, node: IRReturnNode):
        return [
            InstructionMov(self._parse_operand(node.src), RegAX()),
            InstructionRet(),
        ]

    def parse_constant(self, node: IRConstantNode):
        self.instructions.append(OperandImmediate(node.value))

    def parse(self, tacky: list[IRNode]):

        current_func_name = ""
        for i, tack in enumerate(tacky):
            if isinstance(tack, IRProgramNode):
                self.instructions["__PROGRAM__"].append(Program(self.program_name))

            elif isinstance(tack, IRFunctionNode):

                self.instructions[tack.name].append(Function(tack.name))
                current_func_name = tack.name
                self.instructions["__PROGRAM__"][0].globalls.append(tack.name)

            elif isinstance(tack, IRReturnNode):
                self.instructions[current_func_name].extend(self.parse_return(tack))

            elif isinstance(tack, IRUnaryNode):
                self.instructions[current_func_name].extend(self.parse_unary(tack))

            else:
                raise Exception(f"Unknown IR {tack}")

        # Replace OperandPseudo with stack locations
        for j, func in enumerate(self.instructions.keys()):
            for i, inst in enumerate(self.instructions[func]):

                if isinstance(inst, InstructionMov):
                    if isinstance(inst.arg_1, OperandPseudo):

                        self.instructions[func][i].arg_1 = OperandStack(
                            self.generate_stack_pntr(inst.arg_1.value, func)
                        )
                    if isinstance(inst.arg_2, OperandPseudo):
                        self.instructions[func][i].arg_2 = OperandStack(
                            self.generate_stack_pntr(inst.arg_2.value, func)
                        )
                elif isinstance(inst, InstructionUnary):
                    if isinstance(inst.arg_2, OperandPseudo):
                        self.instructions[func][i].arg_2 = OperandStack(
                            self.generate_stack_pntr(inst.arg_2.value, func)
                        )

            # add stack allocation
            if func in self.stack_tracker.keys():
                self.instructions[func].insert(
                    1, InstructionAllocateStack(self.get_function_stack_size(func) + 4)
                )

            # fix invalid mov instructions (can't move stack values, need intermediary reg)
            for i, inst in enumerate(self.instructions[func]):
                if isinstance(inst, InstructionMov):
                    if isinstance(inst.arg_1, OperandStack) and isinstance(
                        inst.arg_2, OperandStack
                    ):

                        dest = inst.arg_2
                        self.instructions[func][i].arg_2 = RegR10()
                        self.instructions[func].insert(
                            i + 1, InstructionMov(RegR10(), dest)
                        )

    def pretty_print(self):
        for func in self.instructions.keys():
            for inst in self.instructions[func]:
                print(repr(inst))

    def generate(self):
        res = ""
        for func in self.instructions.keys():
            for instr in self.instructions[func]:
                res += str(instr) + "\n"

        res += '   .section .note.GNU-stack,"",@progbits\n'

        return res
