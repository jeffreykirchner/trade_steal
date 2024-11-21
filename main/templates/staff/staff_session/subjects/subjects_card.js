 /**
 * take update player groups
 * @param message_data {json} session day in json format
 */
  take_update_connection_status: function take_update_connection_status(message_data){
            
    if(message_data.value == "success")
    {
        let result = message_data.result;

        session_player = app.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.connected_count = result.connected_count;
            session_player.name = result.name;
            session_player.student_id = result.student_id;
            session_player.current_instruction = result.current_instruction;
            session_player.instructions_finished = result.instructions_finished;
            session_player.survey_complete = result.survey_complete;
        }
    }
},

/**
 * take update player groups
 * @param message_data {json} session day in json format
 */
 take_update_groups: function take_update_groups(message_data){
    
    if(message_data.status == "success")
    {
        let group_list = message_data.group_list;

        for(let i=0; i<group_list.length; i++)
        {
            session_player = app.findSessionPlayer(group_list[i].id);

            if(session_player)
            {
                session_player.group_number = group_list[i].group_number;
            }
        }
    }
},

/** take name and student id
* @param message_data {json} session day in json format
*/
take_update_name: function take_update_name(message_data){
           
    if(message_data.value == "success")
    {
        let result = message_data.result;

        session_player = app.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.name = result.name;
            session_player.student_id = result.student_id;
        }       
    }
},

/** take name and student id
* @param message_data {json} session day in json format
*/
take_update_avatar: function take_update_avatar(message_data){
           
    if(message_data.value == "success")
    {
        let result = message_data.result;

        session_player = app.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.avatar = result.avatar;
            this.setupSingleAvatar(this.findSessionPlayerIndex(result.id));
        }       
    }
 },

/** take name and student id
* @param message_data {json} session day in json format
*/
take_next_instruction: function take_next_instruction(message_data){
           
    if(message_data.value == "success")
    {
        let result = message_data.result;

        session_player = this.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.current_instruction = result.current_instruction;
            session_player.current_instruction_complete = result.current_instruction_complete;
        }       
    }
 },

 /** take name and student id
* @param message_data {json} session day in json format
*/
take_finished_instructions: function take_finished_instructions(message_data){
           
    if(message_data.value == "success")
    {
        let result = message_data.result;

        session_player = this.findSessionPlayer(result.id);

        if(session_player)
        {
            session_player.instructions_finished = result.instructions_finished;
            session_player.current_instruction_complete = result.current_instruction_complete;
        }       
    }
 },

 /**
  * update subject earnings
  *  @param message_data {json} session day in json format
  */
 takeUpdateEarnings: function takeUpdateEarnings(message_data){

    if(message_data.value == "success")
    {
        let session_player_earnings = message_data.result.session_player_earnings;
        let session_players = this.session.session_players;

        for(let i=0; i<session_player_earnings.length; i++)
        {
            session_player = app.findSessionPlayer(session_player_earnings[i].id);

            if(session_player)
            {
                session_player.earnings = session_player_earnings[i].earnings;
            }
        }
    }
 },

/**
 * take update subjects production
 */
take_update_production_time: function take_update_production_time(message_data){

    if(message_data.value == "success")
    {
       
        session_player = app.findSessionPlayer(message_data.result.id);
        
        session_player.good_one_production_rate = message_data.result.good_one_production_rate; 
        session_player.good_two_production_rate = message_data.result.good_two_production_rate;    
    }
},

/** send session update form   
*/
sendEmailList: function sendEmailList(){
    this.cancelModal = false;
    this.working = true;

    app.send_message("email_list",
                   {"csv_data" : this.csv_email_list});
},

/** take update subject response
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_update_email_list: function take_update_email_list(message_data){
    app.clearMainFormErrors();

    if(message_data.value == "success")
    {            
        app.upload_email_modal.hide(); 

        result = message_data.result;

        for(i=0; i<result.length; i++)
        {
            let session_player = app.findSessionPlayer(result[i].id);
            session_player.email = result[i].email;
            session_player.student_id = result[i].student_id;
        }
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(message_data.errors);
    } 
},

/** show edit subject modal
*/
showSendEmailList: function showSendEmailList(){
    app.clearMainFormErrors();
    this.cancelModal=true;

    this.csv_email_list = "";
    
    app.upload_email_modal.show(); 
},

