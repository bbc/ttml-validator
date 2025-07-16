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

        // TODO: Run the validator here!
    }
}

$(function () {
    document.getElementById('file-input').addEventListener(
        'change', readMultipleFiles, false);
});
