from scripts.testing.testing_executors import CompileTestExecutor

solution = 'public class Aufgabe {\
    public static void main(String[] args) {\
        String text = "Eine entsprechende und geeignete Sprache.";\
        int i = 0;\
        öwhile (i < text.length()) {\
            if ((i+1) % 3 == 0 && text.charAt(i) != \'e\') {\
                System.out.print(text.charAt(i));\
            }\
            i++;\
        }\
        if (i == 0) {\
            System.out.print("Kein gesuchtes Zeichen im String!");\
        }\
    }\
}'

tester = CompileTestExecutor()

result = tester.execute_test(solution)

print('--------------------------------------------')
print('Results:')
print(f'\tPass: {result.result}')
print(f'\tTime: {result.timestamp}')
print(f'\tMessage: {result.message}')
print('--------------------------------------------')
