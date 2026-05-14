v1: initial commit
    1. Launch browser and search random words in dictionary.
    2. Every search reads the changes in the points and after 5 results with the same points, exits the execution and waits for 300 seconds.
    3. Run the search for 15 times with an interval of 300 seconds.

v2: Enhanced automation and task handling
    1. Introduced `BingRewardsAutomator` class for robust task automation.
    2. Added support for intelligent task discovery and handling using aria-label patterns.
    3. Implemented retry logic for failed tasks and session recovery.
    4. Improved search task execution with intelligent keyword extraction.
    5. Centralized automation logic in `rewards_completer_v2.py` for better maintainability.
    6. Integrated `rewards_completer_v2.py` into `launch.py` for seamless execution.
