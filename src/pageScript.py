from .ttmlValidator import validate_ttml
import io
import argparse
from pyscript import document, when, display, window


document.querySelector("#python-signal").innerText="pageScript.py"


@when("change", "#file-contents")
def file_change_handler(event):
    display("file contents changed")
    document.querySelector("#python-signal").innerText="file_change_handler"


# @when("click", "#validate-button")
def validateNow(event):
    display("button clicked")
    window.console.log("button clicked")
    document.querySelector("#python-signal").innerText="validateNow"

when('click', '#validate-button', handler=validateNow)


def validateTtml(content: str) -> str:
    in_io = io.TextIOWrapper(
        buffer=io.BytesIO(), encoding='utf-8', newline='\n')
    in_io.write(content)
    in_io.flush()
    out_io = io.TextIOWrapper(
        buffer=io.BytesIO(), encoding='utf-8', newline='\n')
    args = argparse.Namespace(
        ttml_in=in_io,
        results_out=out_io,
        json=True,
        csv=False,
        segment=False,
        vertical=False,
        collate_more_than=5
    )
    result = validate_ttml(args=args)
    output = out_io.read()
    return output
