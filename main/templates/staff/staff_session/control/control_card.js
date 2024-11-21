/**start the experiment
*/
start_experiment: function start_experiment(){
    app.working = true;
    app.send_message("start_experiment", {});
},

/** take start experiment response
 * @param message_data {json}
*/
take_start_experiment: function take_start_experiment(message_data){
    app.take_get_Session(message_data);
},

/** update start status
*    @param message_data {json} session day in json format
*/
take_update_start_experiment: function take_update_start_experiment(message_data){
    app.take_get_Session(message_data);
},

/** update start status
*    @param message_data {json} session day in json format
*/
take_update_reset_experiment: function take_update_reset_experiment(message_data){
    app.change_town_view()
    app.chat_list_to_display=[];
    app.take_get_Session(message_data);

    Vue.nextTick(app.update_graph_canvas());

    if(app.timer_warning_timeout)
    {
        clearTimeout(app.timer_warning_timeout);
        app.timer_warning = false;
    }
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
    app.send_message("reset_experiment", {});
},

// /** take reset experiment response
//  * @param message_data {json}
// */
// takeResetExperiment: function takeResetExperiment(message_data){
//     app.change_town_view()
//     app.chat_list_to_display=[];
//     app.take_get_Session(message_data);

//     Vue.nextTick(app.update_graph_canvas());

//     if(app.timer_warning_timeout)
//     {
//         clearTimeout(app.timer_warning_timeout);
//         app.timer_warning = false;
//     }
// },

resetConnections: function resetConnections(){
    if (!confirm('Reset connection status?.')) {
        return;
    }

    app.working = true;
    app.send_message("reset_connections", {});
},

/** update start status
*    @param message_data {json} session day in json format
*/
take_update_reset_connections: function take_update_reset_connections(message_data){
    app.take_get_Session(message_data);
},

/** take reset experiment response
 * @param message_data {json}
*/
takeResetConnections: function takeResetConnections(message_data){
    app.take_get_Session(message_data);
},

/**advance to next phase
*/
next_experiment_phase: function next_experiment_phase(){

    if (!confirm('Continue to the next phase of the experiment?')) {
        return;
    }
    
    app.working = true;
    app.send_message("next_phase", {});
},

/** take next period response
 * @param message_data {json}
*/
take_next_phase: function take_next_phase(message_data){
    
    this.session.current_experiment_phase = message_data.current_experiment_phase;
    this.updatePhaseButtonText();

},

/** take next period response
 * @param message_data {json}
*/
take_update_next_phase: function take_update_next_phase(message_data){
    
    this.session.current_experiment_phase = message_data.current_experiment_phase;
    this.updatePhaseButtonText();
    
    app.takeUpdatePeriod(message_data.period_update);
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

    app.send_message("start_timer", {action : action});
},

/** take start experiment response
 * @param message_data {json}
*/
take_start_timer: function take_start_timer(message_data){
    if(worker) worker.terminate();

    if("result" in message_data) app.take_update_time(message_data);
    // app.session.timer_running = message_data.result.timer_running;

    if(app.session.timer_running)
    {
        worker = new Worker("/static/js/worker_timer.js");

        worker.onmessage = function (evt) {   
            app.send_message("continue_timer", {});
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
    app.send_message("end_early", {});
},

/** take reset experiment response
 * @param message_data {json}
*/
take_end_early: function take_end_early(message_data){
   this.session.parameter_set.period_count = message_data.period_count;
},

/** send invitations
*/
sendSendInvitations: function sendSendInvitations(){

    this.send_messageModalForm.text = tinymce.get("id_invitation_text").getContent();

    if(this.send_messageModalForm.subject == "" || this.send_messageModalForm.text == "")
    {
        this.emailResult = "Error: Please enter a subject and email body.";
        return;
    }

    this.cancelModal = false;
    this.working = true;
    this.emailResult = "Sending ...";

    app.send_message("send_invitations",
                   {"formData" : this.send_messageModalForm});
},

/** take update subject response
 * @param message_data {json} result of update, either sucess or fail with errors
*/
take_send_invitations: function take_send_invitations(message_data){
    app.clearMainFormErrors();

    if(message_data.value == "success")
    {           
        this.emailResult = "Result: " + message_data.result.email_result.mail_count.toString() + " messages sent.";

        this.session.invitation_subject = message_data.result.invitation_subject;
        this.session.invitation_text = message_data.result.invitation_text;
    } 
    else
    {
        this.emailResult = message_data.result;
    } 
},

/** show edit subject modal
*/
showSendInvitations: function showSendInvitations(){

    app.cancelModal=true;

    app.send_messageModalForm.subject = app.session.invitation_subject;
    app.send_messageModalForm.text = app.session.invitation_text;

    tinymce.get("id_invitation_text").setContent(app.send_messageModalForm.text);
    
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
    this.send_messageModalForm.subject = this.emailDefaultSubject;
    
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
    app.send_message("refresh_screens", {});
},

/**
 * take refresh screens
 */
take_refresh_screens: function take_refresh_screens(message_data){
    if(message_data.session != {})
    {           
        app.session = message_data.session;
    } 
    else
    {
       
    }
},