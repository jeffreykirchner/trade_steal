/**
 * send request to create new session
 */
sendCreateSession: function sendCreateSession(){
    this.working = true;
    this.createSessionButtonText ='<i class="fas fa-spinner fa-spin"></i>';
    app.sendMessage("create_session",{});
},

/**
 * take crate a new session
 */
takeCreateSession: function takeCreateSession(messageData){    
    this.createSessionButtonText ='Create Session <i class="fas fa-plus"></i>';
    app.takeGetSessions(messageData);
},

/**
 * send request to delete session
 * @param id : int
 */
sendDeleteSession: function sendDeleteSession(id){
    if (!confirm('Delete session?')) {
        return;
    }

    this.working = true;
    app.sendMessage("delete_session",{"id" : id});
},