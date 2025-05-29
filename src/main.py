def main():
    print("Welcome to the Python Learning Project!")
    print("This project will help you learn the basics of Python programming.")
    
    # Example of a basic function
    def add_numbers(a, b):
        return a + b

    # Example usage of the function
    num1 = 5
    num2 = 10
    result = add_numbers(num1, num2)
    print(f"The sum of {num1} and {num2} is {result}.")

    # Example of a loop
    print("Let's count from 1 to 5:")
    for i in range(1, 6):
        print(i)

    # Example of a conditional statement
    age = 18
    if age >= 18:
        print("You are an adult.")
    else:
        print("You are a minor.")

if __name__ == "__main__":
    main()