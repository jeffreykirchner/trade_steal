{%if session.parameter_set.test_mode%}

/**
 * do random self test actions
 */
randomNumber: function randomNumber(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
},

randomString: function randomString(min_length, max_length){

    s = "";
    r = app.randomNumber(min_length, max_length);

    for(let i=0;i<r;i++)
    {
        v = app.randomNumber(48, 122);
        s += String.fromCharCode(v);
    }

    return s;
},

doTestMode: function doTestMode(){
    {%if DEBUG%}
    console.log("Do Test Mode");
    {%endif%}

    if(worker) worker.terminate();

    if(app.end_game_modal_visible)
    {
        if(app.session_player.name == "")
        {
            document.getElementById("id_name").value =  app.randomString(5, 20);
            document.getElementById("id_student_id").value =  app.randomNumber(1000, 10000);

            app.sendName();
        }

        return;
    }

    if(app.session.started && app.test_mode)
    {
        switch (app.session.current_experiment_phase)
        {
            case "Selection":
                app.doTestModeSelection();
                break;
            case "Instructions":
                app.doTestModeInstructions();
                break;
            case "Run":
                app.doTestModeRun();
                break;
            
        }        
       
    }

    // setTimeout(app.doTestMode, app.randomNumber(1000 , 1500));
    worker = new Worker("/static/js/worker_test_mode.js");

    worker.onmessage = function (evt) {   
        app.doTestMode();
    };

    worker.postMessage(0);
},

/**
 * test during selection phase
 */
 doTestModeSelection: function doTestModeSelection()
 {

    if(app.avatar_choice_grid_selected_row == 0 && app.avatar_choice_grid_selected_col == 0)
    {
        let r = app.randomNumber(1, app.session.parameter_set.avatar_grid_row_count);
        let c = app.randomNumber(1, app.session.parameter_set.avatar_grid_col_count);

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
 doTestModeInstructions: function doTestModeInstructions()
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
                    app.doTestModeMove();
                }
                break;
            case app.instructions.action_page_chat:
                if(app.chat_text != "")
                {
                    document.getElementById("send_chat_id").click();                   
                }
                else
                {
                    app.doTestModeChat();
                }
                break;
        }
    }

    
 },

/**
 * test during run phase
 */
doTestModeRun: function doTestModeRun()
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

            app.sendProdution();
            go=false;
        }
    
    if(app.session.finished) return;
        
    if(go)
        switch (app.randomNumber(1, 3)){
            case 1:
                app.doTestModeChat();
                break;
            
            case 2:
                app.doTestModeMove();
                break;
            
            case 3:
                app.doTestModeProductionUpdate();
                break;
        }
},

/**
 * test mode chat
 */
doTestModeChat: function doTestModeChat(){

    let session_player_id = app.session.session_players_order[app.randomNumber(0, app.session.session_players_order.length-1)];
    let session_player_local = app.session.session_players[session_player_id];

    if(session_player_local.id == app.session_player.id)
    {
        if(app.session.parameter_set.group_chat=='True')
        {
            document.getElementById("chat_all_id").click();
            app.chat_text = app.randomString(5, 20);
        }
    }
    else
    {
        if(app.session.parameter_set.private_chat=='True')
        {
            document.getElementById('chat_invididual_' + session_player_local.id + '_id').click();
            app.chat_text = app.randomString(5, 20);
        }
    }

    
},

/**
 * test mode move
 */
doTestModeMove: function doTestModeMove(){
    if(app.session.current_period_phase != "Trade")
    {
        app.close_move_modal();
        return;
    }

    let session_player_source = null;
    let source_container = null;

    if(app.randomNumber(1, 2) == 1 || app.session.current_experiment_phase == "Instructions")
    {
        if(app.session.parameter_set.allow_stealing == "True" && app.session.current_experiment_phase != "Instructions")
        {
            let session_player_id = app.session.session_players_order[app.randomNumber(0, app.session.session_players_order.length-1)];
            session_player_source = app.session.session_players[session_player_id];        }
        else
        {
            session_player_source = app.session.session_players[app.session_player.id];            
        }

        let session_player_source_index = app.find_session_player_index(session_player_source.id);
        source_container = field_containers[session_player_source_index];        

        app.transfer_good_one_amount = app.randomNumber(0, session_player_source.good_one_field);
        app.transfer_good_two_amount = app.randomNumber(0, session_player_source.good_two_field);

        if(app.transfer_good_one_amount == 0 && app.transfer_good_two_amount == 0)
        {
            return;
        }
    }
    else
    {
        if(app.session.parameter_set.allow_stealing == "True")
        {
            let session_player_id = app.session.session_players_order[app.randomNumber(0, app.session.session_players_order.length-1)];
            session_player_source = app.session.session_players[session_player_id];  
        }
        else
        {
            session_player_source = app.session.session_players[app.session_player.id];     
        }            

        let session_player_source_index = app.find_session_player_index(session_player_source.id);
        source_container = house_containers[session_player_source_index];

        app.transfer_good_one_amount = app.randomNumber(0, session_player_source.good_one_house);
        app.transfer_good_two_amount = app.randomNumber(0, session_player_source.good_two_house);

        if(app.session.parameter_set.good_count==3)
        {
            app.transfer_good_three_amount = app.randomNumber(0, session_player_source.good_three_house);
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
        let session_player_id = app.session.session_players_order[app.randomNumber(0, app.session.session_players_order.length-1)];
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
doTestModeProductionUpdate: function doTestModeProductionUpdate(){
    if(app.session.current_period_phase != "Trade") return;

    app.production_slider = app.randomNumber(-50, 50)
    app.update_production_slider();
},
{%endif%}