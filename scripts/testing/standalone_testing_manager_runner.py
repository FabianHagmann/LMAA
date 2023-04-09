from scripts.testing.testing_executors import TestExecutionResponse
from scripts.testing.testing_manager import TestingManager

solution = 'public class Aufgabe {\
    public static String addSign(String text, char sign) {\
        StringBuilder sb = new StringBuilder();\
        for(int i = 0; i < text.length(); i++) {\
            for(int j = 0; j <= i; j++) {\
                sb.append(text.charAt(j));\
            }\
            if(i < text.length() - 1) {\
                sb.append(sign);\
            }\
        }\
        return sb.toString();\
    }\
}'

test = 'import org.junit.jupiter.api.Test;\
\
import static org.junit.jupiter.api.Assertions.assertEquals;\
\
public class AddSignTest {\
\
    @Test\
    public void testOne() {\
        String result = Aufgabe.addSign("Hello!", \'#\');\
        assertEquals(result, "H#e##l###l####o#####!");\
    }\
}'


def printResult(result: TestExecutionResponse) -> None:
    print('--------------------------------------------')
    print('Result:')
    print(f'\tPass: {result.result}')
    print(f'\tTime: {result.timestamp}')
    print(f'\tMessage:\n{result.message}')
    print('--------------------------------------------')

man = TestingManager()

response = man.solution_contains_multiple(solution, {'for': 2})
printResult(response)

response = man.solution_compiles(solution)
printResult(response)

response = man.solution_unit_test(solution, test)
printResult(response)