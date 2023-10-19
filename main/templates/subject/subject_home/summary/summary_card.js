sendName(){

    app.$data.working = true;
    app.sendMessage("name", {"formData" : $("#endGameForm").serializeArray()});
                     
},

/** take result of moving goods
*/
takeName(messageData){

    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.$data.session_player.name = messageData.status.result.name; 
        app.$data.session_player.student_id = messageData.status.result.student_id;                   
    } 
    else
    {
        app.displayErrors(messageData.status.errors);
    }
},

/**
 * post study link
 */
postSessionLink(){

    if(app.$data.session_player.post_experiment_link == '') return;

    location.href = app.$data.session_player.post_experiment_link;
},