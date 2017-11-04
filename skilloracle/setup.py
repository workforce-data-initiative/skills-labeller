from distutils.core import setup
setup(
    name = "skills-labeller",
    packages = ["skillslabller"],
    version = "0.0.1",
    description = "system for labelling skills within job postings",
    author = ["Kwame Porter Robinson", "Greg Mundy"],
    author_email = "",
    url = "",
    download_url = "https://github.com/workforce-data-initiative/skills-labeller",
    keywords = ["skills", "job data"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: MIT",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        ],
    long_description = """\
A WDI system for labelling and extracting skills within job postings. Implements an entire intelligent system utilizing a front end, pulling down job postings and online learning all under constrained system resources (e.g. EC2 micro/small) for ease of public use.
"""
)
