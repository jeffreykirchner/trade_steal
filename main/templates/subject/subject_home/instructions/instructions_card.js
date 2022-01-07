
/**
 * Given the page number return the requested instruction text
 * @param pageNumber : int
 */
getInstructionPage(pageNumber){

    for(i=0;i<this.instruction_pages.length;i++)
    {
        if(this.instruction_pages[i].page_number==pageNumber)
        {
            return this.instruction_pages[i].text_html;
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
        case 1:
            
            break; 
        case 2:
            return;
            break;
        case 3:
            
            if(this.session_player.current_instruction_complete < this.session_player.current_instruction)
            {
                this.session.current_period_phase = 'Trade';
                if(this.pixi_loaded) this.simulate_clear_goods_instructions();
            }
            
            return;
            break;
        case 4:
            return;
            break; 
        case 5:
           
            break;
        case 6:
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
    
},

/**
 * simulate production on page 2
 */
simulateProductionInstructions(){
    if(this.session.current_experiment_phase != 'Instructions') return;
    if(this.session_player.current_instruction != 2) return;

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
    if(this.session_player.current_instruction != 2) return;

    let parameter_set_type = this.session_player.parameter_set_player.parameter_set_type;

    good_one_field = this.simulate_do_period_production_function(parameter_set_type.good_one_production_1,
                                                            parameter_set_type.good_one_production_2,
                                                            parameter_set_type.good_one_production_3,
                                                            this.production_slider_one);

    good_two_field = this.simulate_do_period_production_function(parameter_set_type.good_two_production_1,
                                                            parameter_set_type.good_two_production_2,
                                                            parameter_set_type.good_two_production_3,
                                                            this.production_slider_two);
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
        if(this.session_player.current_instruction == 2)
        {
            this.session_player.current_instruction_complete=2;
            this.working = false;
        }
    }

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
            id : session_players[0].id,

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
    if(this.session_player.current_instruction == 3)
    {
        this.session_player.current_instruction_complete=3;
    }

    this.closeMoveModal();
},

/**
 * simulate goods transfer on page 4
 */
 simulateChatInstructions(){
    if(this.session_player.current_instruction == 4)
    {
        this.session_player.current_instruction_complete=4;
    }

    this.chat_text="";
},
