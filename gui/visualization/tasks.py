import os
import statistics

from gui.assignments.models import Assignment, Solution
from scripts.visualization.metrics import metrics_manager as manager
from utils import project_utils


def generate_similarity_report_for_export():
    # generate folder and file
    __generate_report_folder__()
    similarity_report_file = open(os.path.join(__get_report_folder_path__(), 'similarity_report.csv'), 'w')

    # generate header
    header_columns = ['semester', 'sheet', 'task', 'subtask', 'ass_length', 'tags'
                      'ass_cosine_avg', 'ass_cosine_min', 'ass_cosine_max', 'ass_cosine_med',
                      'ass_mccabe_mean', 'ass_mccabe_sd', 'ass_mccabe_min', 'ass_mccabe_max', 'ass_mccabe_med',
                      'ass_halstead_mean', 'ass_halstead_sd', 'ass_halstead_min', 'ass_halstead_max',
                      'ass_halstead_med']
    similarity_report_file.write(__generate_report_line__(header_columns, ';'))

    # instantiate necessary variables
    man = manager.MetricsManager()

    for assignment in Assignment.objects.all().order_by('semester', 'sheet', 'task', 'subtask'):
        # prepare values
        raw_solutions = Solution.objects.filter(assignment=assignment).all()
        prepared_solutions = __prepare_assignment_solutions_single_source__(raw_solutions)
        prepared_solutions_with_ids = __prepare_assignment_solutions_single_source_with_ids__(raw_solutions)

        ass_cosine_matrix = man.similarity_cosine_single_source(prepared_solutions)
        ass_mccabe_complexity = man.mccabe_complexity(prepared_solutions_with_ids)
        ass_halstead_complexity = man.halstead_metrics(prepared_solutions_with_ids)
        ass_halstead_volume_list = __prepare_halstead_volume_list__(ass_halstead_complexity)

        # calculate values
        ass_length = len(assignment.assignment)
        tags = ''
        tag_list = assignment.tags.all()
        for i in range(0, len(tag_list) - 1):
            tags += (tag_list[i].name + ',')
        tags += ('' + tag_list[len(tag_list) - 1].name)
        ass_cosine_avg = man.similarity_cosine_average(raw_solutions.count(), ass_cosine_matrix)
        ass_cosine_min = man.similarity_cosine_min(ass_cosine_matrix)
        ass_cosine_max = man.similarity_cosine_max(ass_cosine_matrix)
        ass_cosine_med = man.similarity_cosine_median(raw_solutions.count(), ass_cosine_matrix)
        ass_mccabe_mean = statistics.mean(ass_mccabe_complexity.values())
        ass_mccabe_sd = statistics.stdev(ass_mccabe_complexity.values())
        ass_mccabe_min = min(ass_mccabe_complexity.values())
        ass_mccabe_max = max(ass_mccabe_complexity.values())
        ass_mccabe_med = statistics.median(ass_mccabe_complexity.values())
        ass_halstead_mean = statistics.mean(ass_halstead_volume_list)
        ass_halstead_sd = statistics.stdev(ass_halstead_volume_list)
        ass_halstead_min = min(ass_halstead_volume_list)
        ass_halstead_max = max(ass_halstead_volume_list)
        ass_halstead_med = statistics.median(ass_halstead_volume_list)

        # write line
        line_columns = [assignment.semester, assignment.sheet, assignment.task, assignment.subtask, ass_length, tags,
                        ass_cosine_avg, ass_cosine_min, ass_cosine_max, ass_cosine_med,
                        ass_mccabe_mean, ass_mccabe_sd, ass_mccabe_min, ass_mccabe_max, ass_mccabe_med,
                        ass_halstead_mean, ass_halstead_sd, ass_halstead_min, ass_halstead_max, ass_halstead_med]
        similarity_report_file.write(__generate_report_line__(line_columns, ';'))


def __generate_report_folder__() -> None:
    report_folder_path = __get_report_folder_path__()
    if not os.path.exists(report_folder_path):
        os.makedirs(report_folder_path)


def __get_report_folder_path__() -> str:
    return os.path.join(project_utils.find_root_path(__file__), 'data', 'reports')


def __generate_report_line__(columns: list[any], delimiter: str) -> str:
    line = ''
    for i in range(0, len(columns) - 1):
        if __isfloat__(columns[i]):
            line += ('' + format(columns[i], '.3f') + delimiter)
        elif columns[i] is None:
            line += delimiter
        else:
            line += (columns[i] + delimiter)
    if __isfloat__(columns[len(columns) - 1]):
        line += ('' + format(columns[len(columns) - 1], '.3f') + '\n')
    elif columns[len(columns) - 1] is None:
        line += delimiter
    else:
        line += ('' + columns[len(columns) - 1] + '\n')
    return line


def __prepare_assignment_solutions_single_source__(solutions):
    prepared_solutions = []
    for solution in solutions:
        prepared_solutions.append(solution.solution)
    return prepared_solutions


def __prepare_assignment_solutions_single_source_with_ids__(solutions):
    prepared_solutions = {}
    for solution in solutions:
        prepared_solutions.__setitem__(solution.id, solution.solution)
    return prepared_solutions


def __prepare_halstead_volume_list__(ass_halstead_complexity):
    volume_list = []
    for metric in ass_halstead_complexity.values():
        volume_list.append(metric.get('Program Volume'))
    return volume_list


def __isfloat__(num):
    if num is None:
        return False
    try:
        float(num)
        return True
    except ValueError:
        return False
