import requests

file_name = 'list_convex_qps.txt'
base_address = 'http://qplib.zib.de/qplib/'

with open(file_name, 'r') as f:
    problems = [l[:-1] for l in f.readlines() if l[0].isdigit()]

    for p in problems:
        problem_file = "QPLIB_%s.qplib" % p
        print("Downloading %s" % problem_file)
        r = requests.get(base_address + problem_file)
        with open(problem_file, "wb") as p_f:
            p_f.write(r.content)
