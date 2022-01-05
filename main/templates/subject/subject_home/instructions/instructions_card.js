
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

},
