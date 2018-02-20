#!/bin/bash
if [ "$RUN_UNITTESTS_ONLY" = true ];
then pytest --full-trace test/test_skilloracle.py
else python3 webserver.py # todo: update with nameko run service or supervisord
fi
