import subprocess
import shlex
import sys
import argparse

def execute(cmd):
    if not cmd:
        return 
    output = subprocess.check_output(shlex.split(cmd), stderr = subprocess.STDOUT)
    return output.decode()

def arguments():
    parser = argparse.ArgumentParser(description=  "pass the argument -o with the python execution with the desired name as the second argument for the desired output")
    parser.add_argument("-o", "--Output", help = "Show output")
    args = parser.parse_args()
    if args.Output:
        print("Never gonna give you up , Never gonna let you down...", end= "\n" )
        print(f"Ha!....got you {args.Output}")


def main():
    # n = len(sys.argv)
    # print(f"This code is run on the file : {sys.argv[0]}")
    # print(sys.argv)
    arguments()

if __name__ == '__main__':
    main()