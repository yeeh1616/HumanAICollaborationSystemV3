function text_change(qid, isTextEntry){
    var div_tb_id = 'tb_' + qid;
    var div_tb = document.getElementById(div_tb_id);

    var btn_save_id = 'btn_save_' + qid;
    var btn_save = document.getElementById(btn_save_id);

    if(isTextEntry=="True"){
        if(div_tb.style["cssText"] == "display: none;"){
            div_tb.style = "display: inline-block;";
            var ta = div_tb.children[0];

            if(ta.innerHTML == ""){
                btn_save.disabled = true;
            }else {
                btn_save.disabled = false;
            }
        }
    } else {
        if(div_tb != null){
            if(div_tb.style["cssText"] == "display: inline-block;"){
                div_tb.style = "display: none;";
            }
        }
        btn_save.disabled = false;
    }
}

function text_change2(qid){
    var btn_save_id = 'btn_save_' + qid;
    var btn_save = document.getElementById(btn_save_id);

    var div_tb_id = 'tb_' + qid;
    var div_tb = document.getElementById(div_tb_id);
    var ta = div_tb.children[0];

    if(ta.value == ""){
        btn_save.disabled = true;
    }else {
        btn_save.disabled = false;
    }
}

function text_change3(btn_save_id){
    var btn_save = document.getElementById(btn_save_id);
    btn_save.disabled = false;
}

function type2_highlighting(qid,answer) {
    if(answer == ""){
        return;
    }

    document.getElementById(qid + '_answer').innerText = answer;

    let divs = document.getElementById("summary").children;
    var flagnew = new RegExp(answer,"ig")

    for(i=0; i<divs.length; i++){
        var divs2 = divs[i].children;
        for(j=0; j < divs2.length; j++){
            if(divs2[j].nodeName == "SPAN"){
                var tmp = divs2[j].innerHTML;

                tmp = tmp.replaceAll("<span style=\"background-color: #FFFF00\">","");
                tmp = tmp.replaceAll("</span>","");

                var found = tmp.match(flagnew);
                if (found !== null && found.length > 0){
                    tmp = tmp.replace(flagnew, "<span style=\"background-color: #FFFF00\">" + found[0] + "</span>");
                }
                divs2[j].innerHTML = tmp;
            }
        }
    }

    document.getElementById('btn_save_' + qid).disabled=false;
}

function show_hide_highlighting_multichoice(me, policyId, questionId) {
    var nodes1 = document.getElementById("summary").children;
    for(i = 0; i < nodes1.length; i++){
        var node1 = nodes1[i];
        if(node1.nodeName === 'DIV'){
            var nodes2 = node1.children;
            for(j = 0; j < nodes2.length; j++){
                var node3 = nodes2[j];
                try {
                    if(node3.nodeName === 'SPAN'){
                        if(me.innerHTML == "Hide Highlighting"){
                            node3.style.backgroundColor = '';
                        } else {
                            var scoreStr = document.getElementById(node3.id+"_score").value;
                            var score = parseFloat(scoreStr);
                            if(score>=0.9){
                                node3.style.backgroundColor = '#37ff00';
                            }else if(score>=0.8 && score<0.9){
                                node3.style.backgroundColor = '#a0ff6e';
                            }else if(score>=0.7 && score <0.8){
                                node3.style.backgroundColor = '#ffee04';
                            }else if(score>=0.6 && score <0.7){
                                node3.style.backgroundColor = '#fff833';
                            }else if(score>=0.5 && score <0.6){
                                node3.style.backgroundColor = '#fcf68f';
                            }else if(score>=0.4 && score <0.5){
                                node3.style.backgroundColor = '#fdfcc4';
                            }else {
                                node3.style.backgroundColor = '';
                            }
                        }
                    }
                } catch (error) {}
            }
        }
    }

    if(me.innerHTML == "Hide Highlighting"){
        me.innerHTML = "Highlighting";
    } else {
        me.innerHTML = "Hide Highlighting";
    }
}

function save1(btn, qid, pid, column) {
    var options = document.getElementById(qid + "_op").children;

    for(i=0; i<options.length;i++){
        if(options[i].nodeName == "INPUT" && options[i].checked){
            var ans = options[i+1].innerHTML;

            if(options[i+3].children[0] != null && options[i+3].children[0].nodeName == "TEXTAREA"){
                ans = options[i+3].children[0].value + "|[Text entry]";
            }

            var parmas = '{"pid":"' + pid + '","qid":"' + qid + '","answer":"' + ans + '","column":"' + column + '"}';

            const xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    var json = xhttp.responseText;
                    var obj = JSON.parse(json);

                    var complete = document.getElementById("complete");
                    complete.innerHTML = "Complete: " + obj["complete"] + "/" + obj["total"];

                    var q = document.getElementById("ap_" + qid);
                    q.className="box1";

                    btn.disabled=true;
                }
            };
            xhttp.open("POST", "/policies/1/save");
            xhttp.send(parmas);
            break;
        }
    }
}

function save2(btn, qid, pid, column) {
    var answer_obj = document.getElementById(qid + '_answer');
    var answer = answer_obj.value;
    var parmas = '{"pid":"' + pid + '","qid":"' + qid + '","answer":"' + answer + '","column":"' + column + '"}';

    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var json = xhttp.responseText;
            var obj = JSON.parse(json);

            var complete = document.getElementById("complete");
            complete.innerHTML = "Complete: " + obj["complete"] + "/" + obj["total"];

            var q = document.getElementById("ap_" + qid);
            q.className="box1";

            btn.disabled=true;
        }
    };
    xhttp.open("POST", "/policies/2/save");
    xhttp.send(parmas);
}