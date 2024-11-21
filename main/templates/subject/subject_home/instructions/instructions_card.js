
/**
 * Given the page number return the requested instruction text
 * @param pageNumber : int
 */
getInstructionPage: function getInstructionPage(pageNumber){

    for(i=0;i<app.instructions.instruction_pages.length;i++)
    {
        if(app.instructions.instruction_pages[i].page_number==pageNumber)
        {
            return app.instructions.instruction_pages[i].text_html;
        }
    }

    return "Text not found";
},

/**
 * advance to next instruction page
 */
sendNextInstruction: function sendNextInstruction(direction){

    if(app.working) return;
    
    app.working = true;
    app.send_message("next_instruction", {"direction" : direction});
},

/**
 * advance to next instruction page
 */
take_next_instruction: function take_next_instruction(message_data){
    if(message_data.value == "success")
    {
        result = message_data.result;       
        
        app.session_player.current_instruction = result.current_instruction;
        app.session_player.current_instruction_complete = result.current_instruction_complete;

        app.processInstructionPage();
        app.instructionDisplayScroll();
    } 
    else
    {
        
    }

    app.working = false;
    
},

/**
 * finish instructions
 */
sendFinishInstructions: function sendFinishInstructions(){

    if(app.working) return;
    
    app.working = true;
    app.send_message("finish_instructions", {});
},

/**
 * finish instructions
 */
takeFinishInstructions: function takeFinishInstructions(message_data){
    if(message_data.value == "success")
    {
        result = message_data.result;       
        
        app.session_player.instructions_finished = result.instructions_finished;
        app.session_player.current_instruction_complete = result.current_instruction_complete;
    } 
    else
    {
        
    }

    app.working = false;
    app.closeMoveModal();
},

/**
 * process instruction page
 */
processInstructionPage: function processInstructionPage(){

    switch(app.session_player.current_instruction){
        case app.instructions.action_page_production:
            return;
            break; 
        case app.instructions.action_page_move:
            if(app.session_player.current_instruction_complete < app.session_player.current_instruction)
            {
                app.session.current_period_phase = 'Trade';
                app.setup_page_3_instructions();
            }
            return;
            break;
        case app.instructions.action_page_chat:
            return;
            break;
            
    }

    if(app.session_player.current_instruction_complete < app.session_player.current_instruction)
        {
            app.session_player.current_instruction_complete = app.session_player.current_instruction;
        }

        
},

/**
 * scroll instruction into view
 */
instructionDisplayScroll: function instructionDisplayScroll(){
    
    document.getElementById("instructions_frame").scrollIntoView();

    Vue.nextTick(() => {
        if(document.getElementById("instructions_frame"))
        {  
           document.getElementById("instructions_frame").scrollIntoView();
           app.scroll_update();
        }
     })
    
},

/**
 * simulate production on page 2
 */
simulateProductionInstructions: function simulateProductionInstructions(){
    if(app.session.current_experiment_phase != 'Instructions') return;
    if(app.session_player.current_instruction != app.instructions.action_page_production) return;

    document.getElementById("graph_card").scrollIntoView();

    app.working = true;
    app.session.time_remaining = app.session.parameter_set.period_length_production;
    
    app.simulate_clear_goods_instructions();

    if(app.productionSimulationTimeout) clearTimeout(app.productionSimulationTimeout);
    app.productionSimulationTimeout = setTimeout(app.simulate_do_period_production, 1000);
},

/**
 * simulate_do_period_production
 */
simulate_do_period_production: function simulate_do_period_production(){

    if(app.session.current_experiment_phase != 'Instructions') return;
    if(app.session_player.current_instruction !=  app.instructions.action_page_production) return;

    let parameter_set_player_local = app.get_parameter_set_player_from_player_id(app.session_player.id);

    let parameter_set_type = parameter_set_player_local.parameter_set_type;

    good_one_field = app.simulate_do_period_production_function(parameter_set_type.good_one_production_1,
                                                            parameter_set_type.good_one_production_2,
                                                            parameter_set_type.good_one_production_3,
                                                            app.session_player.good_one_production_rate);

    good_two_field = app.simulate_do_period_production_function(parameter_set_type.good_two_production_1,
                                                            parameter_set_type.good_two_production_2,
                                                            parameter_set_type.good_two_production_3,
                                                            app.session_player.good_two_production_rate);
    let result = [];

    result.push({
        id : app.session_player.id,

        good_one_house : 0,
        good_two_house : 0,
        good_three_house : 0,

        good_one_field : good_one_field + app.session_player.good_one_field,
        good_two_field : good_two_field + app.session_player.good_two_field,

        notice : null,
    })
    
    app.take_update_goods({result : result});

    app.session.time_remaining -= 1;

    if(app.session.time_remaining > 0){
         app.productionSimulationTimeout = setTimeout(app.simulate_do_period_production, 1000);
    }
    else
    {
        if(app.session_player.current_instruction == app.instructions.action_page_production)
        {
            app.session_player.current_instruction_complete=app.instructions.action_page_production;
            app.working = false;
        }
    }

},

/**
 * setup page 3 instructions
 */
setup_page_3_instructions: function setup_page_3_instructions(){

    app.simulate_clear_goods_instructions();

    let result = [];

    result.push({
        id : app.session_player.id,

        good_one_house : 0,
        good_two_house : 0,
        good_three_house : 0,

        good_one_field : 10,
        good_two_field :10,

        notice : null,
    })
    
    app.take_update_goods({result : result});
},

/**
 * reset all goods to zero during instructions
 */
