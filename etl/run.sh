if [ "$RUN_UNITTESTS_ONLY" = true ];
then pytest --full-trace test/test_preprocessor.py test/test_candidate_skills.py test/test_etl.py
#else python vt.py # should provide access to endpoint or resources on which to stand up 1 or more endpoints
#else nameko run vt
# hold open so i can test this code, using nameko
else while :; do echo 'Hit Ctrl+C'; sleep 25; done
fi

# trick for keeping container open, for debug
# while :; do echo 'Hit Ctrl+C'; sleep 25; done
