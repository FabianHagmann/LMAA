import os
import statistics

from gui.assignments.models import Assignment, Solution
from gui.testing.models import ContainsTestcase, CompilesTestresult, UnitTestresult, ContainsTestresult
from scripts.visualization.metrics import metrics_manager as manager
from utils import project_utils


def generate_similarity_report_for_export():
    """
    function for generating and exporting the similarity report

    generates the report and exports it into the file /data/reports/similarity_report.csv
    """

    # generate folder and file
    __generate_report_folder__()
    similarity_report_file = open(os.path.join(__get_report_folder_path__(), 'similarity_report.csv'), 'w')

    # generate header
    header_columns = ['semester', 'sheet', 'task', 'subtask', 'ass_length', 'tags',
                      'ass_cosine_avg', 'ass_cosine_min',
                      'ass_cosine_max', 'ass_cosine_med',
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
        ass_mccabe_med = statistics.median_low(ass_mccabe_complexity.values())
        ass_halstead_mean = statistics.mean(ass_halstead_volume_list)
        ass_halstead_sd = statistics.stdev(ass_halstead_volume_list)
        ass_halstead_min = min(ass_halstead_volume_list)
        ass_halstead_max = max(ass_halstead_volume_list)
        ass_halstead_med = statistics.median_low(ass_halstead_volume_list)

        # write line
        line_columns = [assignment.semester, assignment.sheet, assignment.task, assignment.subtask, ass_length, tags,
                        ass_cosine_avg, ass_cosine_min, ass_cosine_max, ass_cosine_med,
                        ass_mccabe_mean, ass_mccabe_sd, ass_mccabe_min, ass_mccabe_max, ass_mccabe_med,
                        ass_halstead_mean, ass_halstead_sd, ass_halstead_min, ass_halstead_max, ass_halstead_med]
        similarity_report_file.write(__generate_report_line__(line_columns, ';'))


def generate_success_report_for_export():
    """
    function for generating and exporting the success report

    generates the report and exports it into the file /data/reports/success_report.csv
    """

    # generate folder and file
    __generate_report_folder__()
    similarity_report_file = open(os.path.join(__get_report_folder_path__(), 'success_report.csv'), 'w')

    # generate header
    header_columns = ['semester', 'sheet', 'task', 'subtask', 'tags',
                      'sol_num', 'comp', 'unit']
    distinct_times = ContainsTestcase.objects.order_by('times').values('times').distinct()
    for times in distinct_times:
        header_columns.append('cont_' + str(times['times']))
    similarity_report_file.write(__generate_report_line__(header_columns, ';'))

    # instantiate necessary variables
    man = manager.MetricsManager()
    count_sol = 1
    last_assignment = None

    for sol in Solution.objects.order_by('assignment__semester', 'assignment__sheet', 'assignment__task',
                                         'assignment__subtask', 'timestamp'):
        # update sol counter (reset if new assignment is reached)
        count_sol += 1
        if last_assignment is None or sol.assignment.id is not last_assignment.id:
            count_sol = 1
        last_assignment = sol.assignment

        # get data of solution
        tags = ''
        tag_list = sol.assignment.tags.all()
        for i in range(0, len(tag_list) - 1):
            tags += (tag_list[i].name + ',')
        tags += ('' + tag_list[len(tag_list) - 1].name)

        # get most current compiles testresult for solution
        try:
            comp = CompilesTestresult.objects.filter(solution=sol).order_by('-timestamp').first()
            if comp is not None:
                current_comp = comp.result
            else:
                current_comp = None
        except CompilesTestresult.DoesNotExist:
            current_comp = None

        # get most current unit testresult for solution
        try:
            unit = UnitTestresult.objects.filter(solution=sol).order_by('-timestamp').first()
            if unit is not None:
                current_unit = unit.success_testcases / unit.total_testcases
            else:
                current_unit = None
        except UnitTestresult.DoesNotExist:
            current_unit = None

        # get contains testresults differences in vectors for all distinct "times"
        current_contains = []
        for i in range(len(distinct_times)):
            contains_diffs_with_times = []
            contains_testcases_with_times = ContainsTestcase.objects.filter(assignment=sol.assignment,
                                                                            times=distinct_times[i]['times'])
            if contains_testcases_with_times.count() < 1:
                current_contains.append('')
                continue
            for testcase in contains_testcases_with_times:
                try:
                    contains_for_testcase = ContainsTestresult.objects.filter(solution=sol, testcase=testcase).order_by(
                        '-timestamp').first()
                    if contains_for_testcase is not None:
                        current_contains_for_testcase = abs(
                            contains_for_testcase.count_wanted - contains_for_testcase.count_found)
                    else:
                        current_contains_for_testcase = None
                except ContainsTestresult.DoesNotExist:
                    current_contains_for_testcase = None
                contains_diffs_with_times.append(current_contains_for_testcase)

            if len(contains_diffs_with_times) == 0:
                current_contains.append('')
            elif len(contains_diffs_with_times) == 1:
                current_contains.append('(' + str(contains_diffs_with_times[0]) + ')')
            else:
                temp = '('
                for diff in contains_diffs_with_times:
                    temp += ('' + str(diff) + ',')
                temp = temp[0:(len(temp) - 1)]
                temp += ')'
                current_contains.append(temp)

        # write line
        line_columns = [sol.assignment.semester, sol.assignment.sheet, sol.assignment.task, sol.assignment.subtask,
                        tags,
                        count_sol, current_comp, current_unit]
        for i in range(0, len(distinct_times)):
            line_columns.append(current_contains[i])
        similarity_report_file.write(__generate_report_line__(line_columns, ';'))


def __generate_report_folder__() -> None:
    """
    Creates the report folder "/data/reports" if it does not exist
    """
    report_folder_path = __get_report_folder_path__()
    if not os.path.exists(report_folder_path):
        os.makedirs(report_folder_path)


def __get_report_folder_path__() -> str:
    """
    Build the report folder path "/data/reports/"
    :return: path as a string
    """
    return os.path.join(project_utils.find_root_path(__file__), 'data', 'reports')


def __generate_report_line__(columns: list[any], delimiter: str) -> str:
    """
    Generate a CSV line with the given values and delimiters
    :param columns: vales for CSV line. Can be float, String or None
    :param delimiter: delimiter used for the CSV line
    :return: generated CSV line as string
    """
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
    """
    Converts a queryset of solutions into an array
    :param solutions: queryset of Solutions
    :return: converted array
    """

    prepared_solutions = []
    for solution in solutions:
        prepared_solutions.append(solution.solution)
    return prepared_solutions


def __prepare_assignment_solutions_single_source_with_ids__(solutions):
    """
    Converts a queryset of solutions into a dict mapped by the solutions' id
    :param solutions: queryset of Solutions
    :return: converted dict
    """

    prepared_solutions = {}
    for solution in solutions:
        prepared_solutions.__setitem__(solution.id, solution.solution)
    return prepared_solutions


def __prepare_halstead_volume_list__(ass_halstead_complexity):
    """
    Convert the halstead metrics into an array of values
    :param ass_halstead_complexity: halstead metrics dict exported from metrics_manager
    :return: converted array of program volumes
    """

    volume_list = []
    for metric in ass_halstead_complexity.values():
        volume_list.append(metric.get('Program Volume'))
    return volume_list


def __isfloat__(num):
    """
    checks if the given obj is a float
    :param num: object to be checked
    :return: true if it is a float, otherwise false
    """

    if num is None:
        return False
    try:
        float(num)
        return True
    except ValueError:
        return False
