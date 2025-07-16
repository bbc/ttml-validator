// const FileSaver = require('filesaver.js-npm');

function readMultipleFiles(e) {
    filelist = Array.from(e.target.files);
    filelist.sort(function(a, b) {
        return a.name.split('.')[0].replace(/\D/g, '') > b.name.split('.')[0].replace(/\D/g, '');
    });
    currentFileIndex = 0;
    // enableOrDisablePrevAndNext();
    readSingleFile(filelist[currentFileIndex]);
}

function readSingleFile(file, goToEnd = false) {

    if (!file) {
        document.getElementById("current-file").innerText = '';
        return;
    } else {
        document.getElementById("current-file").innerText = file.name;

        var reader = new FileReader();
        reader.onload = function (e) {
            var contents = e.target.result;
            // TODO: Run the validator here!
            displayContents(contents, goToEnd);
        };

        reader.readAsText(file);
    }
    document.getElementById("current-file").innerText = file.name;

}

function displayContents(contents, goToEnd = false) {
    document.getElementById("file-contents").innerText = contents;
}

$(function () {
    document.getElementById('file-input').addEventListener(
        'change', readMultipleFiles, false);
});
