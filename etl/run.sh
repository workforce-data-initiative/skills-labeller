#!/bin/bash

# adopted from nameko-example
is_ready() {
    eval "curl -I http://${RABBIT_USER}:${RABBIT_PASSWORD}@${RABBIT_HOST}:${RABBIT_MANAGEMENT_PORT}/api/vhosts"
}

if [ "$RUN_UNITTESTS_ONLY" = true ];
then pytest --full-trace test/test_preprocessor.py test/test_candidate_skills.py test/test_etl.py
else
	i=0
	while ! is_ready; do
		i=`expr $i + 1`
		if [ $i -ge 10 ]; then
			echo "$(date) - RabbitMQ broker still not ready, giving up!"
			exit 1
		fi
		echo "$(date) - Waiting for RabbitMQ to be ready..."
		sleep 5
	done
	nameko run --config etl/config.yml etl.vt
fi
# trick for keeping container open, for debug
#then while :; do echo 'Hit Ctrl+C'; sleep 25; done
