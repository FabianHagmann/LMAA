import os.path
import shutil
import subprocess
import uuid

from django.utils.datetime_safe import datetime

import utils.project_utils


class TestExecutionResponse:
    """
    Class for storing the result of a test execution
    """

    def __init__(self, result: bool, message: str) -> None:
        self.timestamp = datetime.now()
        self.result = result
        self.message = message

    def __str__(self) -> str:
        return f'[{self.timestamp}] {self.result} ({self.message})'

    def add_to_message(self, new_message: str) -> None:
        """
        add a given message to the existing message

        :param new_message: message to be added
        """

        self.message += new_message

    def set_result(self, new_result: bool) -> None:
        """
        set the result of the response object

        :param new_result: result to be set
        """

        self.result = new_result


class TestExecutionException(Exception):
    """
    Exception to handle all errors that may occur during test execution.

    May only be used by test-executors. Must always be caught by testexecutors and must never be thrown to
    be handled outside logic
    """
    pass


class ContainsTestExecutor:
    """
    Test executor for checking if a given solution contains a given phrase a given amount of times.
    """

    def execute_test(self, solution: str, phrases: dict[str, int]) -> TestExecutionResponse:
        """
        Execute the contains check

        :param solution: given solution to be checked
        :param phrases: dict of phrases:times to be contained
        :return: TestExecutionResponse containing status, timestamp and optional message if failed
        """

        response = TestExecutionResponse(True, '')
        for phrase, times in phrases.items():
            # for every phrase check
            message = self.__check_phrase__(solution, phrase, times)
            if message is not None:
                response.add_to_message(message)
                response.set_result(False)

        return response

    def __check_phrase__(self, solution: str, phrase: str, times: int) -> str | None:
        """
        Checks a single phrase

        :param solution: given solution to be checked
        :param phrase: phrase that is checks to be contained
        :param times: number of times the phrase has to be contained
        :return: error description if phrase does not appear exactly the right amount of times
        """

        count = solution.count(phrase)
        if count == times:
            return None
        return f'"{phrase}" appeared {count} times (not {times} times)'


class CompileTestExecutor:
    __test_parent_dir__ = os.path.join(utils.project_utils.find_root_path(__file__), 'scripts', 'testing', 'temp')

    def __init__(self) -> None:
        self.__build_test_directory_structure__()

    def execute_test(self, solution: str) -> TestExecutionResponse:
        """
        Executes a compile check for a given solution

        :param solution: given solution to be checked
        :return: TestExecutionResponse containing status, timestamp and optional message if failed
        """

        response = TestExecutionResponse(True, '')

        test_dir = self.__generate_test_dir_path__()
        try:
            test_file = self.__set_up_test_environment__(solution, test_dir)
            self.__execute_test_with_files__(test_file)
        except TestExecutionException as tee:
            response.set_result(False)
            response.add_to_message(tee.__str__())
        finally:
            self.__clean_up_test_environment__(test_dir)

        return response

    def __build_test_directory_structure__(self):
        """
        Create temporary general testing-dir if not exists

        Default path /scripts/testing/temp
        """

        if not os.path.exists(self.__test_parent_dir__):
            os.makedirs(self.__test_parent_dir__)

    def __set_up_test_environment__(self, solution: str, test_dir) -> str:
        """
        Create test-specific testing-dir with solution file in it

        :param solution: solution to be packed into a files
        :param test_dir: test-specific testing-dir to be created
        :return: path to the created solution file
        """

        # create testing directory
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # create solution file in testing directory
        java_classname = self.__get_java_class_name__(solution)
        if java_classname is None:
            raise TestExecutionException('Solution does not contain a valid classname')
        try:
            solution_file = open(os.path.join(test_dir, java_classname + '.java'), 'w')
        except OSError:
            raise TestExecutionException('Solution could not be created')
        solution_file.write(solution)

        return os.path.join(test_dir, java_classname + '.java')

    def __clean_up_test_environment__(self, test_dir):
        """
        Delete test-specific testing-dir after test completion

        :param test_dir: test-specific testing directory
        """

        shutil.rmtree(test_dir)

    def __generate_test_dir_path__(self) -> str:
        """
        Generate test-specific unique testing dir

        Name schema: /scripts/testing/temp/<uuid4>

        :return: path to the generated (not necessarily existing) testing directory
        """

        test_id = uuid.uuid4()
        return os.path.join(self.__test_parent_dir__, test_id.__str__())

    def __get_java_class_name__(self, code: str) -> str | None:
        """
        Fetch the correct java classname from a given code segment.

        If no classname of a public class is found, None is returned

        :param code: code segment to parsed for a classname
        :return: found classname of the public class or else None
        """

        try:
            class_index = code.find('public class')
            class_name = code[class_index + len('public class') + 1:] \
                .split('{')[0]
            class_name = class_name.rstrip()
            if class_name[0].isupper():
                return class_name
            else:
                return None
        except:
            return None

    def __execute_test_with_files__(self, test_file):
        """
        Executes the compile check on a given existing .java file

        May promote errors by raising TestExecutionExceptions

        :param test_file: path to the existing .java file containing the tested solution
        """
        cmd = f'javac {test_file}'

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if proc.returncode != 0:
                raise TestExecutionException(proc.stderr)

        except subprocess.CalledProcessError as e:
            raise TestExecutionException(e.output)


