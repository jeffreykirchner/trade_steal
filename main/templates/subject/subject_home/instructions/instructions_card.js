
/**
 * Given the page number return the requested instruction text
 * @param pageNumber : int
 */
getInstructionPage(pageNumber){

    for(i=0;i<this.instructions.instruction_pages.length;i++)
    {
        if(this.instructions.instruction_pages[i].page_number==pageNumber)
        {
            return this.instructions.instruction_pages[i].text_html;
        }
    }

    return "Text not found";
},

/**
 * advance to next instruction page
 */
sendNextInstruction(direction){

    if(this.working) return;
    
    this.working = true;
    this.sendMessage("next_instruction", {"direction" : direction});
},

/**
 * advance to next instruction page
 */
takeNextInstruction(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;       
        
        this.session_player.current_instruction = result.current_instruction;
        this.session_player.current_instruction_complete = result.current_instruction_complete;

        this.processInstructionPage();
        this.instructionDisplayScroll();
    } 
    else
    {
        
    }
    
},

/**
 * finish instructions
 */
sendFinishInstructions(){

    if(this.working) return;
    
    this.working = true;
    this.sendMessage("finish_instructions", {});
},

/**
 * finish instructions
 */
takeFinishInstructions(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;       
        
        this.session_player.instructions_finished = result.instructions_finished;
        this.session_player.current_instruction_complete = result.current_instruction_complete;
    } 
    else
    {
        
    }
},

/**
 * process instruction page
 */
processInstructionPage(){

    switch(this.session_player.current_instruction){
        case this.instructions.action_page_production:
            return;
            break; 
        case this.instructions.action_page_move:
            if(this.session_player.current_instruction_complete < this.session_player.current_instruction)
            {
                this.session.current_period_phase = 'Trade';
                this.setup_page_3_instructions();
            }
            return;
            break;
        case this.instructions.action_page_chat:
            return;
            break;
            
    }

    if(this.session_player.current_instruction_complete < this.session_player.current_instruction)
        {
            this.session_player.current_instruction_complete = this.session_player.current_instruction;
        }

        
},

/**
 * scroll instruction into view
 */
