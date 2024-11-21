/**
 * send request for help doc
 * @param title : string
 */
sendLoadHelpDoc: function sendLoadHelpDoc(title){
    this.working = true;
    this.helpText = "Loading ...";

    var myModal = new bootstrap.Modal(document.getElementById('helpModal'), {
        keyboard: false
        })

    myModal.toggle();

    app.send_message("help_doc", {title : title});
},

/**
 * take help text load request
 * @param message_data : json
 */
take_load_help_doc: function take_load_help_doc(message_data){

    if(message_data.status.value == "success")
    {
        this.helpText = message_data.status.result.help_doc.text;
    }
    else
    {
        this.helpText = message_data.status.message;
    }
},

