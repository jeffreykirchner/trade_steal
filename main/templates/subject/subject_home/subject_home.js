
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

{%include "subject/subject_home/graph/pixi_globals.js"%}

//prevent right click
document.addEventListener('contextmenu', event => event.preventDefault());

let worker = null;

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chat_socket : "",
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
                    test_mode : {%if session.parameter_set.test_mode%}true{%else%}false{%endif%},

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
                    chat_error_message : "",

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
                    avatar_choice_grid_selected_id : null,

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
        handle_socket_connected: function handle_socket_connected(){            
            app.send_get_session();
            app.working = false;
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
        take_message: function take_message(data) {

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            message_type = data.message.message_type;
            message_data = data.message.message_data;

            switch(message_type) {                
                case "get_session":
                    app.take_get_session(message_data);
                    break; 
                case "update_move_goods":
                    app.takeUpdateMoveGoods(message_data);
                    break;
                case "update_start_experiment":
                    app.take_update_start_experiment(message_data);
                    break;
                case "update_reset_experiment":
                    app.take_update_reset_experiment(message_data);
                    break;
                case "update_chat":
                    app.take_update_chat(message_data);
                    break;
                case "update_time":
                    app.take_update_time(message_data);
                    break;
                case "update_production_time":
                    app.takeProduction(message_data);
                    break;
                case "update_groups":
                    app.take_update_groups(message_data);
                    break;
                case "update_end_game":
                    app.takeEndGame(message_data);
                    break;
                case "name":
                    app.takeName(message_data);
                    break;
                case "avatar":
                    app.take_avatar(message_data);
                    break;
                case "update_next_phase":
                    app.take_update_next_phase(message_data);
                    break;
                case "next_instruction":
                    app.take_next_instruction(message_data);
                    break;
                case "finish_instructions":
                    app.take_finish_instructions(message_data);
                    break;
                
            }

            // if(!app.first_load_done)
            // {
            //     if(!app.session.started)
            //     {
            //        this.show_parameters = true;
            //     }
            // }

            //this.working = false;
            //Vue.nextTick(app.update_sdgraph_canvas());
        },

        /** send websocket message to server
        *    @param message_type {string} type of message sent to server
        *    @param message_text {json} body of message being sent to server
        *    @param message_target {string} who message is being sent to
        */
        send_message: function send_message(message_type, message_text, message_target="self") {
            //send socket message to server

            this.chat_socket.send(JSON.stringify({
                    'message_type': message_type,
                    'message_text': message_text,
                    'message_target': message_target,
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
        send_get_session: function send_get_session(){
            app.send_message("get_session", {"playerKey" : this.playerKey});
        },
        
        /** take create new session
        *    @param message_data {json} session day in json format
        */
        take_get_session: function take_get_session(message_data){
            
            app.session = message_data.session;
            app.session_player = message_data.session_player;

            let parameter_set_player_local = app.get_parameter_set_player_from_player_id(app.session_player.id);

            app.current_town = parameter_set_player_local.town;

            app.destroy_pixi_players();

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
                        app.setup_pixi_players();
                    });   
                }
                
                if(this.session.current_experiment_phase != 'Instructions')
                {
                    app.update_chat_display();         
                    Vue.nextTick(() => {
                        app.update_notice_displayScroll();
                    });       
                }
                app.calc_waste();

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
                    this.process_instruction_page();
                    this.instruction_display_scroll();
                });               
                
            }
        },

        /**
         * handle window resize event
         */
        handle_resize: function handle_resize(){                

            setTimeout(function(){
                let canvas = document.getElementById('sd_graph_id');
                app.canvas_width = canvas.width;
                app.canvas_height = canvas.height;
                app.canvas_scale_height = app.canvas_height / app.grid_y;
                app.canvas_scale_width = app.canvas_width / app.grid_x;

                app.setup_pixi_players();
            }, 250);
        },

        /** update start status
        *    @param message_data {json} session day in json format
        */
        take_update_start_experiment: function take_update_start_experiment(message_data){
            app.take_get_session(message_data);

            if(app.session.current_experiment_phase == "Instructions")
            {
                Vue.nextTick(() => {
                    app.instruction_display_scroll();
                });  
                // setTimeout(app.instruction_display_scroll, 250);
            }
        },

        /** update reset status
        *    @param message_data {json} session day in json format
        */
        take_update_reset_experiment: function take_update_reset_experiment(message_data){
            app.destroy_pixi_players();

            app.take_get_session(message_data);

            this.production_slider_one = 50;
            this.production_slider_two = 50;
            this.production_slider = 0;
            this.avatar_choice_grid_selected_row = 0;
            this.avatar_choice_grid_selected_col = 0;

            app.endGameModal.hide();
            this.close_move_modal();
            app.avatarChoiceGridModal.hide();
        },

        /**
        * update time and start status
        */
        take_update_time: function take_update_time(message_data){
            let result = message_data.result;
            let status = message_data.value;
            let notice_list = message_data.notice_list;

            if(status == "fail") return;

            this.session.started = result.started;
            this.session.current_period = result.current_period;
            this.session.current_period_phase = result.current_period_phase;
            this.session.time_remaining = result.time_remaining;
            this.session.timer_running = result.timer_running;
            this.session.finished = result.finished;

            this.tick_tock = this.session.time_remaining % 2;

            app.take_update_goods({result : result.session_players});

            //update subject earnings
            this.session_player.earnings = result.session_player_earnings.earnings;

            if(notice_list.length > 0)
            {
                this.session_player.notices.push(notice_list[0]);
                // setTimeout(app.update_notice_displayScroll, 250);
                Vue.nextTick(() => {
                    app.update_notice_displayScroll();
                }); 

            }

            //if start production phase close transfer
            if(this.session.current_period_phase == "Production" &&
               this.session.time_remaining==this.session.parameter_set.period_length_production)
            {
                this.close_move_modal();
                app.working = false;
            }

            //session complete
            if(app.session.finished)
            {
                this.close_move_modal();
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
            this.close_move_modal();

            //show endgame modal
            app.endGameModal.toggle();

            this.end_game_modal_visible = true;
        },

         /**
         * take end of game notice
         */
        takeEndGame: function takeEndGame(message_data){

        },

        /**
         * update players in group
         */
        take_update_groups: function take_update_groups(message_data){
            app.destroy_pixi_players();

            app.session.session_players = message_data.result.session_players;
            app.session.session_players_order = message_data.result.session_players_order;

            setTimeout(app.setup_pixi_players, 250);

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
                    let session_player = app.session.session_players[p];
                    let s = "chat_invididual_" + session_player.id + "_id";
                    let b = document.getElementById(s);

                    if(b)
                    {
                        b.classList.remove('active');
                        b.checked = false;
                    }
                }
            }

            app.calc_waste();
        },

        /** take next period response
         * @param message_data {json}
        */
        take_update_next_phase: function take_update_next_phase(message_data){
            app.avatarChoiceGridModal.hide();
            app.endGameModal.hide();

            app.destroy_pixi_players();

            this.session.current_experiment_phase = message_data.session.current_experiment_phase;
            this.session.session_players = message_data.session_players;
            this.session_player = message_data.session_player;

            Vue.nextTick(() => {
                // setTimeout(app.setup_pixi_players, 250);
                app.setup_pixi_players();
            });

            app.update_chat_display();
            app.calc_waste();    
            if(app.session.current_experiment_phase == "Instructions")
            {
                Vue.nextTick(() => {
                    app.instruction_display_scroll();
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
        clear_main_form_errors: function clear_main_form_errors(){
            
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
        display_errors: function display_errors(errors){
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

        {%if session.parameter_set.test_mode%} setTimeout(this.doTestMode, this.randomNumber(1000 , 1500)); {%endif%}

        window.addEventListener('resize', this.handle_resize);
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  