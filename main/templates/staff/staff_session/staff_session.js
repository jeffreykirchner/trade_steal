
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

{%include "subject/subject_home/graph/pixi_globals.js"%}

let worker = null;

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    is_subject : false,
                    first_load_done : false,          //true after software is loaded for the first time
                    helpText : "Loading ...",
                    sessionID : {{session.id}},
                    sessionKey : "{{session.session_key}}",
                    other_color : 0xD3D3D3,
                    session : null,

                    staff_edit_name_etc_form_ids: {{staff_edit_name_etc_form_ids|safe}},

                    move_to_next_phase_text : 'Start Next Experiment Phase',

                    pixi_loaded : false,             //true when pixi is loaded
                    // pixi_transfer_line : null,       //transfer line between two pixi containers  
                    //pixi_transfer_source : null,     //source of transfer
                    //pixi_transfer_target : null,     //target of transfer
                    pixi_modal_open : false,         //true whe pixi modal is open
                    pixi_transfer_source_modal_string : "",   //source string shown on transfer modal
                    pixi_transfer_target_modal_string : "" ,  //target string shown on transfer modal

                    transfer_source_modal_string : "",     //source string shown on transfer modal
                    transfer_target_modal_string : "" ,    //target string shown on transfer modal

                    transfer_modal_good_one_rgb : 0x000000,     //good one color shown on transfer modal
                    transfer_modal_good_two_rgb : 0x000000 ,    //good two color shown on transfer modal
                    transfer_modal_good_three_rgb : 0x000000 ,  //good three color shown on transfer modal

                    transfer_modal_good_one_name : "",     //good one name shown on transfer modal
                    transfer_modal_good_two_name : "" ,    //good two name shown on transfer modal
                    transfer_modal_good_three_name : "" ,  //good three name shown on transfer modal

                    transfer_good_one_amount : 0,         //good one amount to be transfered
                    transfer_good_two_amount : 0,         //good two amount to be transfered
                    transfer_good_three_amount : 0,       //good three amount to be transfered

                    current_town : "1",

                    chat_list_to_display : [],                  //list of chats to display on screen
                    notice_list_to_display : [],                //list of chats to display on screen

                    data_downloading : false,                   //show spinner when data downloading

                    staffEditNameEtcForm : {name : "", student_id : "", email : "", id : -1},
                    sendMessageModalForm : {subject : "", text : ""},

                    emailResult : "",                          //result of sending invitation emails
                    emailDefaultSubject : "{{parameters.invitation_subject}}",
                    emailDefaultText : `{{parameters.invitation_text|safe}}`,

                    csv_email_list : "",           //csv email list

                    timer_warning : false,
                    timer_warning_timeout : null,

                    //modals
                    edit_subject_modal: null,
                    edit_session_modal: null,
                    send_message_modal: null,
                    upload_email_modal: null,
                }},
    methods: {

        /** fire when websocket connects to server
        */
        handleSocketConnected: function handleSocketConnected(){            
            app.sendGetSession();
        },

        /** fire trys to connect to server
         * return true if re-connect should be allowed else false
        */
        handle_socket_connection_try: function handle_socket_connection_try(){         
            if(app.session) app.session.timer_running = false;
            if(worker) worker.terminate();
            return true;
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        takeMessage: function takeMessage(data){

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            messageType = data.message.message_type;
            messageData = data.message.message_data;

            switch(messageType) {                
                case "get_session":
                    app.takeGetSession(messageData);
                    break;
                case "update_session":
                    app.takeUpdateSession(messageData);
                    break;
                case "start_experiment":
                    app.takeStartExperiment(messageData);
                    break;
                case "update_start_experiment":
                    app.takeUpdateStartExperiment(messageData);
                    break;
                case "reset_experiment":
                    app.takeResetExperiment(messageData);
                    break;
                case "next_phase":
                    app.takeNextPhase(messageData);
                    break; 
                case "update_next_phase":
                    app.takeUpdateNextPhase(messageData);
                    break; 
                case "update_move_goods":
                    app.takeUpdateGoods(messageData);
                    app.takeUpdateNotice(messageData);
                    break;  
                case "update_reset_experiment":
                    app.takeUpdateResetExperiment(messageData);
                    break;
                case "update_chat":
                    app.takeUpdateChat(messageData);
                    break;
                case "update_time":
                    app.takeUpdateTime(messageData);
                    break;
                case "start_timer":
                    app.takeStartTimer(messageData);
                    break;   
                case "update_groups":
                    app.takeUpdateGroups(messageData);
                    break;  
                case "update_connection_status":
                    app.takeUpdateConnectionStatus(messageData);
                    break;   
                case "reset_connections":
                    app.takeResetConnections(messageData);
                    break; 
                case "update_reset_connections":
                    app.takeUpdateResetConnections(messageData);
                    break; 
                case "update_name":
                    app.takeUpdateName(messageData);
                    break;         
                case "download_summary_data":
                    app.takeDownloadSummaryData(messageData);
                    break;
                case "download_action_data":
                    app.takeDownloadActionData(messageData);
                    break;
                case "download_recruiter_data":
                    app.takeDownloadRecruiterData(messageData);
                    break;
                case "download_payment_data":
                    app.takeDownloadPaymentData(messageData);
                    break;
                case "update_avatar":
                    app.takeUpdateAvatar(messageData);
                    break;
                case "update_next_instruction":
                    app.takeNextInstruction(messageData);
                    break;
                case "update_finish_instructions":
                    app.takeFinishedInstructions(messageData);
                    break;
                case "help_doc":
                    app.takeLoadHelpDoc(messageData);
                    break;
                case "end_early":
                    app.takeEndEarly(messageData);
                    break;
                case "update_production_time":
                    app.takeUpdateProductionTime(messageData);
                    break;
                case "update_update_subject":
                    app.takeUpdateSubject(messageData);
                    break;
                case "send_invitations":
                    app.takeSendInvitations(messageData);
                    break;
                case "email_list":
                    app.takeUpdateEmailList(messageData);
                    break;
                case "update_anonymize_data":
                    app.takeAnonymizeData(messageData);
                    break;
                case "update_survey_complete":
                    app.take_update_survey_complete(messageData);
                    break;
                case "refresh_screens":
                    app.take_refresh_screens(messageData);
                    break;
                case "stop_timer_pulse":
                    app.take_stop_timer_pulse(messageData);
            }

            app.working = false;
            //Vue.nextTick(app.update_sdgraph_canvas());
        },

        /**
         * do after session has loaded
         */
        do_first_load: function do_first_load()
        {
            app.edit_subject_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('edit_subject_modal'), {keyboard: false});
            app.edit_session_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('edit_session_modal'), {keyboard: false});
            app.send_message_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('send_message_modal'), {keyboard: false});
            app.upload_email_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('upload_email_modal'), {keyboard: false});

            document.getElementById('edit_subject_modal').addEventListener('hidden.bs.modal', app.hide_edit_subject);
            document.getElementById('edit_session_modal').addEventListener('hidden.bs.modal', app.hide_edit_session);
            document.getElementById('send_message_modal').addEventListener('hidden.bs.modal', app.hide_send_invitations);
            document.getElementById('upload_email_modal').addEventListener('hidden.bs.modal', app.hide_send_email_list);

            tinyMCE.init({
                target: document.getElementById('id_invitation_text'),
                height : "400",
                theme: "silver",
                plugins: "directionality,paste,searchreplace,code",
                directionality: "{{ directionality }}",
            });
    
            // Prevent Bootstrap dialog from blocking focusin
            document.addEventListener('focusin', (e) => {
            if (e.target.closest(".tox-tinymce-aux, .moxman-window, .tam-assetmanager-root") !== null) {
                e.stopImmediatePropagation();
            }
            });

            app.first_load_done = true;

        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage:function sendMessage(messageType, messageText) {            

            this.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        /** send winsock request to get session info
        */
        sendGetSession: function sendGetSession(){
            app.sendMessage("get_session",{"sessionKey" : app.sessionKey});
        },

        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession: function takeGetSession(messageData){
            
            app.session = messageData.session;
            app.destroyPixiPlayers();
            
            if(app.session.started)
            {
                
            }
            else
            {
                
            }
            
            if(!app.pixi_loaded)
            {
                Vue.nextTick(() => {
                    app.setupPixi();
                });
                // setTimeout(app.setupPixi, 250);  
            }     
            else
            {
                Vue.nextTick(() => {
                    app.setupPixiPlayers();
                });
                // setTimeout(app.setupPixiPlayers, 250);
            }
            
            app.updateChatDisplay(true);
            app.updatePhaseButtonText();
            app.updateNoticeDisplay(true);        

            if(!app.first_load_done)
            {
                Vue.nextTick(() => {
                    app.do_first_load();
                    app.update_graph_canvas()
                });
            }
            else
            {
                
            }

            if(!app.session.finished)
            {
                let v = {};
                v.timer_running = app.session.timer_running;
                app.takeStartTimer(v);
            }
        },

        /**
         * handle window resize event
        */
        handleResize: function handleResize(){

            setTimeout(function(){
                let canvas = document.getElementById('sd_graph_id');
                app.canvas_width = canvas.width;
                app.canvas_height = canvas.height;
                app.canvas_scale_height = app.canvas_height / app.grid_y;
                app.canvas_scale_width = app.canvas_width / app.grid_x;

                app.setupPixiPlayers();
            }, 250);
        },

        /**update text of move on button based on current state
         */
        updatePhaseButtonText: function updatePhaseButtonText(){
            if(this.session.finished && this.session.current_experiment_phase == "Done")
            {
                this.move_to_next_phase_text = '** Session complete **';
            }
            else if(this.session.finished && this.session.current_experiment_phase != "Done")
            {
                this.move_to_next_phase_text = 'Complete Session <i class="fas fa-flag-checkered"></i>';
            }
            else if(this.session.current_experiment_phase == "Run")
            {
                this.move_to_next_phase_text = 'Running ...';
            }
            else if(this.session.started && !this.session.finished)
            {
                if(this.session.current_experiment_phase == "Selection")
                {
                    this.move_to_next_phase_text = 'Complete Avatar Selection <i class="far fa-play-circle"></i>';
                }
                else if(this.session.current_experiment_phase == "Instructions" && 
                        (this.session.parameter_set.avatar_assignment_mode == "Subject Select"))
                {

                    this.move_to_next_phase_text = 'Start Avatar Selection <i class="far fa-play-circle"></i>';
                }
                else if(this.session.current_experiment_phase == "Instructions")
                {
                    this.move_to_next_phase_text = 'Continue Session <i class="far fa-play-circle"></i>';
                }

                // && this.session.parameter_set.show_instructions == "True"
            }
        },

        /** take updated data from goods being moved by another player
        *    @param messageData {json} session day in json format
        */
        takeUpdateChat: function takeUpdateChat(messageData){
            
            let result = messageData;
            let chat = result.chat;
            let town = result.town;

            if(this.session.chat_all[town].length>=100)
                this.session.chat_all[town].shift();
            
            this.session.chat_all[town].push(chat);
            app.updateChatDisplay(false);
        },

        /**
         * update chat displayed based on town chosen
         */
        updateChatDisplay: function updateChatDisplay(force_scroll){
            
            this.chat_list_to_display=Array.from(this.session.chat_all[parseInt(this.current_town)]);
        },

        /**
         * update chat displayed based on town chosen
         */
        updateNoticeDisplay: function updateNoticeDisplay(forceScroll){            
            this.notice_list_to_display=Array.from(this.session.notices[parseInt(this.current_town)]);
            // setTimeout(function() {  app.updateNoticeDisplayScrollStaff(forceScroll); }, 250);
        },

        /**
         * show applicable notices.
         */
        takeUpdateNotice: function takeUpdateNotice(messageData){

            let result = messageData.result;

            for(i=0;i<result.length;i++)
            {
                if(result[i].notice)
                {
                    let session_player = app.findSessionPlayer(result[0].id);
                    let notice_parameter_set_player = app.get_parameter_set_player_from_player_id(session_player.id);
                    let town = notice_parameter_set_player.town; 
                    let notice = result[i].notice;
                    if(notice.show_on_staff)
                    {
                        if(this.session.notices[town].length >= 100)
                            this.session.notices[town].shift();
                        
                        this.session.notices[town].push(notice);
                        this.updateNoticeDisplay(false);
                         //scroll to view
                       
                    }
                }
            }

            
        },

        updateNoticeDisplayScrollStaff: function updateNoticeDisplayScrollStaff(force_scroll){
            if(!app.session.timer_running) return;

            if(window.innerHeight + window.pageYOffset >= document.body.offsetHeight || force_scroll)
            {
                if(this.notice_list_to_display.length==0) return;
            
                var elmnt = document.getElementById("notice_id_" + this.notice_list_to_display[this.notice_list_to_display.length-1].id.toString());
                elmnt.scrollIntoView();
                
            }
        },

        /**
         * update time and start status
         */
        takeUpdateTime: function takeUpdateTime(messageData){

            let result = messageData.result;
            let status = messageData.value;

            if(status == "fail") return;

            app.session.started = result.started;
            app.session.current_period = result.current_period;
            app.session.current_period_phase = result.current_period_phase;
            app.session.time_remaining = result.time_remaining;
            app.session.timer_running = result.timer_running;
            app.session.finished = result.finished;

            app.takeUpdateGoods({result : result.session_players});
            app.takeUpdateEarnings(messageData);
            app.takeUpdatePeriod(messageData.period_update);

            app.updatePhaseButtonText();

            if(app.timer_warning_timeout)
            {
                clearTimeout(app.timer_warning_timeout);
                app.timer_warning = false;
            }

            app.timer_warning_timeout = setTimeout(app.timerWarning, 5000);
        },

        /**
         * update single session period
         */
        takeUpdatePeriod: function takeUpdatePeriod(period_update){
            if(!period_update) return;

            app.session.session_periods[period_update.period_number-1] = period_update;
            Vue.nextTick(app.update_graph_canvas());
        },

        /**
         * take update end game
         */
        takeUpdateEndGame: function takeUpdateEndGame(messageData){

        },

        /**
         * change the town shown
         */
        change_town_view: function change_town_view(){
            app.destroyPixiPlayers();
            app.setupPixiPlayers();
            app.updateChatDisplay(true);
            app.updateNoticeDisplay(true);
        },

        //do nothing on when enter pressed for post
        onSubmit: function onSubmit(){
            //do nothing
        },
        
        {%include "staff/staff_session/control/control_card.js"%}
        {%include "staff/staff_session/session/session_card.js"%}
        {%include "subject/subject_home/graph/graph_card.js"%}
        {%include "subject/subject_home/graph/helpers.js"%}
        {%include "staff/staff_session/subjects/subjects_card.js"%}
        {%include "staff/staff_session/summary/summary_card.js"%}
        {%include "staff/staff_session/data/data_card.js"%}
        {%include "staff/staff_session/axis/axis_card.js"%}
        {%include "js/help_doc.js"%}
    
        /** clear form error messages
        */
        clearMainFormErrors: function clearMainFormErrors(){
            
            for(var item in app.session)
            {
                e = document.getElementById("id_errors_" + item);
                if(e) e.remove();
            }

            s = app.staff_edit_name_etc_form_ids;
            for(var i in s)
            {
                e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }
        },

        /** display form error messages
        */
        displayErrors: function displayErrors(errors){
            for(let e in errors)
                {
                    let str='<span id=id_errors_'+ e +' class="text-danger">';
                    
                    for(let i in errors[e])
                    {
                        str +=errors[e][i] + '<br>';
                    }

                    str+='</span>';

                    document.getElementById("div_id_" + e).insertAdjacentHTML('beforeend', str);
                    document.getElementById("div_id_" + e).scrollIntoView(); 
                }
        }, 
    },

    mounted(){
        window.addEventListener('resize', this.handleResize);
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  