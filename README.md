# TTML Validator

A utility to read a file and check against a set of requirements to
see if it is valid EBU-TT-D according to the BBC Subtitle Guidelines,
and if not, to list the errors.

For requirements, see [Subtitle File Validation Checks (BBC internal Confluence page)](https://confluence.dev.bbc.co.uk/x/GDiPGQ)

## Usage

Built with python 3.11, so you might want to make sure you have that version available.

1. Install `poetry`
2. `poetry install`

```sh
poetry run validate-ttml -ttml_in input_file.ttml -results_out results_file.txt
```

`stdin` and `stdout` can be used instead of specifying the files.

A useful bash script to validate many files, assuming there's a subdirectory called `validation` is:

```sh
function validatemany { for arg in "$@"; do [[ -f $arg ]] && ttmlfile="${arg##*/}" && ttmlpath="${arg%$ttmlfile}" && poetry run validate-ttml -ttml_in "$arg" -results_out "${ttmlpath}validation/${ttmlfile}.csv" -csv; done }
```

Then if you have a directory containing a bunch of subtitle files to validate, whose filenames
have a .xml extension, say, you can do:

```sh
mkdir /path/to/many/validation
validatemany /path/to/many/*.xml
```

### -csv

Outputs validation results as a CSV file.

Headers are:
* status   - Pass, Info, Warn, Fail
* location - where the validation relates to
* message  - the validation result

### -segment and -segdur and -segment_relative_timing

Useful when the file is a segment used when streaming
for example in DASH.

When `-segment` is set,
extracts digits from the beginning of the filename,
and uses as the segment number,
with a default segment duration of 3.84s.

If the segment duration is not 3.84s,
it can be set using the `-segdur` parameter.

If `-segment` is set and the `-segdur` is less than
23 minutes no check is made for some subtitles being
required within the first 23 minutes.

Otherwise, if the segment duration is at least 23 minutes,
the check for a minimum number of subtitles
within the first 23 minutes begins at the epoch.

If `-segment_relative_timing` is not set (the default),
the epoch is computed from the segment number and segment duration.
Otherwise, for segment-relative timing, the epoch is set to 0s.

### -collate_more_than

By default, if a validation message is seen in more than
5 locations with the same status, those messages will be
collated and the output will include one message stating
the number of locations. Set to a different number to
adjust from 5.

If set to 0, will not collate any messages.

## To Do list

* add the ability to check EBU-TT files too,
and/or other flavours of TTML
* tag each validation failure so that we can extract specific
types of failure as being more or less relevant or severe,
for example syntactic, semantic, aesthetic, spec-conformance,
BBC requirement, etc. A spec-conformant file should play
in some way, but might just not look right. But one that is
both spec-conformant, and passes the aesthetic tests and
the BBC requirements should play and look right
* be more specific about how we handle subtitles intended
for portrait (vertical), square or landscape videos,
including adjusting safe areas and font size acceptable
ranges.
* check the metadata
* identify if a file is actually a valid EBU-TT document
* compute font size even if the wrong units are used,
e.g. "1c" does mean something even if it isn't allowed in EBU-TT-D
* when id attributes are used instead of xml:id attributes,
treat those as though they'd been correctly specified as xml:id
and then see how well the document works
* check conformance to the IMSC HRM
* see how feasible it is to construct a valid document
from an invalid input based on the validation failures