/** hide edit subject modal
*/
hideSendEmailList: function hideSendEmailList(){
    this.csv_email_list = "";

    if(this.cancelModal)
    {      
       
    }
},

/** send session update form   
*/
sendUpdateSubject: function sendUpdateSubject(){
    this.cancelModal = false;
    this.working = true;
    app.send_message("update_subject",
                   {"formData" : this.staffEditNameEtcForm});
},

/** take update subject response
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_update_subject: function take_update_subject(message_data){
    app.clearMainFormErrors();

    if(message_data.value == "success")
    {            
        app.edit_subject_modal.hide();    

        let session_player = app.findSessionPlayer(message_data.session_player.id);
        session_player.name = message_data.session_player.name;
        session_player.student_id = message_data.session_player.student_id;
        session_player.email = message_data.session_player.email;
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(message_data.errors);
    } 
},

/** show edit subject modal
*/
showEditSubject: function showEditSubject(id){
    app.clearMainFormErrors();
    this.cancelModal=true;

    this.staffEditNameEtcForm.id = id;

    let session_player = app.findSessionPlayer(id);

    this.staffEditNameEtcForm.name = session_player.name;
    this.staffEditNameEtcForm.student_id = session_player.student_id;
    this.staffEditNameEtcForm.email = session_player.email;
    
    app.edit_subject_modal.show();  
},

/** hide edit subject modal
*/
hideEditSubject: function hideEditSubject(){
    if(this.cancelModal)
    {
       
       
    }
},

/**
 * copy earnings to clipboard
 */
copyEarnings: function copyEarnings(){

   let text="";

   for(i=0;i<app.session.session_players_order.length;i++)
    {
        let session_player_id = app.session.session_players_order[i];

        text += app.session.session_players[session_player_id].student_id + ",";
        text += app.session.session_players[session_player_id].earnings;

        if(i<app.session.session_players_order.length-1) text += "\r\n";
    }

   app.copyToClipboard(text);
   app.earnings_copied = true;
},

//copy text to clipboard
copyToClipboard: function copyToClipboard(text){

    // Create a dummy input to copy the string array inside it
    var dummy = document.createElement("textarea");

    // Add it to the document
    document.body.appendChild(dummy);

    // Set its ID
    dummy.setAttribute("id", "dummy_id");

    // Output the array into it
    document.getElementById("dummy_id").value=text;

    // Select it
    dummy.select();
    dummy.setSelectionRange(0, 99999); /*For mobile devices*/

    // Copy its contents
    document.execCommand("copy");

    // Remove it as its not needed anymore
    document.body.removeChild(dummy);

    /* Copy the text inside the text field */
    document.execCommand("copy");
},

/** send session update form   
*/
sendAnonymizeData: function sendAnonymizeData(){
    
    if (!confirm('Anonymize data? Identifying information will be permanent removed.')) {
        return;
    }

    this.working = true;
    app.send_message("anonymize_data",{});
},

/** take update subject response
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_anonymize_data: function take_anonymize_data(message_data){
    app.clearMainFormErrors();

    if(message_data.value == "success")
    {            

        let session_player_updates = message_data.result;
        let session_players = this.session.session_players;

        for(let i=0; i<session_player_updates.length; i++)
        {
            session_player = app.findSessionPlayer(session_player_updates[i].id);

            if(session_player)
            {
                session_player.email = session_player_updates[i].email;
                session_player.name = session_player_updates[i].name;
                session_player.student_id = session_player_updates[i].student_id;
            }
        }
    
    } 
},

/** take survey completed by subject
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_update_survey_complete: function take_update_survey_complete(message_data){
    result = message_data;

    session_player = app.findSessionPlayer(result.player_id);
    session_player.survey_complete = true;
},