import re

TOKENS = [
    (r"[a-zA-Z_]\w*\b", "IDENTIFIER"),
    (r"[0-9]+\b", "CONSTANT"),
    (r"int\b", "INT"),
    (r"void\b", "VOID"),
    (r"return\b", "RETURN"),
    (r"\(", "OPEN_PAREN"),
    (r"\)", "CLOSE_PAREN"),
    (r"\{", "OPEN_BRACE"),
    (r"\}", "CLOSE_BRACE"),
    (r";", "SEMICOLON"),
    (r"~", "TILDA"),
    (r"-", "HYPHEN"),
    (r"--", "DOUBLE_HYPHEN"),
    (r"\+", "ADD"),
    (r"\*", "MULTIPLY"),
    (r"\/", "DIVIDE"),
    (r"\%", "REMAINDER"),
    (r"&", "AND_BITWISE"),
    (r"\|", "OR_BITWISE"),
    (r"\^", "XOR_BITWISE"),
    (r"<", "LESS_THAN"),
    (r"<<", "LEFT_SHIFT"),
    (r">", "GREATER_THAN"),
    (r">>", "RIGHT_SHIFT"),
    (r"!", "NOT"),
    (r"&&", "AND_LOGICAL"),
    (r"\|\|", "OR_LOGICAL"),
    (r"==", "EQUAL"),
    (r"!=", "NOT_EQUAL"),
    (r"<=", "LESS_OR_EQUAL"),
    (r">=", "GREATER_OR_EQUAL"),
]

KEYWORDS = ["INT", "VOID", "RETURN"]


class Token:
    def __init__(self, type: str, value: str = "") -> None:
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, [  {self.value}  ])"

    def __str__(self) -> str:
        return f"Token({self.type}, [  {self.value}  ])"

    def __eq__(self, other) -> bool:
        return self.type == other.type


class Lexer:
    def __init__(self, content: str, debug: bool) -> None:
        self.content = content.replace("\t", "  ")
        self.tokens = []
        self.debug = debug

    def __repr__(self):
        content = ""
        for token in self.tokens:
            content += str(token) + "\n"
        return content

    def lex(self) -> list[Token]:
        while self.content != "":

            # skip whitespace
            if self.content[0] in [" ", "\n", "\r\n", "\r"]:
                self.content = self.content[1:]

            # skip comments
            elif self.content[0:2] == "//":
                self.content = self.content.split("\n", 1)[1]

            # skip multiline comments
            elif self.content[0:2] == "/*":
                self.content = self.content.split("*/", 1)[1]

            # skip hash functions...for now!
            elif self.content[0] == "#":
                self.content = self.content.split("\n", 1)[1]

            else:

                # Find matching tokens
                matches = []
                for token in TOKENS:
                    regex = token[0]
                    match = re.match(regex, self.content)
                    if match:
                        matches.append((match.group(), token[1]))

                if matches:
                    matched_keyword = False

                    # find longest match at start of input for any regex
                    # if keyword and identifier match, choose keyword
                    if len(matches) > 1:
                        for match in matches:
                            if match[1] in KEYWORDS:
                                self.tokens.append(Token(match[1], match[0]))
                                self.content = self.content[len(match[0]) :]
                                matched_keyword = True

                    if not matched_keyword:
                        match = max(matches, key=lambda x: len(x[0]))
                        self.tokens.append(Token(match[1], match[0]))
                        self.content = self.content[len(match[0]) :]

                else:
                    print(self.content)
                    raise Exception("Invalid token")
        return self.tokens
