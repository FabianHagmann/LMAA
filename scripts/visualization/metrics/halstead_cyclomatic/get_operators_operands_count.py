"""
gets operators and operands count for the given tokens

Source: https://github.com/MohamedSaidSallam/halstead_cyclomatic
"""

import json
import os

import utils.project_utils

operands = os.path.join(utils.project_utils.find_root_path(__file__), 'scripts', 'visualization', 'metrics',
                        'operands.json')
with open(operands, 'r', encoding='utf-8') as operandsJson:
    OPERANDS = set(json.load(operandsJson))


def get_operators_operands_count(tokens):
    """_summary_

    Args:
        tokens (javalang tokens): source code tokens parsed by javalang

    Returns:
        tuple:
            - dictionary(operand: count): dictionary of operands in the tokens and their count
            - dictionary(operator: count): dictionary of operators in the tokens and their count
    """

    operands = {}
    operators = {}

    for token in tokens:
        value = token.value

        if token.__class__.__name__ in OPERANDS:
            operands[value] = operands.get(value, 0) + 1
        else:
            operators[value] = operators.get(value, 0) + 1

    return operators, operands
