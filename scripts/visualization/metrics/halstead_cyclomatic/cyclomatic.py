"""
calculate cyclomatic complexity

Source: https://github.com/MohamedSaidSallam/halstead_cyclomatic
"""

import json
import os

import utils.project_utils

branchOperators = os.path.join(utils.project_utils.find_root_path(__file__), 'scripts', 'visualization', 'metrics',
                               'branchOperators.json')
with open(branchOperators, 'r', encoding='utf-8') as branchOperatorsJson:
    branchOperators = set(json.load(branchOperatorsJson))


def calculate_cyclomatic(operators):
    """_summary_

    Args:
        operators (dictionary operator:count): dictionary of operators and their count

    Returns:
        int: cyclomatic complexity
    """
    return sum([operators[cyc_operator]
                for cyc_operator in branchOperators if cyc_operator in operators], start=1)