class UnitTestExecutor:
    __test_parent_dir__ = os.path.join(utils.project_utils.find_root_path(__file__), 'scripts', 'testing', 'temp')

    def __init__(self) -> None:
        self.__build_test_directory_structure__()

    def execute_test(self, solution: str, unit_test: str) -> TestExecutionResponse:
        """
        Executes a unit test check for a given solution and unit test

        :param solution: given solution to be checked
        :param unit_test: unit test used to check solution
        :return: TestExecutionResponse containing status, timestamp and optional message containing success rate and
        descriptions for failed tests
        """

        response = TestExecutionResponse(True, '')

        test_dir = self.__generate_test_dir_path__()
        try:
            test_files = self.__set_up_test_environment__(solution, unit_test, test_dir)
            result = self.__execute_test_with_files__(test_dir, test_files, self.__get_java_class_name__(unit_test))

            response.set_result(result[0])
            response.add_to_message(f'\t{result[1]}\n')
            response.add_to_message(f'\t{result[2]}')
        except TestExecutionException as tee:
            response.set_result(False)
            response.add_to_message(tee.__str__())
        finally:
            self.__clean_up_test_environment__(test_dir)

        return response

    def __build_test_directory_structure__(self):
        """
        Create temporary general testing-dir if not exists

        Default path /scripts/testing/temp
        """

        if not os.path.exists(self.__test_parent_dir__):
            os.makedirs(self.__test_parent_dir__)

    def __generate_test_dir_path__(self) -> str:
        """
        Generate test-specific unique testing dir

        Name schema: /scripts/testing/temp/<uuid4>

        :return: path to the generated (not necessarily existing) testing directory
        """

        test_id = uuid.uuid4()
        return os.path.join(self.__test_parent_dir__, test_id.__str__())

    def __set_up_test_environment__(self, solution: str, unit_test: str, test_dir) -> tuple[str, str, str]:
        """
        Create test-specific testing-dir with solution file, unit test file and 'junit-platform-console-standalone-1.9.2.jar'
        in it

        :param solution: solution to be packed into a file
        :param unit_test: unit test to packed into a file
        :param test_dir: test-specific testing-dir to be created
        :return: tuple containing paths to the solution file, unit test file and junit console jar
        """

        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # create solution and unit test files
        solution_classname = self.__get_java_class_name__(solution)
        unit_classname = self.__get_java_class_name__(unit_test)

        if solution_classname is None or unit_classname is None:
            raise TestExecutionException('Solution or unit-test does not contain a valid classname')
        if solution_classname == unit_classname:
            raise TestExecutionException('Solution and unit-test cannot have the same classname')

        try:
            solution_file = open(os.path.join(test_dir, solution_classname + '.java'), 'w')
            unit_file = open(os.path.join(test_dir, unit_classname + '.java'), 'w')
        except OSError:
            raise TestExecutionException('Solution or unit file could not be created')

        solution_file.write(solution)
        unit_file.write(unit_test)

        # copy junit console jar to the testing directory
        try:
            junit_jar_name = 'junit-platform-console-standalone-1.9.2.jar'
            shutil.copy(os.path.join(utils.project_utils.find_root_path(__file__), 'scripts', 'testing', 'helpers', junit_jar_name), test_dir)
        except IOError:
            raise TestExecutionException('Error when adding junit-jar to test environment')

        return os.path.join(test_dir, solution_classname + '.java'), os.path.join(test_dir, unit_classname + '.java'), \
            os.path.join(test_dir, 'junit-platform-console-standalone-1.9.2.jar')

    def __get_java_class_name__(self, code: str) -> str | None:
        """
        Fetch the correct java classname from a given code segment.

        If no classname of a public class is found, None is returned

        :param code: code segment to parsed for a classname
        :return: found classname of the public class or else None
        """

        try:
            class_index = code.find('public class')
            class_name = code[class_index + len('public class') + 1:] \
                .split('{')[0]
            class_name = class_name.rstrip()
            if class_name[0].isupper():
                return class_name
            else:
                return None
        except:
            return None

    def __clean_up_test_environment__(self, test_dir):
        """
        Delete test-specific testing-dir after test completion

        :param test_dir: test-specific testing directory
        """

        shutil.rmtree(test_dir)

    def __execute_test_with_files__(self, test_dir, test_files, test_classname) -> tuple[bool, str, str]:
        """
        Executes the compile check on a given existing .java file

        May promote errors by raising TestExecutionExceptions

        :param test_dir: path to the test directory containing all files from test_files
        :param test_files: paths to the existing solution java file, unit test java file and junit console jar
        :param test_classname: name of the public class of the unit test file
        :return: tuple containing the result as a bool, the pass ration of unit tests, and error messages of failed tests

        """

        working_dir = os.path.join(test_dir, 'target')
        os.mkdir(working_dir)

        try:
            # compile files together
            proc = subprocess.run(
                ['javac', '-d', working_dir, '-cp', test_files[2], test_files[0], test_files[1]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if proc.returncode != 0:
                raise TestExecutionException(proc.stderr)

            # execute unit test
            proc = subprocess.run(
                ['java', '-jar', test_files[2], '--class-path', working_dir, '-c', test_classname],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

        except subprocess.CalledProcessError as e:
            raise TestExecutionException(e.output)

        # read necessary information from process response
        num_tests = int(proc.stdout[proc.stdout.find('tests started') - 5:proc.stdout.find('tests started')].strip())
        num_successes = int(
            proc.stdout[proc.stdout.find('tests successful') - 5:proc.stdout.find('tests successful')].strip())
        message = ''
        search_index = 0
        while True:
            next_fail = proc.stdout[search_index:].find('[X]')
            if next_fail == -1:
                break

            next_fail_line_start = proc.stdout[:next_fail].rfind('--')
            next_fail_line_end = proc.stdout[next_fail:].find('\n') + next_fail
            next_fail_message = proc.stdout[next_fail_line_start + 7:next_fail_line_end]
            message += next_fail_message + '\n'
            search_index = next_fail + 5

        return num_tests == num_successes, f'{num_successes}/{num_tests}', message
