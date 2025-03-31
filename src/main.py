#!/home/benth/miniconda3/envs/main/bin/python

import click
from Lexer import Lexer
from SemanticAnalysis import SemanticAnalysis
from parser.Parser import Parser, pretty_print
from tacky.Tacky import Tacky
from assembler.Assembler import AssemblyParser
import subprocess


@click.command()
@click.argument("input_file", type=click.File("r"))
@click.option("--lex", is_flag=True, help="Lex the input file")
@click.option("--parse", is_flag=True, help="Parse the input file")
@click.option("--validate", is_flag=True, help="Parse the input file")
@click.option("--tacky", is_flag=True, help="Tacky the input file")
@click.option("--codegen", is_flag=True, help="Generate the AST")
@click.option("-s", is_flag=True, help="Generate assembly")
@click.option("--debug", is_flag=True, help="Debug")
def main(input_file, lex, parse, validate, tacky, codegen, s, debug):

    content = input_file.read()

    if lex:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

    elif parse:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

        parser = Parser(tokens, debug)
        ast = parser.parse()
        if debug:
            pretty_print(ast)

    elif validate:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

        parser = Parser(tokens, debug)
        ast = parser.parse()
        if debug:
            pretty_print(ast)

        semantic = SemanticAnalysis()
        ast = semantic.parse(ast)
        if debug:
            semantic.pretty_print(ast)

    elif tacky:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

        parser = Parser(tokens, debug)
        ast = parser.parse()
        if debug:
            pretty_print(ast)

        semantic = SemanticAnalysis()
        ast = semantic.parse(ast)
        if debug:
            semantic.pretty_print()

        tacky = Tacky(ast, debug)
        ir = tacky.emit_ir(ast)
        if debug:
            tacky.pretty_print(ir)

    elif codegen:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

        parser = Parser(tokens, debug)
        ast = parser.parse()
        if debug:
            pretty_print(ast)

        semantic = SemanticAnalysis()
        ast = semantic.parse(ast)
        if debug:
            semantic.pretty_print()

        tacky = Tacky(ast, debug)
        ir = tacky.emit_ir(ast)
        if debug:
            tacky.pretty_print(ir)

        assm = AssemblyParser(input_file.name.replace(".c", ".s"))
        assm.parse(ir)
        if debug:
            assm.pretty_print()

        # assembly = AsmParser(ast, input_file.name, debug)
        # assembly.parse()

    elif s:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

        parser = Parser(tokens, debug)
        ast = parser.parse()
        if debug:
            pretty_print(ast)

        semantic = SemanticAnalysis()
        ast = semantic.parse(ast)
        if debug:
            semantic.pretty_print()

        tacky = Tacky(ast, debug)
        ir = tacky.emit_ir(ast)
        if debug:
            tacky.pretty_print(ir)

        assm = AssemblyParser(input_file.name.replace(".c", ".s"))
        assm.parse(ir)

        if debug:
            assm.pretty_print()

        with open(input_file.name.replace(".c", ".s"), "w") as f:
            content = assm.generate()
            f.write(content)
        if debug:
            print(content)

    else:
        lexer = Lexer(content, debug)
        tokens = lexer.lex()
        if debug:
            print(str(lexer))

        parser = Parser(tokens, debug)
        ast = parser.parse()
        if debug:
            pretty_print(ast)

        semantic = SemanticAnalysis()
        ast = semantic.parse(ast)
        if debug:
            semantic.pretty_print()

        tacky = Tacky(ast, debug)
        ir = tacky.emit_ir(ast)
        if debug:
            tacky.pretty_print(ir)

        assm = AssemblyParser(input_file.name.replace(".c", ".s"))
        assm.parse(ir)
        with open(input_file.name.replace(".c", ".s"), "w") as f:
            content = assm.generate()
            f.write(content)
        if debug:
            print(content)

        output_file = input_file.name.replace(".c", "")
        subprocess.run(["gcc", input_file.name.replace(".c", ".s"), "-o", output_file])

    return 0


if __name__ == "__main__":
    main()
