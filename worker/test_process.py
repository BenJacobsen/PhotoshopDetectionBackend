import sys

if len(sys.argv) == 2 and sys.argv[1] == "fail":
    raise Exception("Failed to process image")
else:
    print("50")