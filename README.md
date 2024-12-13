# TTML Validator

A utility to read a file and check against a set of requirements to
see if it is valid EBU-TT-D according to the BBC Subtitle Guidelines,
and if not, to list the errors.

## Usage

Built with python 3.11, so you might want to make sure you have that version available.

1. Install `poetry`
2. `poetry install`

```sh
poetry run validate-ttml -ttml_in input_file.ttml -results_out results_file.txt
```

`stdin` and `stdout` can be used instead of specifying the files.

