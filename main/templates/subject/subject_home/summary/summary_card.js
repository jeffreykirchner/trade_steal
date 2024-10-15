sendName: function sendName(){

    app.working = true;
    formData = {name:document.getElementById("id_name").value, 
                student_id:document.getElementById("id_student_id").value,};
    app.sendMessage("name", {"formData" : formData});
                     
},

/** take result of moving goods
*/
takeName: function takeName(messageData){

    app.clearMainFormErrors();

    if(messageData.value == "success")
    {
        app.session_player.name = messageData.result.name; 
        app.session_player.student_id = messageData.result.student_id;                   
    } 
    else
    {
        app.displayErrors(messageData.errors);
    }
},

/**
 * post study link
 */
postSessionLink: function postSessionLink(){

    if(app.session_player.post_experiment_link == '') return;

    location.href = app.session_player.post_experiment_link;
},