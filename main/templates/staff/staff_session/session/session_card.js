/** send session update form   
*/
sendUpdateSession: function sendUpdateSession(){
    this.cancelModal = false;
    this.working = true;
    app.sendMessage("update_session",{"formData" : {title:app.session.title}});
},

/** take update session reponse
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateSession: function takeUpdateSession(messageData){
    app.clearMainFormErrors();

    if(messageData.value == "success")
    {
        app.takeGetSession(messageData);       
        app.edit_session_modal.hide();    
    } 
    else
    {
        this.cancelModal=true;                           
        app.displayErrors(messageData.errors);
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