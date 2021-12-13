
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    is_subject : true,
                    working : false,
                    first_load_done : false,                       //true after software is loaded for the first time
                    playerKey : "{{session_player.player_key}}",
                    owner_color : 0xA9DFBF,
                    other_color : 0xD3D3D3,
                    session_player : {{session_player_json|safe}}, 
                    session : {{session_json|safe}},

                    session_player_move_two_form_ids: {{session_player_move_two_form_ids|safe}},
                    session_player_move_three_form_ids: {{session_player_move_three_form_ids|safe}},

                    pixi_loaded : false,             //true when pixi is loaded
                    pixi_transfer_line : {visible : false},       //transfer line between two pixi containers  
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

                    current_town : "0",

                    chat_text : "",
                    chat_recipients : "all",
                    chat_recipients_index : 0,
                    chat_button_label : "Everyone",
                    chat_list_to_display : [],                //list of chats to display on screen

                    production_slider : 0,
                    production_slider_one : 50,
                    production_slider_two : 50,

                    good_one_waste : 0,
                    good_two_waste : 0,
                    good_one_need : 0,
                    good_two_needed : 0,
                    potential_earnings : 0,
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
                case "move_goods":
                    app.takeMoveGoods(messageData);
                    break;  
                case "update_move_goods":
                    app.takeUpdateMoveGoods(messageData);
                    break;
                case "update_start_experiment":
                    app.takeUpdateStartExperiment(messageData);
                    break;
                case "update_reset_experiment":
                    app.takeUpdateResetExperiment(messageData);
                    break;
                case "chat":
                    app.takeChat(messageData);
                    break;
                case "update_chat":
                    app.takeUpdateChat(messageData);
                    break;
                case "update_time":
                    app.takeUpdateTime(messageData);
                    break;
                case "production_time":
                    app.takeProduction(messageData);
                    break;
                case "update_groups":
                    app.takeUpdateGroups(messageData);
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
            app.sendMessage("get_session",{"playerKey" : app.$data.playerKey});
        },
        
        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession(messageData){
            
            app.destroyPixiPlayers();

            app.$data.session = messageData.status.session;
            app.$data.session_player = messageData.status.session_player;

            app.$data.current_town = app.$data.session_player.parameter_set_player.town;

            if(app.$data.session.started)
            {
                app.$data.production_slider_one =  app.$data.session_player.good_one_production_rate;
                app.$data.production_slider_two =  app.$data.session_player.good_two_production_rate;

                if(app.$data.production_slider_one>50){
                    app.$data.production_slider = 50-app.$data.production_slider_one;
                }
                else if(app.$data.production_slider_one<50){
                    app.$data.production_slider = app.$data.production_slider_two-50;
                }
            }
            else
            {
                
            }                       

            if(!app.$data.pixi_loaded)
                setTimeout(app.setupPixi, 250);
            else
            {
                setTimeout(app.setupPixiPlayers, 250);
            }
            
            app.updateChatDisplay();
            app.calcWaste();
        },

        /** update start status
        *    @param messageData {json} session day in json format
        */
        takeUpdateStartExperiment(messageData){
            app.takeGetSession(messageData);
        },

        /** update reset status
        *    @param messageData {json} session day in json format
        */
        takeUpdateResetExperiment(messageData){
            app.takeGetSession(messageData);
            app.$data.production_slider_one = 50;
            app.$data.production_slider_two = 50;
            app.$data.production_slider=0;
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

            //update subject earnings
            app.$data.session_player.earnings = result.session_player_earnings.earnings;
            
        },

        /**
         * update players in group
         */
        takeUpdateGroups(messageData){
            app.destroyPixiPlayers();

            app.$data.session.session_players = messageData.status.result.session_players;

            setTimeout(app.setupPixiPlayers, 250);

            app.updateChatDisplay();
            app.calcWaste();
        },

        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },
        
        {%include "subject/subject_home/graph/graph_card.js"%}
        {%include "subject/subject_home/chat/chat_card.js"%}
        {%include "subject/subject_home/production/production_card.js"%}
        {%include "subject/subject_home/earnings/earnings_card.js"%}
        {%include "subject/subject_home/summary/summary_card.js"%}
    
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

        {%if session.parameter_set.test_mode%}
        /**
         * do random self test actions
         */
         randomNumber(min, max){
            //return a random number between min and max
            min = Math.ceil(min);
            max = Math.floor(max+1);
            return Math.floor(Math.random() * (max - min) + min);
        },

        doTestMode(){
            {%if DEBUG%}
            console.log("Do Test Mode");
            {%endif%}

            if(this.$data.session.started &&
               this.$data.session.parameter_set.test_mode)
            {
                //do chat
                if(this.chat_text != "")
                {
                    this.sendChat()
                }
                else
                {
                    r = this.randomNumber(20 ,5);
                    for(let i=0;i<r;i++)
                    {
                        v = this.randomNumber(122, 48);
                        this.chat_text += String.fromCharCode(v);
                    }
                
                }
            }

            setTimeout(this.doTestMode, this.randomNumber(10000 , 1000));
        },
        {%endif%}
    },

    mounted(){

        $('#moveTwoGoodsModal').on("hidden.bs.modal", this.hideTransferModal);
        $('#moveThreeGoodsModal').on("hidden.bs.modal", this.hideTransferModal);
        {%if session.parameter_set.test_mode%} setTimeout(this.doTestMode, this.randomNumber(10000 , 1000)); {%endif%}

    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  