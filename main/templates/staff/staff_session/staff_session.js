
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
                    session : {
                        current_period : 1,
                        started : false,
                        locked : true,
                        start_date : "---",
                        current_period : 0,
                        finished : false,                        
                        parameter_set : {
                            id : 0,
                            period_count : 0,
                            period_length_production : 0,
                            period_length_trade : 0,
                            break_period_frequency : 0,
                            good_count : 2,
                            good_a_label : "",
                            good_b_label : "",
                            good_a_rgb_color : '#000000',
                            good_b_rgb_color : '#000000',
                            parameter_set_types : [{good_one_amount:""},
                                                   {good_one_amount:""}],                               
                        },
                        session_periods : [],
                        session_players : [],
                    },

                    session_player_move_two_form_ids: {{session_player_move_two_form_ids|safe}},
                    session_player_move_three_form_ids: {{session_player_move_three_form_ids|safe}},

                    move_to_next_period_text : 'Move to next period <i class="fas fa-fast-forward"></i>',

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
                case "next_period":
                    app.takeNextPeriod(messageData);
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
            
            app.updateChatDisplay();
        },

        /**update text of move on button based on current state
         */
        updateMoveOnButtonText(){
            if(app.$data.session.finished)
            {
                app.$data.move_to_next_period_text = '** Experiment complete **';
            }
            else if(app.$data.session.started)
            {
                if(app.$data.session.current_period == app.$data.session.parameter_set.number_of_periods)
                {
                    app.$data.move_to_next_period_text = 'Complete experiment <i class="fas fa-flag-checkered"></i>';
                }
                else
                {
                    app.$data.move_to_next_period_text = 'Move to next period <i class="fas fa-fast-forward"></i>';
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
            
            app.$data.session.chat_all[town].push(chat);
            app.updateChatDisplay();
        },

        /**
         * update chat displayed based on town chosen
         */
        updateChatDisplay(){
            
            app.$data.chat_list_to_display=Array.from(app.$data.session.chat_all[parseInt(app.$data.current_town)]);

            //add spacers
            for(let i=app.$data.chat_list_to_display.length;i<18;i++)
            {
                app.$data.chat_list_to_display.unshift({id:i*-1,sender_label:"", text:"|", sender_id:0, chat_type:'All'})
            }

            //scroll to view
            if(app.$data.chat_list_to_display.length>0)
            {
                Vue.nextTick(() => {app.updateChatDisplayScroll()});        
            }
        },

        /**
         * scroll to newest chat element
         */
        updateChatDisplayScroll(){
            var elmnt = document.getElementById("chat_id_" + app.$data.chat_list_to_display[app.$data.chat_list_to_display.length-1].id.toString());
            elmnt.scrollIntoView(); 
        },

        /**
         * change the town shown
         */
        change_town_view(){
            app.destroyPixiPlayers();
            app.setupPixiPlayers();
            app.updateChatDisplay();
        },
        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },
        
        {%include "staff/staff_session/control/control_card.js"%}
        {%include "staff/staff_session/session/session_card.js"%}
        {%include "subject/subject_home/graph/graph_card.js"%}
        {%include "staff/staff_session/subjects/subjects_card.js"%}
    
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

  