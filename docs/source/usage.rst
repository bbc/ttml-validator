Usage
=====

ttml-validator is a Python project. 
It is built with python 3.13, so you might want to make sure you have that version available.

Setup
-----

You can use `poetry` or `uv` to build and run.

**Poetry**

1. Install `poetry`
2. If need be, ``poetry env use 3.13.4`` to tell poetry to create and use 3.13.4
3. ``poetry install``

**uv**

1. Install `uv`
2. If need be, ``uv python install 3.13`` to tell uv to install 3.13
3. Pin to that version: ``uv python pin 3.13``
4. ``uv build``

Running scripts
---------------

Replacing ``$launchtool`` with ``poetry`` or ```uv``` according to your environment:

::

    $launchtool run validate-ttml -ttml_in input_file.ttml -results_out results_file.txt


``stdin`` and ``stdout`` can be used instead of specifying the files.

A useful bash script to validate many files, assuming there's a subdirectory called ``validation`` is:

::

    function validatemany { for arg in "$@"; do [[ -f $arg ]] && ttmlfile="${arg##*/}" && ttmlpath="${arg%$ttmlfile}" && $launchtool run validate-ttml -ttml_in "$arg" -results_out "${ttmlpath}validation/${ttmlfile}.csv" -csv; done }

Then if you have a directory containing a bunch of subtitle files to validate, whose filenames
have a .xml extension, say, you can do:

::

    mkdir /path/to/many/validation
    validatemany /path/to/many/*.xml

Assuming you have produced CSV outputs you can summarise the results across all the files using:

::

    $launchtool run collate-validation-results -validation_csv_path "/path/to/many/validation/*.csv" -results_out /path/to/many/validation_summary.csv

which will put a validation summary CSV file in the same directory as your subtitle files.
Note the quotes around the wildcard string so that the shell doesn't expand it.

Note this output location avoids polluting your directory of validation CSV files with a non-validation CSV file,
which would cause this script to fail. The ``-results_out`` parameter can be omitted, in which case it writes to stdout.

-csv        Outputs validation results as a CSV file.
            Headers are:
            * status   - Pass, Info, Warn, Fail
            * location - where the validation relates to
            * message  - the validation result

-segment    extracts digits from the beginning of the filename,
            and uses as the segment number,
            with a default segment duration of 3.84s.

-segdur     sets the segment duration, if not 3.84s.

-segment_relative_timing    Useful when the file is a segment used when streaming
                            for example in DASH.

If ``-segment`` is set and the ``-segdur`` is less than
23 minutes no check is made for some subtitles being
required within the first 23 minutes.

Otherwise, if the segment duration is at least 23 minutes,
the check for a minimum number of subtitles
within the first 23 minutes begins at the epoch.

If ``-segment_relative_timing`` is not set (the default),
the epoch is computed from the segment number and segment duration.
Otherwise, for segment-relative timing, the epoch is set to 0s.

-collate_more_than  By default, if a validation message is seen in more than
                    5 locations with the same status, those messages will be
                    collated and the output will include one message stating
                    the number of locations. Set to a different number to
                    adjust from 5.
                    If set to 0, will not collate any messages.