instructionDisplayScroll(){
    
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
simulateProductionInstructions(){
    if(this.session.current_experiment_phase != 'Instructions') return;
    if(this.session_player.current_instruction != this.instructions.action_page_production) return;

    document.getElementById("graph_card").scrollIntoView();

    this.working = true;
    this.session.time_remaining = this.session.parameter_set.period_length_production;
    
    app.simulate_clear_goods_instructions();

    if(this.productionSimulationTimeout) clearTimeout(this.productionSimulationTimeout);
    this.productionSimulationTimeout = setTimeout(this.simulate_do_period_production, 1000);
},

/**
 * simulate_do_period_production
 */
simulate_do_period_production(){

    if(this.session.current_experiment_phase != 'Instructions') return;
    if(this.session_player.current_instruction !=  this.instructions.action_page_production) return;

    let parameter_set_type = this.session_player.parameter_set_player.parameter_set_type;

    good_one_field = this.simulate_do_period_production_function(parameter_set_type.good_one_production_1,
                                                            parameter_set_type.good_one_production_2,
                                                            parameter_set_type.good_one_production_3,
                                                            this.session_player.good_one_production_rate);

    good_two_field = this.simulate_do_period_production_function(parameter_set_type.good_two_production_1,
                                                            parameter_set_type.good_two_production_2,
                                                            parameter_set_type.good_two_production_3,
                                                            this.session_player.good_two_production_rate);
    let result = [];

    result.push({
        id : this.session_player.id,

        good_one_house : 0,
        good_two_house : 0,
        good_three_house : 0,

        good_one_field : good_one_field + this.session_player.good_one_field,
        good_two_field : good_two_field + this.session_player.good_two_field,

        notice : null,
    })
    
    app.takeUpdateGoods({status : {result : result}});

    this.session.time_remaining -= 1;

    if(this.session.time_remaining > 0){
         this.productionSimulationTimeout = setTimeout(this.simulate_do_period_production, 1000);
    }
    else
    {
        if(this.session_player.current_instruction == this.instructions.action_page_production)
        {
            this.session_player.current_instruction_complete=this.instructions.action_page_production;
            this.working = false;
        }
    }

},

/**
 * setup page 3 instructions
 */
setup_page_3_instructions(){

    this.simulate_clear_goods_instructions();

    let result = [];

    result.push({
        id : this.session_player.id,

        good_one_house : 0,
        good_two_house : 0,
        good_three_house : 0,

        good_one_field : 10,
        good_two_field :10,

        notice : null,
    })
    
    app.takeUpdateGoods({status : {result : result}});
},

/**
 * reset all goods to zero during instructions
 */
simulate_clear_goods_instructions(){

    let session_players = this.session.session_players;
    let result = [];

    for(i=0; i<session_players.length;i++)
    {
        result.push({
            id : session_players[i].id,

            good_one_house : 0,
            good_two_house : 0,
            good_three_house : 0,

            good_one_field : 0,
            good_two_field : 0,

            notice : null,
        })
    }

    app.takeUpdateGoods({status : {result : result}});
},

/**
 * simulate_do_period_production_function
 */
simulate_do_period_production_function(good_production_1, good_production_2, good_production_3, production_rate){

    let total_time = this.session.parameter_set.period_length_production;

    let good_time =  total_time * parseFloat(production_rate)/parseFloat('100');
    let production = parseFloat(good_production_1) + parseFloat(good_production_2) * good_time ** parseFloat(good_production_3);
    production *= (parseFloat('1')/total_time);

    return production;
},
/**
 * simulate goods transfer on page 3
 */
simulateGoodTransferInstructions(){
    this.clearMainFormErrors();

    if(pixi_transfer_source.name.type.toString() != "field" ||
       pixi_transfer_target.name.type.toString() != "house" ||
       pixi_transfer_source.name.user_id != this.session_player.id ||
       pixi_transfer_target.name.user_id != this.session_player.id) 
    {
        let errors = {transfer_good_one_amount_2g:["For the purposes of the instructions, please transfer items from your field to your house."],
                      transfer_good_one_amount_3g:["For the purposes of the instructions, please transfer items from your field to your house."]};
        this.displayErrors(errors);
        return;
    }

    let form_data = $("#moveTwoGoodsForm").serializeArray();

    let transfer_good_one_amount_2g = Number(this.transfer_good_one_amount);
    let transfer_good_two_amount_2g = Number(this.transfer_good_two_amount);

    if(transfer_good_one_amount_2g == 0 && transfer_good_two_amount_2g == 0)
    {

        let errors = {transfer_good_one_amount_2g:["Invalid Entry."],};
        this.displayErrors(errors);
        return;
    }

    if(!Number.isInteger(transfer_good_one_amount_2g) || 
        parseInt(transfer_good_one_amount_2g) < 0)
    {
        let errors = {transfer_good_one_amount_2g:["Invalid entry."]};
        this.displayErrors(errors);
        return;
    }

    if(!Number.isInteger(transfer_good_two_amount_2g) || 
        parseInt(transfer_good_two_amount_2g) < 0)
    {
        let errors = {transfer_good_two_amount_2g:["Invalid entry."]};
        this.displayErrors(errors);
        return;
    }

    if(parseInt(transfer_good_one_amount_2g) > this.session_player.good_one_field)
    {
        let errors = {transfer_good_one_amount_2g:["There are not enough goods on your field."]};
        this.displayErrors(errors);
        return;
    }

    if(parseInt(transfer_good_two_amount_2g) > this.session_player.good_two_field)
    {
        let errors = {transfer_good_two_amount_2g:["There are not enough goods on your field."]};
        this.displayErrors(errors);
        return;
    }

    let result = [];

    result.push({
        id : this.session_player.id,

        good_one_house : this.session_player.good_one_house + parseInt(transfer_good_one_amount_2g),
        good_two_house : this.session_player.good_two_house + parseInt(transfer_good_two_amount_2g),
        good_three_house : 0,

        good_one_field : this.session_player.good_one_field - parseInt(transfer_good_one_amount_2g),
        good_two_field : this.session_player.good_two_field - parseInt(transfer_good_two_amount_2g),

        notice : null,
    });
    
    app.takeUpdateGoods({status : {result : result}});

    if(this.session_player.current_instruction == this.instructions.action_page_move)
    {
        this.session_player.current_instruction_complete=this.instructions.action_page_move;
    }

    this.closeMoveModal();
},

/**
 * simulate goods transfer on page 4
 */
 simulateChatInstructions(){
    if(this.session_player.current_instruction != this.instructions.action_page_chat) return;

    if(this.chat_text.trim() == "") return;
    if(this.chat_text.trim().length > 200) return;

    if(this.chat_recipients == "NONE") return;

    if(this.chat_recipients == "all")
    {
        chat_type = "All";

        messageData = {status : {chat: {text : this.chat_text.trim(),
                                 sender_label : this.session_player.parameter_set_player.id_label,
                                 sender_id : this.session_player.id,
                                 id : randomNumber(1, 1000000)},
                      chat_type:chat_type}}
    }
    else
    {
        chat_type = "Individual";

        messageData = {status : {chat: {text : this.chat_text.trim(),
                                        sender_label : this.session_player.parameter_set_player.id_label,
                                        sender_id : this.session_player.id,
                                        id : randomNumber(1, 1000000)},
                                 sesson_player_target : this.chat_recipients,        
                                 chat_type:chat_type}}
    }

   

    app.takeUpdateChat(messageData);

    if(this.session_player.current_instruction == this.instructions.action_page_chat)
    {
        this.session_player.current_instruction_complete= this.instructions.action_page_chat;
    }

    this.chat_text="";
},

scroll_update()
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