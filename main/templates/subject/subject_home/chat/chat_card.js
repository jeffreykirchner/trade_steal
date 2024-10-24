sendChat: function sendChat(){

    if(this.working) return;
    if(this.chat_text.trim() == "") return;
    if(this.chat_text.trim().length > 200) return;
    if(this.chat_recipients=="NONE") return;
    
    this.working = true;
    app.sendMessage("chat", {"recipients" : this.chat_recipients,
                             "text" : this.chat_text.trim(),
                            });

    this.chat_text="";                   
},

/** take result of moving goods
*/
takeChat: function takeChat(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    if(messageData.value == "success")
    {
        app.takeUpdateChat(messageData);                        
    } 
    else
    {
        
    }
},

/** take updated data from goods being moved by another player
*    @param messageData {json} session day in json format
*/
takeUpdateChat: function takeUpdateChat(messageData){
    
    let result = messageData;
    let chat = result.chat;
    let session_player = this.session_player;

    // if(app.chat_recipients=="NONE") return;

    if(result.chat_type=="All")
    {
        if(session_player.chat_all.length >= 100)
            session_player.chat_all.shift();

        session_player.chat_all.push(chat);
        if(this.chat_recipients != "all")
        {
            session_player.new_chat_message = true;
        }
    }
    else if(result.chat_type=="Individual")
    {
        var sesson_player_target =  result.sesson_player_target;
        var session_players = this.session.session_players;

        var target = -1;
        if(sesson_player_target == session_player.id)
        {
            target = result.chat.sender_id;
        }
        else
        {
            target = sesson_player_target;
        }

        session_player = app.findSessionPlayer(target);
        session_player_index = app.findSessionPlayerIndex(target);

        if(session_player)
        {
            if(session_player.chat_individual.length >= 100)
               session_player.chat_individual.shift();

            session_player.chat_individual.push(chat);

            if(session_player_index != this.chat_recipients_index)
            {
                session_player.new_chat_message = true;
            }
        }

        // for(let i=0; i<session_players.length; i++)
        // {
        //     if(session_players[i].id == target)
        //     {
                
                
        //         break;
        //     }
        // }        
    }

    app.updateChatDisplay();
},

/** update who should receive chat
*    @param messageData {json} session day in json format
*/
updateChatRecipients: function updateChatRecipients(chat_recipients, chat_recipients_index){

    this.chat_recipients = chat_recipients;
    
    this.chat_recipients_index = chat_recipients_index;

    app.updateChatDisplay();

    if(this.chat_recipients=="all")
    {
        this.chat_button_label = "Everyone";
        this.session_player.new_chat_message = false;
    }
    else
    {
        let parameter_set_player = app.get_parameter_set_player_from_player_id(chat_recipients);
        this.chat_button_label = "Person " + parameter_set_player.id_label;
        this.session.session_players[chat_recipients_index].new_chat_message = false;
    }
},

/** update chat displayed on the screen
 */
updateChatDisplay: function updateChatDisplay(){

    if(app.chat_recipients=="NONE") return;

    if(this.chat_recipients=="all")
    {
        this.chat_list_to_display=Array.from(this.session_player.chat_all);
    }
    else
    {
        this.chat_list_to_display=Array.from(this.session.session_players[this.chat_recipients_index].chat_individual);
    }

    //add spacers
    // for(let i=this.chat_list_to_display.length;i<12;i++)
    // {
    //     this.chat_list_to_display.unshift({id:i*-1, text:"|", sender_id:this.session_player.id})
    // }

    // //scroll to view
    // if(this.chat_list_to_display.length>0)
    // {
    //     Vue.nextTick(() => {app.updateChatDisplayScroll()});        
    // }
},

updateChatDisplayScroll: function updateChatDisplayScroll(){
    // var elmnt = document.getElementById("chat_id_" + this.chat_list_to_display[this.chat_list_to_display.length-1].id.toString());
    // elmnt.scrollIntoView(); 
},

