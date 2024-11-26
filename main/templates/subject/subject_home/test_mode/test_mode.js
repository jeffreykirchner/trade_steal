{%if session.parameter_set.test_mode%}

/**
 * do random self test actions
 */
random_number: function random_number(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
},

random_string: function random_string(min_length, max_length){

    s = "";
    r = app.random_number(min_length, max_length);

    for(let i=0;i<r;i++)
    {
        v = app.random_number(48, 122);
        s += String.fromCharCode(v);
    }

    return s;
},

do_test_mode: function do_test_mode(){
    {%if DEBUG%}
    console.log("Do Test Mode");
    {%endif%}

    if(worker) worker.terminate();

    if(app.end_game_modal_visible)
    {
        if(app.session_player.name == "")
        {
            document.getElementById("id_name").value =  app.random_string(5, 20);
            document.getElementById("id_student_id").value =  app.random_number(1000, 10000);

            app.send_name();
        }

        return;
    }

    if(app.session.started && app.test_mode)
    {
        switch (app.session.current_experiment_phase)
        {
            case "Selection":
                app.do_test_mode_selection();
                break;
            case "Instructions":
                app.do_test_mode_instructions();
                break;
            case "Run":
                app.do_test_mode_run();
                break;
            
        }        
       
    }

    // setTimeout(app.do_test_mode, app.random_number(1000 , 1500));
    worker = new Worker("/static/js/worker_test_mode.js");

    worker.onmessage = function (evt) {   
        app.do_test_mode();
    };

    worker.postMessage(0);
},

/**
 * test during selection phase
 */
 do_test_mode_selection: function do_test_mode_selection()
 {

    if(app.avatar_choice_grid_selected_row == 0 && app.avatar_choice_grid_selected_col == 0)
    {
        let r = app.random_number(1, app.session.parameter_set.avatar_grid_row_count);
        let c = app.random_number(1, app.session.parameter_set.avatar_grid_col_count);

        let parameter_set_avatar = app.get_grid_avatar(r, c);

        if(parameter_set_avatar.avatar == null) return;

        document.getElementById('choice_grid_' + r + '_' + c + '_id').click();
    }
    else if(app.session_player.avatar == null)
    {
        document.getElementById('submit_avatar_choice_id').click();
    }

 },

/**
 * test during instruction phase
 */
 do_test_mode_instructions: function do_test_mode_instructions()
 {
    if(app.session_player.instructions_finished) return;
    if(app.working) return;
    
    if(app.session_player.current_instruction == app.session_player.current_instruction_complete)
    {

        if(app.session_player.current_instruction == app.instructions.instruction_pages.length)
            document.getElementById("instructions_start_id").click();
        else
            document.getElementById("instructions_next_id").click();

    }else
    {
        switch (app.session_player.current_instruction)
        {            
            case app.instructions.action_page_production:
                document.getElementById("simulate_production_id").click();
                break;
            case app.instructions.action_page_move:
                if(app.pixi_modal_open)
                {
                    if(app.session.parameter_set.good_count==2)
                        document.getElementById("move_two_id").click();
                    else           
                        document.getElementById("move_three_id").click();        
                }
                else
                {
                    app.do_test_mode_move();
                }
                break;
            case app.instructions.action_page_chat:
                if(app.chat_text != "")
                {
                    document.getElementById("send_chat_id").click();                   
                }
                else
                {
                    app.do_test_mode_chat();
                }
                break;
        }
    }

    
 },

/**
 * test during run phase
 */
do_test_mode_run: function do_test_mode_run()
{
    //do chat
    let go = true;

    if(go)
        if(app.chat_text != "")
        {
            document.getElementById("send_chat_id").click();
            go=false;
        }

    //move goods
    if(go)
        if(app.pixi_modal_open)
        {
            if(app.session.current_period_phase != "Trade")
            {
                app.close_move_modal();
                return;
            }

            app.sendMoveGoods();
            go=false;
        }
    
    //update production
    if(go)
        if(app.production_slider_one != app.session_player.good_one_production_rate)
        {
            if(app.session.current_period_phase != "Trade")
            {
                return;
            }

            app.send_prodution();
            go=false;
        }
    
    if(app.session.finished) return;
        
    if(go)
        switch (app.random_number(1, 3)){
            case 1:
                app.do_test_mode_chat();
                break;
            
            case 2:
                app.do_test_mode_move();
                break;
            
            case 3:
                app.do_test_mode_production_update();
                break;
        }
},

