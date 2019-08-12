from CHECLabPySB.d190730_pedestal import Test
from subprocess import call


def process(r0, tcal):
    generate_ped = f"generate_ped -i {r0} -o {tcal} -t"
    call(generate_ped, shell=True)


def main():
    file = Test()
    process(file.r0, file.tcal)


if __name__ == '__main__':
    main()