simulate_clear_goods_instructions: function simulate_clear_goods_instructions(){

    // let session_players = app.session.session_players;
    let result = [];

    for(i=0; i<app.session.session_players_order.length;i++)
    {
        let session_player_id = app.session.session_players_order[i];

        result.push({
            id : app.session.session_players[session_player_id].id,

            good_one_house : 0,
            good_two_house : 0,
            good_three_house : 0,

            good_one_field : 0,
            good_two_field : 0,

            notice : null,
        })
    }

    app.take_update_goods({result : result});
},

/**
 * simulate_do_period_production_function
 */
simulate_do_period_production_function: function simulate_do_period_production_function(good_production_1, good_production_2, good_production_3, production_rate){

    let total_time = app.session.parameter_set.period_length_production;

    let good_time =  total_time * parseFloat(production_rate)/parseFloat('100');
    let production = parseFloat(good_production_1) + parseFloat(good_production_2) * good_time ** parseFloat(good_production_3);
    production *= (parseFloat('1')/total_time);

    return production;
},
/**
 * simulate goods transfer on page 3
 */
simulateGoodTransferInstructions: function simulateGoodTransferInstructions(){
    app.clearMainFormErrors();

    if(pixi_transfer_source.name.type.toString() != "field" ||
       pixi_transfer_target.name.type.toString() != "house" ||
       pixi_transfer_source.name.user_id != app.session_player.id ||
       pixi_transfer_target.name.user_id != app.session_player.id) 
    {
        let errors = {transfer_good_one_amount_2g:["For the purposes of the instructions, please transfer items from your field to your house."]};
        app.displayErrors(errors);
        return;
    }

    let form_data = {transfer_good_one_amount_2g: app.transfer_good_one_amount,
                     transfer_good_two_amount_2g: app.transfer_good_two_amount};

    let transfer_good_one_amount_2g = Number(app.transfer_good_one_amount);
    let transfer_good_two_amount_2g = Number(app.transfer_good_two_amount);

    if(transfer_good_one_amount_2g == 0 && transfer_good_two_amount_2g == 0)
    {

        let errors = {transfer_good_one_amount_2g:["Invalid entry."],};
        app.displayErrors(errors);
        return;
    }

    if(!Number.isInteger(transfer_good_one_amount_2g) || 
        parseInt(transfer_good_one_amount_2g) < 0)
    {
        let errors = {transfer_good_one_amount_2g:["Invalid entry."]};
        app.displayErrors(errors);
        return;
    }

    if(!Number.isInteger(transfer_good_two_amount_2g) || 
        parseInt(transfer_good_two_amount_2g) < 0)
    {
        let errors = {transfer_good_two_amount_2g:["Invalid entry."]};
        app.displayErrors(errors);
        return;
    }

    if(parseInt(transfer_good_one_amount_2g) > app.session_player.good_one_field)
    {
        let errors = {transfer_good_one_amount_2g:["There are not enough goods on your field."]};
        app.displayErrors(errors);
        return;
    }

    if(parseInt(transfer_good_two_amount_2g) > app.session_player.good_two_field)
    {
        let errors = {transfer_good_two_amount_2g:["There are not enough goods on your field."]};
        app.displayErrors(errors);
        return;
    }

    let result = [];

    result.push({
        id : app.session_player.id,

        good_one_house : app.session_player.good_one_house + parseInt(transfer_good_one_amount_2g),
        good_two_house : app.session_player.good_two_house + parseInt(transfer_good_two_amount_2g),
        good_three_house : 0,

        good_one_field : app.session_player.good_one_field - parseInt(transfer_good_one_amount_2g),
        good_two_field : app.session_player.good_two_field - parseInt(transfer_good_two_amount_2g),

        notice : null,
    });
    
    app.take_update_goods({result : result});

    if(app.session_player.current_instruction == app.instructions.action_page_move)
    {
        app.session_player.current_instruction_complete=app.instructions.action_page_move;
    }

    app.closeMoveModal();
},

/**
 * simulate goods transfer on page 4
 */
 simulateChatInstructions: function simulateChatInstructions(){
    if(app.session_player.current_instruction != app.instructions.action_page_chat) return;

    if(app.chat_text.trim() == "") return;
    if(app.chat_text.trim().length > 200) return;

    if(app.chat_recipients == "NONE") return;

    let parameter_set_player_local = app.get_parameter_set_player_from_player_id(app.session_player.id);

    if(app.chat_recipients == "all")
    {
        chat_type = "All";

        message_data = {chat: {text : app.chat_text.trim(),
                              sender_label : parameter_set_player_local.id_label,
                              sender_id : app.session_player.id,
                              id : randomNumber(1, 1000000)},
                      chat_type:chat_type,
                      status:"success"}
    }
    else
    {
        chat_type = "Individual";

        message_data = {chat: {text : app.chat_text.trim(),
                                     sender_label : parameter_set_player_local.id_label,
                                     sender_id : app.session_player.id,
                                     id : randomNumber(1, 1000000)},
                       sesson_player_target : app.chat_recipients,        
                       chat_type:chat_type,
                       status:"success"}
    }

    app.take_update_chat(message_data);

    if(app.session_player.current_instruction == app.instructions.action_page_chat)
    {
        app.session_player.current_instruction_complete= app.instructions.action_page_chat;
    }

    app.chat_text="";
},

scroll_update: function scroll_update()
{
    var scrollTop = document.getElementById('instructions_frame_a').scrollTop;
    var scrollHeight = document.getElementById('instructions_frame_a').scrollHeight; // added
    var offsetHeight = document.getElementById('instructions_frame_a').offsetHeight;
    // var clientHeight = document.getElementById('box').clientHeight;
    var contentHeight = scrollHeight - offsetHeight; // added
    if (contentHeight <= scrollTop) // modified
    {
        // Now this is called when scroll end!
        app.instruction_pages_show_scroll = false;
    }
    else
    {
        app.instruction_pages_show_scroll = true;
    }
},