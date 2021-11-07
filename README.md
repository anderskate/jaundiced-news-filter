# Jaundiced news filter

So far only one news site is supported - [ИНОСМИ.РУ](https://inosmi.ru/). For it, a special adapter has been developed that can highlight the text of the article against the background of the rest of the HTML markup. Other news sites will require new adapters, all of which will be in the `adapters` directory. The code for the INOSMI.RU website is also placed there: `adapters / inosmi_ru.py`.

In the future, you can create a universal adapter suitable for all sites, but its development will be difficult and will require additional time and effort.

# How to install

You need Python 3.7 or later. It is recommended to create a virtual environment to install packages.

The first step is to install the packages:

```python3
pip3 install -r requirements.txt
```

# How to run

```python3
python3 server.py
```

# How to run tests

For testing used [pytest](https://docs.pytest.org/en/latest/),
Tests cover code fragments that are difficult to debug: text_tools.py and adapters.
Commands for running tests:

```
python -m pytest adapters/inosmi_ru.py
```

```
python -m pytest tests.py
```

# Objectives of the project

The code is written for educational purposes.
This is a lesson from the course on web development — [Девман](https://dvmn.org).
