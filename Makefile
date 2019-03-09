test:
	find ./apache_log_analyzer ! -name '__*__.py' -name '*.py' | xargs -r python3 -m doctest
