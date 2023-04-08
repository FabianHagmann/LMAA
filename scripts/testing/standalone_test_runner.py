from scripts.testing.testing_executors import CompileTestExecutor, UnitTestExecutor

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

compileTester = CompileTestExecutor()

result = compileTester.execute_test(solution)

print('--------------------------------------------')
print('Compile Result:')
print(f'\tPass: {result.result}')
print(f'\tTime: {result.timestamp}')
print(f'\tMessage: {result.message}')
print('--------------------------------------------')


unitTester = UnitTestExecutor()

result = unitTester.execute_test(solution, test)

print('--------------------------------------------')
print('Compile Result:')
print(f'\tPass: {result.result}')
print(f'\tTime: {result.timestamp}')
print(f'\tMessage:\n{result.message}')
print('--------------------------------------------')