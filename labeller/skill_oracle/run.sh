#!/bin/sh

DEFAULT_PORT=7000

if [[ $# -gt 0 ]]; then
    vw $@ &
    python oracle.py
else
    vw save_resume --port $DEFAULT_PORT --active --predictions /dev/null --daemon --audit --link=logistic --loss_function=logistic &
    python oracle.py
fi
