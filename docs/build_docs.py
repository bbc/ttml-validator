import subprocess
import yaml
import os


def build_doc(version, language, tag):
    os.environ["current_version"] = version
    os.environ["current_language"] = language
    subprocess.run("git checkout " + tag, shell=True)
    subprocess.run("git checkout main -- conf.py", shell=True)
    subprocess.run("git checkout main -- versions.yaml", shell=True)
    # subprocess.run("doxygen Doxyfile", shell=True)  # uncomment if needed
    os.environ['SPHINXOPTS'] = "-D language='{}'".format(language)
    subprocess.run("make html", shell=True)


def move_dir(src, dst):
    subprocess.run(["mkdir", "-p", dst])
    subprocess.run("mv "+src+'* ' + dst, shell=True)


os.environ["build_all_docs"] = str(True)
# os.environ["pages_root"] = "https://bbc.github.io/ttml-validator"
# os.environ["pages_root"] = "http://localhost:8000"
os.environ["pages_root"] = ""  # makes everything relative paths

build_doc("latest", "en", "main")
move_dir("./build/html/", "../pages/")
# build_doc("latest", "de", "main")
# move_dir("./build/html/", "../pages/de/")

with open("versions.yaml", "r") as yaml_file:
    docs = yaml.safe_load(yaml_file)

for version, details in docs.items():
    tag = details.get('tag', '')
    for language in details.get('languages', []):
        build_doc(version, language, version)
        move_dir("./build/html/", "../pages/"+version+'/'+language+'/')
