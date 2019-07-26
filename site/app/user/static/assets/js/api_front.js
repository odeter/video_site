function api_reaction(url, like, l_type, t_id, dis_obj, li_obj){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
	if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
	    noti_msg(json['update_msg'], json['note_type']);
	    dis_obj.text(json['c_likes'])
	    li_obj.text(json['c_dislikes'])
	}
    };
    var data = JSON.stringify({"c_type": "react", "like": like,
			       "target": l_type, "target_id": t_id});
    xhr.send(data);
}

function api_delCom(url, d_type, t_id, com_table=null){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    console.log("called!!")
    xhr.onreadystatechange = function () {
	if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
	    noti_msg(json['update_msg'], json['note_type']);
	    if(com_table){
		$('#'+com_table).DataTable().row('#'+t_id).remove().draw( false );
	    }
	}
    };
    var data = JSON.stringify({"c_type": "del", "target": d_type, "target_id": t_id});
    xhr.send(data);
}
