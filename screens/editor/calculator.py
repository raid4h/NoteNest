# screens/editor/calculator.py
# Powers the "grocery list" style auto-calculator: lines ending in a
# bare "=" get their arithmetic evaluated, and every line's trailing
# number contributes to a running grand total. Pure functions only --
# no widget/screen dependencies, same style as markup.py.

import ast
import re

# Matches a number (optionally with a leading $ and/or minus sign) at
# the very end of a line, e.g. "Milk 3.50" or "Refund -$2".
_TRAILING_NUMBER_PATTERN = re.compile(r'(\$)?\s*(-?\d+(?:\.\d+)?)\s*$')

# Matches a line that ends in a bare "=" with something ending in a
# digit or closing parenthesis right before it, e.g. "3.50 + 2 =".
_CALC_EXPR_PATTERN = re.compile(r'^(.*[\d\)])\s*=\s*$')

# Only digits, a decimal point, whitespace, and +-*/() are allowed in
# a calculator expression -- rejects anything else before it's even
# parsed, as a first line of defense.
_SAFE_EXPR_CHARS = re.compile(r'^[\d.+\-*/() ]+$')

# The only AST node types a calculator expression is allowed to
# contain. Anything outside this list (function calls, names,
# attribute access, etc.) gets rejected -- this is what makes
# evaluating user-typed text safe, unlike a raw eval().
_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd,
)


def _safe_eval_expr(expr):
    # Returns a float result, or None if the expression is invalid or
    # contains anything not on the allowed-node whitelist above.
    if not _SAFE_EXPR_CHARS.match(expr):
        return None
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            return None
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            return None

    try:
        return eval(compile(tree, "<calculator>", "eval"))
    except (ZeroDivisionError, OverflowError):
        return None


def format_calculated_number(value):
    # Whole numbers show without decimals (5 instead of 5.00);
    # everything else rounds to 2 decimal places.
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}"


def process_calculator_lines(text):
    """
    Returns (display_text, grand_total, uses_currency).

    display_text: same as the input, but any line ending in a bare
    "=" gets its result appended -- visual only, never written back
    into the note's actual stored content.

    grand_total: sum of one number per line across the whole note
    (either that line's own trailing number, or its calculated result
    if it was a "=" line) -- or None if no numbers were found at all.

    uses_currency: True if any matched number had a literal "$" in
    front of it, so the total can be shown with a "$" prefix too.
    """
    lines = text.split("\n")
    output_lines = []
    total = 0.0
    found_any = False
    uses_currency = False

    for line in lines:
        stripped = line.strip()

        # Skip lines containing an image or link marker entirely --
        # a photo's random filename could coincidentally end in a
        # digit and get misread as a price otherwise.
        if "{{img:" in line or "{{link:" in line:
            output_lines.append(line)
            continue

        calc_match = _CALC_EXPR_PATTERN.match(stripped)
        if calc_match:
            expr = calc_match.group(1).strip()
            result = _safe_eval_expr(expr)
            if result is not None:
                output_lines.append(f"{line.rstrip()} {format_calculated_number(result)}")
                total += result
                found_any = True
                continue
            # Looked like a calculator line but didn't evaluate safely
            # (e.g. malformed expression) -- leave it unchanged and
            # fall through to the trailing-number check below.

        output_lines.append(line)

        number_match = _TRAILING_NUMBER_PATTERN.search(stripped)
        if number_match:
            if number_match.group(1) == "$":
                uses_currency = True
            total += float(number_match.group(2))
            found_any = True

    display_text = "\n".join(output_lines)
    return display_text, (total if found_any else None), uses_currency