#!/bin/bash
if [ "$RUN_UNITTESTS_ONLY" = true ];
then pytest --full-trace test/test_skilloracle.py
else python3 /skills-labeller/skilloracle/webserver.py
fi
#while true; do echo 'hit ctrl-c'; sleep 35; done
