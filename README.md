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


