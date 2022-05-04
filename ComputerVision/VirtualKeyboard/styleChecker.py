import pycodestyle

fchecker = pycodestyle.Checker('function_file.py', show_source=True)
file_errors = fchecker.check_all()

print("Found %s errors (and warnings)" % file_errors)