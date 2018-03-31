# skills-labeller
A WDI system for labelling and extracting skills within job postings. Implements an entire intelligent system utilizing a front end, pulling down job postings and online learning all under constrained system resources (e.g. EC2 micro/small) for ease of public use. This readme will be modified as the system continues to see development.

### How to Test
#### ETL API unit test
(warning: can take up to 20 minutes for broadband/slow connections,
  downloads first item of live dataset)
// in docker-compose.yml:55, set RUN_UNITTESTS_ONLY=false

// runs against stood up docker container defined in docker-compose

`pytest --full-trace test/test_etl_api.py`

#### Candidate Skills API test
// in docker-compose.yml:55, set RUN_UNITTESTS_ONLY=false

`pytest --full-trace test/test_candidate_skill_api.py`

#### ETL+Candidate Skills Class unit test
// in docker-compose.yml:55, set RUN_UNITTESTS_ONLY=true

// runs w/in docker container

`docker-compose up etl`
