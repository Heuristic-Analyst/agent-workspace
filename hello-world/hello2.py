import sys


def greet(name="World"):
    return f"Hello, {name}!"


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "World"
    print(greet(name))
    print("Second hello world file, same idea, slightly different shape.")


if __name__ == "__main__":
    main()
