/**
 * send request to create new session
 */
send_create_session: function send_create_session(){
    this.working = true;
    this.create_session_button_text ='<i class="fas fa-spinner fa-spin"></i>';
    app.send_message("create_session",{});
},

/**
 * take crate a new session
 */
take_create_session: function take_create_session(message_data){    
    this.create_session_button_text ='Create Session <i class="fas fa-plus"></i>';
    app.take_get_sessions(message_data);
},

/**
 * send request to delete session
 * @param id : int
 */
send_delete_session: function send_delete_session(id){
    if (!confirm('Delete session?')) {
        return;
    }

    this.working = true;
    app.send_message("delete_session",{"id" : id});
},

/**
 * sort by title
 */
sort_by_title: function sort_by_title(){

    app.working = true;

    app.sessions.sort(function(a, b) {
        a=a.title.trim().toLowerCase();
        b=b.title.trim().toLowerCase();
        return a < b ? -1 : a > b ? 1 : 0;
    });

    app.working = false;
},

/**
 * sort by date
 */
sort_by_date: function sort_by_date(){

    app.working = true;

    app.sessions.sort(function(a, b) {
        return new Date(b.start_date) - new Date(a.start_date);

    });

    app.working = false;
},