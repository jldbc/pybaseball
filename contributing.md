# Contributing

We welcome pull requests improving any aspect of this library! The main ways to contribute to pybaseball are the following:

* Scraping additional data sources from trusted sites (FanGraphs, Baseball Reference, etc.). Write a function that scrapes the data and returns it in a usable format.
* Fix an error or broken request/scrape in the existing code
* Refactoring and style improvements
* Documentation / README improvements
* Baseball-specific analysis functions
* Custom visualization and data preparation tools
* Share some example code

A good place to start is on our Issues page, specifically [good first issues](https://github.com/jldbc/pybaseball/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) or [feature requests](https://github.com/jldbc/pybaseball/issues?q=is%3Aissue+is%3Aopen+label%3A%22feature+request%22).

# Guidelines

Generally follow [PEP8](https://peps.python.org/pep-0008/) for code formatting. Please use [Type Annotations](https://docs.python.org/3/library/typing.html) for functions. If any of this is foreign, make the PR and we will give guidance in code review. 

With each PR, please make sure you address the following:

1. Include description of the changes. If this addresses an existing issue, please make sure to reference it (add a # with the issue number so Github links the two).
2. Any new functionalities should have tests. Any amended functionalities should have the existing tests pass or have tests amended to conform the changes.
3. New/changed functionality should be described in the [docs](https://github.com/jldbc/pybaseball/tree/master/docs).


# Steps

1. Fork the repository from [the main page](https://github.com/jldbc/pybaseball).

2. Clone your fork to your computer and add the remote 

```
git clone git@github.com:<your GitHub handle>/pybaseball.git
cd pybaseball
git remote add upstream git@github.com:jldbc/pybaseball.git
```

3. Create a branch

```
git checkout -b my-awesome-new-feature
```

4. Run setup.py (strongly recommend in a virtualenv)

```
pip install -e .
```

5. Make your changes

6. Run the test suite. From the top level `pybaseball` directory run:

```
pytest
```


7. Add and commit changes with descriptive message

```
git add file1.py tests/test_file1.py docs/file1.md
git commit -m "My new fancy functionality"
```

8. Sync with upstream to pull any recent changes

```
git fetch upstream
git rebase upstream/master
```

9. Push your changes

```
git push origin my-awesome-new-feature
```

10. Click the link that appears in your terminal to make a pull request, or go to your fork of the repository and click the link. Add a summary of your changes and submit!