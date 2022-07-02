function save_summary(pid, f1) {
    var summary = document.getElementById("w3review").value;
    var parmas = pid + "------" + summary;

    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = xhttp.responseText;
            var obj = JSON.parse(json);
            var complete = document.getElementById("complete");
            complete.innerHTML = "Complete: " + obj["complete"] + "/" + obj["total"];

            var q = document.getElementById("ap_1");
            q.className = "box1";

            var btn_save = document.getElementById("save_summary");
            btn_save.disabled = true;
        }
    };
    xhttp.open("POST", "/policies/0/save_summary");
    xhttp.send(parmas);
}

function summary_change() {
    var btn_save = document.getElementById("save_summary");
    btn_save.disabled = false;
}