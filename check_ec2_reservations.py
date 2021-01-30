#!/usr/bin/python3.7

import re, sys
from ec2_reservation_check import cli
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(cli())