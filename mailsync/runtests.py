import os
import sys
import nose

os.environ["TEST_ENV"] = "True"

# Example usage -> python runtests - all tests
# python runtests tests/alerts - selected folder

if __name__ == "__main__":
	try:
		suite = eval(sys.argv[1]) # Selected tests
	except:
		suite = None # All tests

	nose.run(suite)