#!/bin/bash
pip install flake8 > /dev/null 2>&1
flake8 backend/ --count --max-complexity=10 --max-line-length=88 --statistics | grep "F821\|F841\|F401\|E712\|F541\|C901"
