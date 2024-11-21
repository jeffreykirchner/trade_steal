/** send session update form   
*/
sendUpdateSession: function sendUpdateSession(){
    this.cancelModal = false;
    this.working = true;
    app.send_message("update_session",{"formData" : {title:app.session.title}});
},

/** take update session reponse
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_update_session: function take_update_session(message_data){
    app.clearMainFormErrors();

    if(message_data.value == "success")
    {
        app.take_get_Session(message_data);       
        app.edit_session_modal.hide();    
    } 
    else
    {
        this.cancelModal=true;                           
        app.displayErrors(message_data.errors);
    } 
},

/** show edit session modal
*/
showEditSession:function showEditSession(){
    app.clearMainFormErrors();
    this.cancelModal=true;
    this.sessionBeforeEdit = Object.assign({}, this.session);

    app.edit_session_modal.show();
},

/** hide edit session modal
*/
hideEditSession:function hideEditSession(){
    if(this.cancelModal)
    {
        Object.assign(this.session, this.sessionBeforeEdit);
        this.sessionBeforeEdit=null;
    }
},