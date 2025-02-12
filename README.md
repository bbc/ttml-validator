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

### -csv

Outputs validation results as a CSV file.

Headers are:
* status   - Pass, Info, Warn, Fail
* location - where the validation relates to
* message  - the validation result

### -segment and -segdur

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
within the first 23 minutes begins at the epoch
computed from the segment number and segment duration.

### -collate_more_than

By default, if a validation message is seen in more than
5 locations with the same status, those messages will be
collated and the output will include one message stating
the number of locations. Set to a different number to
adjust from 5.

If set to 0, will not collate any messages.
