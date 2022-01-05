
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    is_subject : false,
                    first_load_done : false,          //true after software is loaded for the first time
                    sessionID : {{session.id}},
                    sessionKey : "{{session.session_key}}",
                    other_color : 0xD3D3D3,
                    session : {{session_json|safe}},

                    session_player_move_two_form_ids: {{session_player_move_two_form_ids|safe}},
                    session_player_move_three_form_ids: {{session_player_move_three_form_ids|safe}},

                    move_to_next_phase_text : 'Start Next Experiment Phase',

                    pixi_loaded : false,             //true when pixi is loaded
                    pixi_transfer_line : null,       //transfer line between two pixi containers  
                    pixi_transfer_source : null,     //source of transfer
                    pixi_transfer_target : null,     //target of transfer
                    pixi_modal_open : false,         //true whe pixi modal is open
                    pixi_transfer_source_modal_string : "",   //source string shown on transfer modal
                    pixi_transfer_target_modal_string : "" ,  //target string shown on transfer modal

                    transfer_source_modal_string : "",   //source string shown on transfer modal
                    transfer_target_modal_string : "" ,  //target string shown on transfer modal

                    transfer_modal_good_one_rgb : 0x000000,   //good one color shown on transfer modal
                    transfer_modal_good_two_rgb : 0x000000 ,  //good two color shown on transfer modal
                    transfer_modal_good_three_rgb : 0x000000 ,  //good three color shown on transfer modal

                    transfer_modal_good_one_name : "",   //good one name shown on transfer modal
                    transfer_modal_good_two_name : "" ,  //good two name shown on transfer modal
                    transfer_modal_good_three_name : "" ,  //good three name shown on transfer modal

                    transfer_good_one_amount : 0, //good one amount to be transfered
                    transfer_good_two_amount : 0, //good two amount to be transfered
                    transfer_good_three_amount : 0, //good three amount to be transfered

                    current_town : "1",

                    chat_list_to_display : [],                //list of chats to display on screen

                    data_downloading : false,                   //show spinner when data downloading
                }},
    methods: {

        /** fire when websocket connects to server
        */
        handleSocketConnected(){            
            app.sendGetSession();
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        takeMessage(data) {

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            messageType = data.message.messageType;
            messageData = data.message.messageData;

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
            }

            if(!app.$data.first_load_done)
            {
                if(!app.$data.session.started)
                {
                    app.$data.show_parameters = true;
                }
            }

            app.$data.first_load_done = true;

            app.working = false;
            //Vue.nextTick(app.update_sdgraph_canvas());
        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage(messageType, messageText) {
            

            app.$data.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        /** send winsock request to get session info
        */
        sendGetSession(){
            app.sendMessage("get_session",{"sessionKey" : app.$data.sessionKey});
        },

        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession(messageData){
            
            app.destroyPixiPlayers();

            app.$data.session = messageData.session;

            if(app.$data.session.started)
            {
                
            }
            else
            {
                
            }
            
            if(!app.$data.pixi_loaded)
                setTimeout(app.setupPixi, 250);       
            else
                setTimeout(app.setupPixiPlayers, 250);
            
            app.updateChatDisplay(true);
            app.updatePhaseButtonText();
        },

       
        /**update text of move on button based on current state
         */
        updatePhaseButtonText(){
            if(this.session.finished && this.session.current_experiment_phase == "Done")
            {
                this.move_to_next_phase_text = '** Experiment complete **';
            }
            else if(this.session.finished && this.session.current_experiment_phase != "Done")
            {
                this.move_to_next_phase_text = 'Complete Expermient <i class="fas fa-flag-checkered"></i>';
            }
            else if(this.session.current_experiment_phase == "Run")
            {
                this.move_to_next_phase_text = 'Running ...';
            }
            else if(this.session.started && !this.session.finished)
            {
                if(this.session.current_experiment_phase == "Selection" && this.session.parameter_set.show_instructions == "True")
                {
                    this.move_to_next_phase_text = 'Show Instrutions <i class="fas fa-map"></i>';
                }
                else
                {
                    this.move_to_next_phase_text = 'Start Expermient <i class="far fa-play-circle"></i>';
                }
            }
        },

        /** take updated data from goods being moved by another player
        *    @param messageData {json} session day in json format
        */
        takeUpdateChat(messageData){
            
            let result = messageData.status;
            let chat = result.chat;
            let town = result.town;

            if(app.$data.session.chat_all[town].length>=100)
                app.$data.session.chat_all[town].shift();
            
            app.$data.session.chat_all[town].push(chat);
            app.updateChatDisplay(false);
        },

        /**
         * update chat displayed based on town chosen
         */
        updateChatDisplay(force_scroll){
            
            app.$data.chat_list_to_display=Array.from(app.$data.session.chat_all[parseInt(app.$data.current_town)]);

            //add spacers
            for(let i=app.$data.chat_list_to_display.length;i<18;i++)
            {
                app.$data.chat_list_to_display.unshift({id:i*-1,sender_label:"", text:"|", sender_id:0, chat_type:'All'})
            }

            //scroll to view
            if(app.$data.chat_list_to_display.length>0)
            {
                Vue.nextTick(() => {app.updateChatDisplayScroll(force_scroll)});        
            }
        },

        /**
         * scroll to newest chat element
         */
        updateChatDisplayScroll(force_scroll){

            if(window.innerHeight + window.pageYOffset >= document.body.offsetHeight || force_scroll)
            {
                var elmnt = document.getElementById("chat_id_" + app.$data.chat_list_to_display[app.$data.chat_list_to_display.length-1].id.toString());
                elmnt.scrollIntoView(); 
            }
        },

        /**
         * update time and start status
         */
        takeUpdateTime(messageData){

            let result = messageData.status.result;
            let status = messageData.status.value;

            if(status == "fail") return;

            app.$data.session.started = result.started;
            app.$data.session.current_period = result.current_period;
            app.$data.session.current_period_phase = result.current_period_phase;
            app.$data.session.time_remaining = result.time_remaining;
            app.$data.session.timer_running = result.timer_running;
            app.$data.session.finished = result.finished;

            app.takeUpdateGoods({status : {result : result.session_players}});
            app.takeUpdateEarnings(messageData);

            app.updatePhaseButtonText();
        },

        /**
         * take update end game
         */
         takeUpdateEndGame(messageData){

         },

        /**
         * change the town shown
         */
        change_town_view(){
            app.destroyPixiPlayers();
            app.setupPixiPlayers();
            app.updateChatDisplay(true);
        },
        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },
        
        {%include "staff/staff_session/control/control_card.js"%}
        {%include "staff/staff_session/session/session_card.js"%}
        {%include "subject/subject_home/graph/graph_card.js"%}
        {%include "staff/staff_session/subjects/subjects_card.js"%}
        {%include "staff/staff_session/summary/summary_card.js"%}
        {%include "staff/staff_session/data/data_card.js"%}
    
        /** clear form error messages
        */
        clearMainFormErrors(){
            
            for(var item in app.$data.session)
            {
                $("#id_" + item).attr("class","form-control");
                $("#id_errors_" + item).remove();
            }

            s = app.$data.session_player_move_two_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.$data.session_player_move_three_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }
        },

        /** display form error messages
        */
        displayErrors(errors){
            for(var e in errors)
            {
                $("#id_" + e).attr("class","form-control is-invalid")
                var str='<span id=id_errors_'+ e +' class="text-danger">';
                
                for(var i in errors[e])
                {
                    str +=errors[e][i] + '<br>';
                }

                str+='</span>';
                $("#div_id_" + e).append(str); 

                var elmnt = document.getElementById("div_id_" + e);
                elmnt.scrollIntoView(); 

            }
        }, 
    },

    mounted(){

        $('#moveTwoGoodsModal').on("hidden.bs.modal", this.hideTransferModal);
        $('#moveThreeGoodsModal').on("hidden.bs.modal", this.hideTransferModal);
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  