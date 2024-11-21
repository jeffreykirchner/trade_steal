sendName: function sendName(){

    app.working = true;
    formData = {name:document.getElementById("id_name").value, 
                student_id:document.getElementById("id_student_id").value,};
    app.send_message("name", {"formData" : formData});
                     
},

/** take result of moving goods
*/
takeName: function takeName(message_data){

    app.clearMainFormErrors();

    if(message_data.value == "success")
    {
        app.session_player.name = message_data.result.name; 
        app.session_player.student_id = message_data.result.student_id;                   
    } 
    else
    {
        app.displayErrors(message_data.errors);
    }
},

/**
 * post study link
 */
postSessionLink: function postSessionLink(){

    if(app.session_player.post_experiment_link == '') return;

    location.href = app.session_player.post_experiment_link;
},