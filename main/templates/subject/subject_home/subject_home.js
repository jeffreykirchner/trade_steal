
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

{%include "subject/subject_home/graph/pixi_globals.js"%}

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
                    session_player : null, 
                    session : null,
                    reconnection_count : 0,

                    tick_tock : 0,

                    session_player_move_two_form_ids: {{session_player_move_two_form_ids|safe}},
                    session_player_move_three_form_ids: {{session_player_move_three_form_ids|safe}},
                    end_game_form_ids: {{end_game_form_ids|safe}},

                    pixi_loaded : false,             //true when pixi is loaded
                    // pixi_transfer_line : {visible : false},       //transfer line between two pixi containers  
                    transfer_in_progress : false,   //true when transfer is in progress
                    //pixi_transfer_source : null,     //source of transfer
                    //pixi_transfer_target : null,     //target of transfer
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
                    chat_recipients : "{{default_chat_recipient}}",
                    chat_recipients_index : 0,
                    chat_button_label : "{{default_chat_label}}",
                    chat_list_to_display : [],                //list of chats to display on screen

                    production_slider : 0,
                    production_slider_one : 50,
                    production_slider_two : 50,

                    good_one_waste : 0,
                    good_two_waste : 0,
                    good_one_need : 0,
                    good_two_needed : 0,
                    potential_earnings : 0,

                    end_game_modal_visible : false,
                    avatar_choice_modal_visible : false,

                    avatar_choice_grid_selected_row : 0,
                    avatar_choice_grid_selected_col : 0,

                    instructions : {{instructions|safe}},
                    instruction_pages_show_scroll : false,

                    // modals
                    moveTwoGoodsModal : null,
                    moveThreeGoodsModal : null,
                    avatarChoiceGridModal : null,
                    endGameModal : null,

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
            if(!app.session) return true;

            app.reconnection_count+=1;

            if(app.reconnection_count > app.session.parameter_set.reconnection_limit)
            {
                app.reconnection_failed = true;
                app.check_in_error_message = "Refresh your browser."
                return false;
            }

            return true;
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        takeMessage: function takeMessage(data) {

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            messageType = data.message.message_type;
            messageData = data.message.message_data;

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
                case "update_end_game":
                    app.takeEndGame(messageData);
                    break;
                case "name":
                    app.takeName(messageData);
                    break;
                case "avatar":
                    app.takeAvatar(messageData);
                    break;
                case "update_next_phase":
                    app.takeUpdateNextPhase(messageData);
                    break;
                case "next_instruction":
                    app.takeNextInstruction(messageData);
                    break;
                case "finish_instructions":
                    app.takeFinishInstructions(messageData);
                    break;
                
            }

            // if(!app.first_load_done)
            // {
            //     if(!app.session.started)
            //     {
            //        this.show_parameters = true;
            //     }
            // }

            this.working = false;
            //Vue.nextTick(app.update_sdgraph_canvas());
        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage: function sendMessage(messageType, messageText) {            

            this.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        /**
         * do after session has loaded
        */
        doFirstLoad: function doFirstLoad()
        {

            app.moveTwoGoodsModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('moveTwoGoodsModal'), {keyboard: false});
            app.moveThreeGoodsModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('moveThreeGoodsModal'), {keyboard: false});
            app.avatarChoiceGridModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('avatarChoiceGridModal'), {keyboard: false});
            app.endGameModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('endGameModal'), {keyboard: false});

            document.getElementById('moveTwoGoodsModal').addEventListener('hidden.bs.modal', app.hideTransferModal);
            document.getElementById('moveThreeGoodsModal').addEventListener('hidden.bs.modal', app.hideTransferModal);
            document.getElementById('avatarChoiceGridModal').addEventListener('hidden.bs.modal', app.hideChoiceGridModal);
            document.getElementById('endGameModal').addEventListener('hidden.bs.modal', app.hideEndGameModal);

            //if survery required forward to it.
            if(app.session.parameter_set.survey_required=='True' && 
               !app.session_player.survey_complete)
            {
                window.location.replace(app.session_player.survey_link);
            }

            //scroll to instructions
            Vue.nextTick(() => {
                document.getElementById('instructions_frame_a').addEventListener('scroll',
                    function()
                    {
                        app.scroll_update();
                    },
                    false
                )    
                
                app.scroll_update();
            })
            this.first_load_done = true;
        },

        /** send winsock request to get session info
        */
        sendGetSession: function sendGetSession(){
            app.sendMessage("get_session", {"playerKey" : this.playerKey});
        },
        
        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession: function takeGetSession(messageData){
            
            app.session = messageData.session;
            app.session_player = messageData.session_player;

            let parameter_set_player_local = app.get_parameter_set_player_from_player_id(app.session_player.id);

            app.current_town = parameter_set_player_local.town;

            app.destroyPixiPlayers();

            if(app.session.started)
            {
                app.production_slider_one =  app.session_player.good_one_production_rate;
                app.production_slider_two =  app.session_player.good_two_production_rate;

                if(app.production_slider_one>50){
                    app.production_slider = 50-app.production_slider_one;
                }
                else if(app.production_slider_one<50){
                    app.production_slider = app.production_slider_two-50;
                }
            }
            else
            {
                
                
            }   
            
            if(!app.first_load_done)
            {
                Vue.nextTick(() => {
                    app.doFirstLoad();
                });
            }
            
            if(this.session.current_experiment_phase != 'Done')
            {
                if(!app.pixi_loaded)
                    Vue.nextTick(() => {
                        app.setupPixi();
                    });
                else
                {
                    Vue.nextTick(() => {
                        app.setupPixiPlayers();
                    });   
                }
                
                if(this.session.current_experiment_phase != 'Instructions')
                {
                    app.updateChatDisplay();         
                    Vue.nextTick(() => {
                        app.updateNoticeDisplayScroll();
                    });       
                }
                app.calcWaste();

                // if game is finished show modal
                if(app.session.finished)
                {
                    Vue.nextTick(() => {
                        this.showEndGameModal();
                    });
                }

                //if no avavtar show choioce grid
                Vue.nextTick(() => {
                    app.showAvatarChoiceGrid();
                });

            }

            if(this.session.current_experiment_phase == 'Instructions')
            {
                Vue.nextTick(() => {
                    this.processInstructionPage();
                    this.instructionDisplayScroll();
                });               
                
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

        /** update start status
        *    @param messageData {json} session day in json format
        */
        takeUpdateStartExperiment: function takeUpdateStartExperiment(messageData){
            app.takeGetSession(messageData);

            if(app.session.current_experiment_phase == "Instructions")
            {
                Vue.nextTick(() => {
                    app.instructionDisplayScroll();
                });  
                // setTimeout(app.instructionDisplayScroll, 250);
            }
        },

        /** update reset status
        *    @param messageData {json} session day in json format
        */
        takeUpdateResetExperiment: function takeUpdateResetExperiment(messageData){
            app.takeGetSession(messageData);

            this.production_slider_one = 50;
            this.production_slider_two = 50;
            this.production_slider = 0;
            this.avatar_choice_grid_selected_row = 0;
            this.avatar_choice_grid_selected_col = 0;

            app.endGameModal.hide();
            this.closeMoveModal();
        },

        /**
        * update time and start status
        */
        takeUpdateTime: function takeUpdateTime(messageData){
            let result = messageData.result;
            let status = messageData.value;
            let notice_list = messageData.notice_list;

            if(status == "fail") return;

            this.session.started = result.started;
            this.session.current_period = result.current_period;
            this.session.current_period_phase = result.current_period_phase;
            this.session.time_remaining = result.time_remaining;
            this.session.timer_running = result.timer_running;
            this.session.finished = result.finished;

            this.tick_tock = this.session.time_remaining % 2;

            app.takeUpdateGoods({result : result.session_players});

            //update subject earnings
            this.session_player.earnings = result.session_player_earnings.earnings;

            if(notice_list.length > 0)
            {
                this.session_player.notices.push(notice_list[0]);
                // setTimeout(app.updateNoticeDisplayScroll, 250);
                Vue.nextTick(() => {
                    app.updateNoticeDisplayScroll();
                }); 

            }

            //if start production phase close transfer
            if(this.session.current_period_phase == "Production" &&
               this.session.time_remaining==this.session.parameter_set.period_length_production)
            {
                this.closeMoveModal();
            }

            //session complete
            if(app.session.finished)
            {
                this.showEndGameModal();
            }            
        },

        /**
         * if needed show avatar choice grid
         */
        showAvatarChoiceGrid: function showAvatarChoiceGrid(){

            if((this.session.parameter_set.avatar_assignment_mode == 'Subject Select' || 
                this.session.parameter_set.avatar_assignment_mode == 'Best Match') &&
                this.session.current_experiment_phase == "Selection" &&
                !this.avatar_choice_modal_visible)

            {
                app.avatarChoiceGridModal.toggle();

                this.avatar_choice_modal_visible=true;

                if(this.session_player.avatar != null)
                {
                    this.take_choice_grid_label(this.session_player.avatar.label)
                }
            }
        },

        /**
         * show the end game modal
         */
        showEndGameModal: function showEndGameModal(){
            if(this.end_game_modal_visible) return;

            //hide transfer modals
            this.closeMoveModal();

            //show endgame modal
            app.endGameModal.toggle();

            this.end_game_modal_visible = true;
        },

         /**
         * take end of game notice
         */
        takeEndGame: function takeEndGame(messageData){

        },

        /**
         * update players in group
         */
        takeUpdateGroups: function takeUpdateGroups(messageData){
            app.destroyPixiPlayers();

            this.session.session_players = messageData.result.session_players;

            setTimeout(app.setupPixiPlayers, 250);

            // document.getElementById("chat_all_id").click();
           

            if(app.session.parameter_set.private_chat == 'True')
            {
                app.chat_recipients = "NONE";
                app.chat_recipients_index = 0;
                app.chat_button_label = "Select Recipient";
                
                //deselect group chat
                if(app.session.parameter_set.group_chat == 'True')
                {
                    let b = document.getElementById("chat_all_id");
                    b.classList.remove('active');
                    b.checked = false;
                }

                //deselect group chat
                for(p in app.session.session_players)
                {
                    let s = "chat_invididual_" + app.session.session_players[p].id + "_id";
                    let b = document.getElementById(s);

                    if(b)
                    {
                        b.classList.remove('active');
                        b.checked = false;
                    }
                }
            }

            app.calcWaste();
        },

        /** take next period response
         * @param messageData {json}
        */
        takeUpdateNextPhase: function takeUpdateNextPhase(messageData){
            app.avatarChoiceGridModal.hide();
            app.endGameModal.hide();

            app.destroyPixiPlayers();

            this.session.current_experiment_phase = messageData.session.current_experiment_phase;
            this.session.session_players = messageData.session_players;
            this.session_player = messageData.session_player;

            Vue.nextTick(() => {
                // setTimeout(app.setupPixiPlayers, 250);
                app.setupPixiPlayers();
            });

            app.updateChatDisplay();
            app.calcWaste();    
            if(app.session.current_experiment_phase == "Instructions")
            {
                Vue.nextTick(() => {
                    app.instructionDisplayScroll();
                });
            }    
            
            app.showAvatarChoiceGrid();    
        },

        /** hide choice grid modal modal
        */
        hideChoiceGridModal: function hideChoiceGridModal(){
            this.avatar_choice_modal_visible=false;
        },

        /** hide choice grid modal modal
        */
        hideEndGameModal: function hideEndGameModal(){
            this.end_game_modal_visible=false;
        },

        //do nothing on when enter pressed for post
        onSubmit: function onSubmit(){
            //do nothing
        },
        
        {%include "subject/subject_home/graph/graph_card.js"%}
        {%include "subject/subject_home/graph/helpers.js"%}
        {%include "subject/subject_home/chat/chat_card.js"%}
        {%include "subject/subject_home/production/production_card.js"%}
        {%include "subject/subject_home/earnings/earnings_card.js"%}
        {%include "subject/subject_home/summary/summary_card.js"%}
        {%include "subject/subject_home/test_mode/test_mode.js"%}
        {%include "subject/subject_home/avatar_choice_grid/avatar_choice_grid.js"%}
        {%include "subject/subject_home/instructions/instructions_card.js"%}
    
        /** clear form error messages
        */
        clearMainFormErrors: function clearMainFormErrors(){
            
            s = this.session_player_move_two_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = this.session_player_move_three_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = this.end_game_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }
        },

        /** display form error messages
        */
        displayErrors: function displayErrors(errors){
            for(var e in errors)
            {
                for(let e in errors)
                {
                    //e = document.getElementById("id_" + e).getAttribute("class", "form-control is-invalid")
                    let str='<span id=id_errors_'+ e +' class="text-danger">';
                    
                    for(let i in errors[e])
                    {
                        str +=errors[e][i] + '<br>';
                    }

                    str+='</span>';

                    document.getElementById("div_id_" + e).insertAdjacentHTML('beforeend', str);
                    document.getElementById("div_id_" + e).scrollIntoView(); 
                }

            }
        }, 

    },

    mounted(){

        {%if session.parameter_set.test_mode%} setTimeout(this.doTestMode, this.randomNumber(1000 , 10000)); {%endif%}

        window.addEventListener('resize', this.handleResize);
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  