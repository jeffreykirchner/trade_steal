sendChat: function sendChat(){

    if(app.working) return;
    if(app.chat_text.trim() == "") return;
    if(app.chat_text.trim().length > 200) return;
    if(app.chat_recipients=="NONE")
    {
        app.chat_error_message = "Please select a recipient.";
        return;
    }

    app.chat_error_message = "";
    app.working = true;

    app.send_message("chat", 
                    {"recipients" : app.chat_recipients, "text" : app.chat_text.trim(),},
                    "group");

    app.chat_text="";                   
},

/** take result of moving goods
*/
takeChat: function takeChat(message_data){
    //app.cancelModal=false;
    //app.clear_main_form_errors();

    if(message_data.value == "success")
    {
        app.take_update_chat(message_data);                        
    } 
    else
    {
        
    }
},

/** take updated data from goods being moved by another player
*    @param message_data {json} session day in json format
*/
take_update_chat: function take_update_chat(message_data){
    
    let result = message_data;
    let chat = result.chat;
    let session_player = app.session_player;

    // if(app.chat_recipients=="NONE") return;
    if(result.status == "success")
    {
        if(result.chat_type=="All")
        {
            if(session_player.chat_all.length >= 100)
                session_player.chat_all.shift();

            session_player.chat_all.push(chat);
            if(app.chat_recipients != "all")
            {
                session_player.new_chat_message = true;
            }
        }
        else if(result.chat_type=="Individual")
        {
            var sesson_player_target =  result.sesson_player_target;

            var target = -1;
            if(sesson_player_target == session_player.id)
            {
                target = result.chat.sender_id;
            }
            else
            {
                target = sesson_player_target;
            }

            session_player = app.session.session_players[target];
            session_player_index = app.findSessionPlayerIndex(target);

            if(session_player)
            {
                if(session_player.chat_individual.length >= 100)
                session_player.chat_individual.shift();

                session_player.chat_individual.push(chat);

                if(session_player_index != app.chat_recipients_index)
                {
                    session_player.new_chat_message = true;
                }
            }       
        }
    }

    if(parseInt(message_data.session_player_id) == app.session_player.id)
    { 
        app.working = false;           
    }
    
    app.update_chat_display();
},

/** update who should receive chat
*    @param message_data {json} session day in json format
*/
updateChatRecipients: function updateChatRecipients(chat_recipients, chat_recipients_index){

    app.chat_recipients = chat_recipients;
    
    app.chat_recipients_index = chat_recipients_index;

    app.update_chat_display();

    if(app.chat_recipients=="all")
    {
        app.chat_button_label = "Everyone";
        app.session_player.new_chat_message = false;
    }
    else
    {
        let parameter_set_player = app.get_parameter_set_player_from_player_id(chat_recipients);
        app.chat_button_label = "Person " + parameter_set_player.id_label;
        let session_player_id = app.session.session_players_order[chat_recipients_index];
        let session_player = app.session.session_players[session_player_id];
        session_player.new_chat_message = false;
    }
},

/** update chat displayed on the screen
 */
update_chat_display: function update_chat_display(){

    if(app.chat_recipients=="NONE") return;

    if(app.chat_recipients=="all")
    {
        app.chat_list_to_display=Array.from(app.session_player.chat_all);
    }
    else
    {
        let session_player_id = app.session.session_players_order[app.chat_recipients_index];
        let session_player = app.session.session_players[session_player_id];
        app.chat_list_to_display=Array.from(session_player.chat_individual);
    }

},

update_chat_displayScroll: function update_chat_displayScroll(){
    // var elmnt = document.getElementById("chat_id_" + app.chat_list_to_display[app.chat_list_to_display.length-1].id.toString());
    // elmnt.scrollIntoView(); 
},

