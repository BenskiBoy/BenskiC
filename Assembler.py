from Tacky import *

from collections import defaultdict

###########################################


class Program:
    def __init__(self):
        pass

    def __str__(self):
        return ".section .not.GNU-stack," ",@progbits"


###########################################


class Function:
    def __init__(self, name):
        self.name = name

    def set_stack_size(self, stack_size: int = 0):
        self.stack_size = stack_size

    def __repr__(self):
        return f"Func[{self.name}]"

    def __str__(self):
        return f"""
   .global {self.name}
{self.name}:
   pushq   %rbp
   movq    %rsp, %rbp
   subq    ${self.stack_size}, %rsp
"""


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
        return f"   {self.command} {str(self.arg_1)}, {str(self.arg_2)}"


class InstructionMov(Instruction):
    def __init__(self, src: Operand, dst: Operand) -> None:
        super().__init__("movl", src, dst)

    def __str__(self):
        return f"   movl   {self.arg_1}, {self.arg_2}"


class InstructionUnary(Instruction):
    def __init__(self, unary_operator: UnaryOperator, operand: Operand) -> None:
        super().__init__("Unary", unary_operator, operand)

    def __str__(self):
        return f"   {self.arg_1} {self.arg_2}"


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


class AssemblyParser:

    def __init__(self) -> None:
        self.instructions = []
        self.stack_counter = -4
        self.stack_tracker = {}

    def get_stack_pntr(self, pseudo_name=str) -> None:
        if pseudo_name not in self.stack_tracker:
            self.stack_tracker[pseudo_name] = self.stack_counter
            self.stack_counter -= 4
            return self.stack_tracker[pseudo_name]
        else:
            return self.stack_tracker[pseudo_name]

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

        self.instructions.append(
            InstructionMov(self._parse_operand(node.src), self._parse_operand(node.dst))
        )
        self.instructions.append(
            InstructionUnary(self._parse_unary(node.op), self._parse_operand(node.dst))
        )

    def parse_return(self, node: IRReturnNode):
        self.instructions.append(InstructionMov(self._parse_operand(node.src), RegAX()))
        self.instructions.append(InstructionRet())

    def parse_function(self, node: FunctionNode):
        self.instructions.append(Function(node.name))

    def parse_program(self, node: IRProgramNode):
        self.instructions.append(Program())

    def parse_constant(self, node: IRConstantNode):
        self.instructions.append(OperandImmediate(node.value))

    def parse(self, tacky: list[IRNode]):

        for i, tack in enumerate(tacky):
            if isinstance(tack, IRProgramNode):
                self.parse_program(tack)

            elif isinstance(tack, IRFunctionNode):
                self.parse_function(tack)

            elif isinstance(tack, IRReturnNode):
                self.parse_return(tack)

            elif isinstance(tack, IRUnaryNode):
                self.parse_unary(tack)
            else:
                raise Exception(f"Unknown IR {tack}")

        # Replace OperandPseudo with stack locations
        for i, inst in enumerate(self.instructions):
            if isinstance(inst, InstructionMov):
                if isinstance(inst.arg_1, OperandPseudo):
                    self.instructions[i].arg_1 = OperandStack(
                        self.get_stack_pntr(inst.arg_1.value)
                    )
                if isinstance(inst.arg_2, OperandPseudo):
                    self.instructions[i].arg_2 = OperandStack(
                        self.get_stack_pntr(inst.arg_2.value)
                    )
            elif isinstance(inst, InstructionUnary):
                if isinstance(inst.arg_2, OperandPseudo):
                    self.instructions[i].arg_2 = OperandStack(
                        self.get_stack_pntr(inst.arg_2.value)
                    )

        # add stack allocation
        # self.instructions.insert(1, InstructionAllocateStack(self.stack_counter + 4))

        # fix invalid mov instructions (can't move stack values, need intermediary reg)
        for i, inst in enumerate(self.instructions):
            if isinstance(inst, InstructionMov):
                if isinstance(inst.arg_1, OperandStack) and isinstance(
                    inst.arg_2, OperandStack
                ):
                    dest = inst.arg_2
                    self.instructions[i].arg_2 = RegR10()
                    self.instructions.insert(i + 1, InstructionMov(RegR10(), dest))
                    # self.instructions.insert(i, InstructionMov(inst.arg_1, RegR10()))
                    # self.instructions[i + 1].arg_2 = RegR10()
                    # self.instructions.insert(
                    #     i + 2, InstructionMov(RegR10(), inst.arg_2)
                    # )
                    # self.instructions.pop(i)

    def pretty_print(self):
        for inst in self.instructions:
            print(repr(inst))

    def generate(self):
        res = ""
        for instr in self.instructions:
            res += str(instr) + "\n"
        return res


# ASSEMBLY_NODE_LOOKUP = {
#     IRConstantNode: lambda self, node: self.parse_constant(node),
#     IRReturnNode: lambda self, node: self.parse_return(node),
#     IRUnaryNode: lambda self, node: self.parse_unary(node),
#     IRFunctionNode: lambda self, node: self.parse_function(node),
#     IRProgramNode: lambda self, node: self.parse_program(node),
# }


# class AsmParser:
#     def __init__(self, ast, input_file_name, debug) -> None:
#         self.ast = ast
#         self.assembly_parser = AssemblyParser()
#         self.input_file_name = input_file_name
#         self.debug = debug

#     def parse(self) -> list[str]:

#         def _parse(ast):

#             for child in ast.children:
#                 ASSEMBLY_NODE_LOOKUP[child.__class__](self.assembly_parser, child)
#                 if len(child.children) > 0:
#                     _parse(child)

#         _parse(self.ast)

#         return self.assembly_parser.instructions

#     def generate(self):

#         content = ""

#         content += f'  .file "{self.input_file_name}"\n'
#         content += f"  .text\n"

#         for glob in self.assembly_parser.globals:
#             content += f"  .global {glob.args[0]}\n"

#         for typ in self.assembly_parser.types:
#             content += f"  .type {typ.args[0]}, {typ.args[1]}\n"

#         for inst in self.assembly_parser.instructions:
#             if str(inst)[-1] == ":":
#                 content += str(inst) + "\n"
#             else:
#                 content += f"  {str(inst)}" + "\n"

#         content += f'  .ident  "GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0"\n'
#         content += f'  .section  .note.GNU-stack,"",@progbits\n'

#         return content
