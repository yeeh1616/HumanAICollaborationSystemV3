function clear_db() {
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        var json = xhttp.responseText;
        var obj = JSON.parse(json);
        var flag = obj["success"];

        if (flag) {
            alert("Clear success!");
        } else {
            alert("Clear failed.");
        }
    };
    xhttp.open("POST", "/clearall");
    xhttp.send();
}