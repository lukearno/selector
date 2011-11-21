"""(Re)generate the expected results of compiling path expressions.

"""

import csv

from selector import SimpleParser


parser = SimpleParser()

with open('util/path-expressions.csv', 'r') as pe_in:
    with open('tests/unit/path-expression-expectations.csv', 'w') as pe_out:
        reader = csv.reader(pe_in)
        writer = csv.writer(pe_out)
        for (pe,) in reader:
            writer.writerow([pe, parser(pe)])