/**
 * test mode chat
 */
do_test_mode_chat: function do_test_mode_chat(){

    let session_player_id = app.session.session_players_order[app.random_number(0, app.session.session_players_order.length-1)];
    let session_player_local = app.session.session_players[session_player_id];

    if(session_player_local.id == app.session_player.id)
    {
        if(app.session.parameter_set.group_chat=='True')
        {
            document.getElementById("chat_all_id").click();
            app.chat_text = app.random_string(5, 20);
        }
    }
    else
    {
        if(app.session.parameter_set.private_chat=='True')
        {
            document.getElementById('chat_invididual_' + session_player_local.id + '_id').click();
            app.chat_text = app.random_string(5, 20);
        }
    }

    
},

/**
 * test mode move
 */
do_test_mode_move: function do_test_mode_move(){
    if(app.session.current_period_phase != "Trade")
    {
        app.close_move_modal();
        return;
    }

    let session_player_source = null;
    let source_container = null;

    if(app.random_number(1, 2) == 1 || app.session.current_experiment_phase == "Instructions")
    {
        if(app.session.parameter_set.allow_stealing == "True" && app.session.current_experiment_phase != "Instructions")
        {
            let session_player_id = app.session.session_players_order[app.random_number(0, app.session.session_players_order.length-1)];
            session_player_source = app.session.session_players[session_player_id];        }
        else
        {
            session_player_source = app.session.session_players[app.session_player.id];            
        }

        let session_player_source_index = app.find_session_player_index(session_player_source.id);
        source_container = field_containers[session_player_source_index];        

        app.transfer_good_one_amount = app.random_number(0, session_player_source.good_one_field);
        app.transfer_good_two_amount = app.random_number(0, session_player_source.good_two_field);

        if(app.transfer_good_one_amount == 0 && app.transfer_good_two_amount == 0)
        {
            return;
        }
    }
    else
    {
        if(app.session.parameter_set.allow_stealing == "True")
        {
            let session_player_id = app.session.session_players_order[app.random_number(0, app.session.session_players_order.length-1)];
            session_player_source = app.session.session_players[session_player_id];  
        }
        else
        {
            session_player_source = app.session.session_players[app.session_player.id];     
        }            

        let session_player_source_index = app.find_session_player_index(session_player_source.id);
        source_container = house_containers[session_player_source_index];

        app.transfer_good_one_amount = app.random_number(0, session_player_source.good_one_house);
        app.transfer_good_two_amount = app.random_number(0, session_player_source.good_two_house);

        if(app.session.parameter_set.good_count==3)
        {
            app.transfer_good_three_amount = app.random_number(0, session_player_source.good_three_house);
        }

        if(app.transfer_good_one_amount == 0 && app.transfer_good_two_amount == 0)
        {
            return;
        }
    }

    let session_player_target = null;
    
    if(app.session.current_experiment_phase == "Instructions")
    {
        session_player_target = app.session.session_players[app.session_player.id];   
    }
    else
    {
        let session_player_id = app.session.session_players_order[app.random_number(0, app.session.session_players_order.length-1)];
        session_player_target = app.session.session_players[session_player_id]; 
    }

    let session_player_target_index = app.find_session_player_index(session_player_target.id);
    let target_container = house_containers[session_player_target_index];

    app.handle_container_down(source_container,
                                {data: {global: {x:source_container.x, y:source_container.y}}})
    
    app.handle_container_up(target_container,
                            {data: {global: {x:target_container.x, y:target_container.y}}})
},

/**
 * test mode update production percentages
 */
do_test_mode_production_update: function do_test_mode_production_update(){
    if(app.session.current_period_phase != "Trade") return;

    app.production_slider = app.random_number(-50, 50)
    app.update_production_slider();
},
{%endif%}