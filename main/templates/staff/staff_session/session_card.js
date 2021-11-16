/** send session update form   
*/
sendUpdateSession(){
    app.$data.cancelModal = false;
    app.$data.working = true;
    app.sendMessage("update_session",{"formData" : $("#sessionForm").serializeArray(),
                                      "sessionID" : app.$data.sessionID});
},

/** take update session reponse
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateSession(messageData){
    app.clearMainFormErrors();

    if(messageData.status == "success")
    {
        app.takeGetSession(messageData);       
        $('#editSessionModal').modal('hide');    
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.errors);
    } 
},

/** show edit session modal
*/
showEditSession:function(){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.sessionBeforeEdit = Object.assign({}, app.$data.session);

    
    var myModal = new bootstrap.Modal(document.getElementById('editSessionModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit session modal
*/
hideEditSession:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session, app.$data.sessionBeforeEdit);
        app.$data.sessionBeforeEdit=null;
    }
},