sendChat(){

    if(app.$data.working) return;
    if(app.$data.chat_text.trim() == "") return;
    if(app.$data.chat_text.trim().length > 200) return;
    
    app.$data.working = true;
    app.sendMessage("chat", {"recipients" : app.$data.chat_recipients,
                             "text" : app.$data.chat_text.trim(),
                            });
    app.$data.chat_text="";                   
},

/** take result of moving goods
*/
takeChat(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    if(messageData.status.value == "success")
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
takeUpdateChat(messageData){
    
    let result = messageData.status.result;
    let chat = result.chat;
    let session_player = app.$data.session_player;

    if(result.chat_type=="All")
    {
        session_player.chat_all.push(chat);
    }
    else
    {
        let sesson_player_target =  result.sesson_player_target;
        let session_players = app.$data.session.session_players;

        let target = -1;
        if(sesson_player_target == session_player.id)
        {
            target = result.sender_id;
        }
        else
        {
            target = sesson_player_target;
        }

        for(let i=0; i<session_players.length; i++)
        {
            if(session_players[i].id == target)
            {
                session_players[i].chat_individual.push(chat);
                break;
            }
        }        
    }

    app.updateChatDisplay();
},

/** update who should receive chat
*    @param messageData {json} session day in json format
*/
updateChatRecipients(chat_recipients, chat_button_label, chat_recipients_index){
    app.$data.chat_recipients = chat_recipients;
    app.$data.chat_button_label = chat_button_label;
    app.$data.chat_recipients_index = chat_recipients_index;

    app.updateChatDisplay();
},

/** update chat displayed on the screen
 */
updateChatDisplay(){

    if(app.$data.chat_recipients=="all")
    {
        app.$data.chat_list_to_display=Array.from(app.$data.session_player.chat_all);
    }
    else
    {
        app.$data.chat_list_to_display=Array.from(app.$data.session.session_players[app.$data.chat_recipients_index].chat_individual);
    }

    //add spacers
    for(let i=app.$data.chat_list_to_display.length;i<18;i++)
    {
        app.$data.chat_list_to_display.unshift({id:i*-1, text:"|", sender_id:app.$data.session_player.id})
    }

    //scroll to view
    if(app.$data.chat_list_to_display.length>0)
    {
        //setTimeout(app.updateChatDisplayScroll, 250);

        Vue.nextTick(() => {app.updateChatDisplayScroll()});        
    }
},

updateChatDisplayScroll(){
    var elmnt = document.getElementById("chat_id_" + app.$data.chat_list_to_display[app.$data.chat_list_to_display.length-1].id.toString());
    elmnt.scrollIntoView(); 
},

