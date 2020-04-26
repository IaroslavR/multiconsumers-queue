<p>
<a href="https://www.python.org/downloads/release/python-370"><img alt="Python 3.7" src="https://img.shields.io/badge/python-3.7-blue.svg"></a>
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

# multiconsumers-queue-cli
Wrapper for queue based producer/consumers parallel tasks execution

#### Futures:
- graceful shutdown by ^C
- producer/consumer errors handling out of the box
- scheduled tasks statistics logging

#### Examples:
- [with ThreadPoolExecutor](examples/cli-threads.py) for I/O bound tasks
    ```
    Usage: cli-threads.py [OPTIONS]

      Demo script with ThreadPoolExecutor

    Options:
      --workers INTEGER     How many workers will be started  [default: 5]
      --limit INTEGER       How many items can be produced  [default: 50]
      --logging-level TEXT  Logging level  [default: INFO]
      --help                Show this message and exit.
    ```

#### References:
- [Concurrency with Python: Threads and Locks](https://bytes.yingw787.com/posts/2019/01/12/concurrency_with_python_threads_and_locks/)
- [The tragic tale of the deadlocking Python queue](https://codewithoutrules.com/2017/08/16/concurrency-python/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/#setting-up-a-python-project-using-poetry)
