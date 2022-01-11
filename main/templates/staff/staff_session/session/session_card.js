/** send session update form   
*/
sendUpdateSession(){
    app.$data.cancelModal = false;
    app.$data.working = true;
    app.sendMessage("update_session",{"formData" : $("#sessionForm").serializeArray()});
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
    this.cancelModal=true;
    this.sessionBeforeEdit = Object.assign({}, this.session);

    var myModal = new bootstrap.Modal(document.getElementById('editSessionModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit session modal
*/
hideEditSession:function(){
    if(this.cancelModal)
    {
        Object.assign(this.session, this.sessionBeforeEdit);
        this.sessionBeforeEdit=null;
    }
},