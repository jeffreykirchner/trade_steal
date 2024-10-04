/**start the experiment
*/
start_experiment: function start_experiment(){
    app.working = true;
    app.sendMessage("start_experiment", {});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartExperiment: function takeStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateStartExperiment: function takeUpdateStartExperiment(messageData){
    app.takeGetSession(messageData);
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetExperiment: function takeUpdateResetExperiment(messageData){
    app.takeGetSession(messageData);
},

/**reset experiment, remove all bids, asks and trades
*/
reset_experiment: function reset_experiment(){
    if (!confirm('Reset session? All activity will be removed.')) {
        return;
    }

    if(worker) worker.terminate();
    app.session.timer_running = false;

    app.working = true;
    app.sendMessage("reset_experiment", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetExperiment: function takeResetExperiment(messageData){
    app.change_town_view()
    app.chat_list_to_display=[];
    app.takeGetSession(messageData);

    if(app.timer_warning_timeout)
    {
        clearTimeout(app.timer_warning_timeout);
        app.timer_warning = false;
    }
},

resetConnections: function resetConnections(){
    if (!confirm('Reset connection status?.')) {
        return;
    }

    app.working = true;
    app.sendMessage("reset_connections", {});
},

/** update start status
*    @param messageData {json} session day in json format
*/
takeUpdateResetConnections: function takeUpdateResetConnections(messageData){
    app.takeGetSession(messageData);
},

/** take reset experiment response
 * @param messageData {json}
*/
takeResetConnections: function takeResetConnections(messageData){
    app.takeGetSession(messageData);
},

/**advance to next phase
*/
next_experiment_phase: function next_experiment_phase(){

    if (!confirm('Continue to the next phase of the experiment?')) {
        return;
    }
    
    app.working = true;
    app.sendMessage("next_phase", {});
},

/** take next period response
 * @param messageData {json}
*/
takeNextPhase: function takeNextPhase(messageData){
    
    this.session.current_experiment_phase = messageData.status.current_experiment_phase;
    this.updatePhaseButtonText();

},

/** take next period response
 * @param messageData {json}
*/
takeUpdateNextPhase: function takeUpdateNextPhase(messageData){
    
    this.session.current_experiment_phase = messageData.status.current_experiment_phase;
    this.updatePhaseButtonText();
    
    app.takeUpdatePeriod(messageData.status.period_update);
},

/**
 * start the period timer
*/
startTimer: function startTimer(){
    app.working = true;

    let action = "";

    if(app.session.timer_running)
    {
        action = "stop";
    }
    else
    {
        action = "start";
    }

    app.sendMessage("start_timer", {action : action});
},

/** take start experiment response
 * @param messageData {json}
*/
takeStartTimer: function takeStartTimer(messageData){
    if(worker) worker.terminate();

    if("status" in messageData) app.takeUpdateTime(messageData);
    // app.session.timer_running = messageData.result.timer_running;

    if(app.session.timer_running)
    {
        worker = new Worker("/static/js/worker_timer.js");

        worker.onmessage = function (evt) {   
            app.sendMessage("continue_timer", {});
        };

        worker.postMessage(0);
    }
},

/**
 * stop local timer pulse 
 */
take_stop_timer_pulse: function take_stop_timer_pulse(){
    if(worker) worker.terminate();
},

/**reset experiment, remove all bids, asks and trades
*/
endEarly: function endEarly(){
    if (!confirm('End the experiment after this period completes?')) {
        return;
    }

    app.working = true;
    app.sendMessage("end_early", {});
},

/** take reset experiment response
 * @param messageData {json}
*/
takeEndEarly: function takeEndEarly(messageData){
   this.session.parameter_set.period_count = messageData.status.result;
},

/** send invitations
*/
sendSendInvitations: function sendSendInvitations(){

    this.sendMessageModalForm.text = tinymce.get("id_invitation_text").getContent();

    if(this.sendMessageModalForm.subject == "" || this.sendMessageModalForm.text == "")
    {
        this.emailResult = "Error: Please enter a subject and email body.";
        return;
    }

    this.cancelModal = false;
    this.working = true;
    this.emailResult = "Sending ...";

    app.sendMessage("send_invitations",
                   {"formData" : this.sendMessageModalForm});
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeSendInvitations: function takeSendInvitations(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {           
        this.emailResult = "Result: " + messageData.status.result.email_result.mail_count.toString() + " messages sent.";

        this.session.invitation_subject = messageData.status.result.invitation_subject;
        this.session.invitation_text = messageData.status.result.invitation_text;
    } 
    else
    {
        this.emailResult = messageData.status.result;
    } 
},

/** show edit subject modal
*/
showSendInvitations: function showSendInvitations(){

    app.cancelModal=true;

    app.sendMessageModalForm.subject = app.session.invitation_subject;
    app.sendMessageModalForm.text = app.session.invitation_text;

    tinymce.get("id_invitation_text").setContent(app.sendMessageModalForm.text);
    
    app.send_message_modal.show();
},

/** hide edit subject modal
*/
hideSendInvitations: function hideSendInvitations(){
    this.emailResult = "";
},

/**
 * fill invitation with default values
 */
fillDefaultInvitation: function fillDefaultInvitation(){
    this.sendMessageModalForm.subject = this.emailDefaultSubject;
    
    tinymce.get("id_invitation_text").setContent(this.emailDefaultText);
},

/**
 * send refresh screens
 */
send_refresh_screens: function send_refresh_screens(message_data){
    if (!confirm('Refresh the client and server screens?')) {
        return;
    }

    app.working = true;
    app.sendMessage("refresh_screens", {});
},

/**
 * take refresh screens
 */
take_refresh_screens: function take_refresh_screens(message_data){
    if(message_data.session != {})
    {           
        app.session = message_data.status.session;
    } 
    else
    {
       
    }
},