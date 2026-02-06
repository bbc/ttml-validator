Usage
=====

ttml-validator is a Python project. 
It is built with python 3.13, so you might want to make sure you have that version available.

Setup
-----

After cloning the repository (recursively - it has submodule dependencies),
you can use `poetry` or `uv` to build and run.

**Poetry**

1. Install `poetry`
2. If need be, ``poetry env use 3.13.4`` to tell poetry to create and use 3.13.4
3. ``poetry install``

We have tested this works with Poetry v2.2.1.

**uv**

1. Install `uv`
2. If need be, ``uv python install 3.13`` to tell uv to install 3.13
3. Pin to that version: ``uv python pin 3.13``
4. ``uv build``

We have tested this works with uv v0.7.12.

Running the validator script
----------------------------

Replacing ``$launchtool`` with ``poetry`` or ```uv``` according to your environment:

::

    $launchtool run validate-ttml -ttml_in input_file.ttml -results_out results_file.txt

Command line options for ``validate-ttml`` are:

-h, --help      shows the help message and exits

-ttml_in file       The input file to validate.
                    If absent ``stdin`` is used.

-results_out file
    Where to write out the results.
    If absent ``stdout`` is used.

-csv
    Outputs validation results as a CSV file, rather than the default
    plain text file. Overrides ``-json`` if that is also set.
    Headers are:
    * status   - Pass, Info, Warn, Fail
    * location - where the validation relates to
    * message  - the validation result

-json           Outputs validation results as a JSON file, rather than the default
                plain text file. Ignored if ``-csv`` is also set.

-segment        extracts digits from the beginning of the filename,
                and uses as the segment number,
                with a default segment duration of 3.84s.

-segdur duration_seconds    sets the segment duration, if not 3.84s.

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

-vertical       if set, validates the input as though it were intended for a
                vertical or portrait (9:16 aspect ratio) video.

-collate_more_than count
    By default, if a validation message is seen in more than
    5 locations with the same status, those messages will be
    collated and the output will include one message stating
    the number of locations. Set to a different number to
    adjust from 5.
    If set to 0, will not collate any messages.

Validating many files and collating the results
-----------------------------------------------

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

``collate-validation-results`` has the following command line options:

-h, --help                  show this help message and exit

-validation_csv_path path   Path where validation CSV files can be found. May include wildcards.

-results_out file           file to be written, containing the validation summary output.
                            If omitted, defaults to ``stdout``.
