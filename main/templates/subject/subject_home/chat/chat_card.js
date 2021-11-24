sendChat(){
    
    app.$data.working = true;
    app.sendMessage("chat", {"recipients" : app.$data.chat_recipients,
                             "text" : app.$data.chat_text,
                            });
},

/** take result of moving goods
*/
takeChat(messageData){
    //app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeUpdateGoods(messageData);       
                 
    } 
    else
    {
        
    }
},

/** take updated data from goods being moved by another player
*    @param messageData {json} session day in json format
*/
takeUpdateChat(messageData){
    app.takeUpdateGoods(messageData);
},

/** update who should receive chat
*    @param messageData {json} session day in json format
*/
updateChatRecipients(chat_recipients, chat_button_label){
    app.$data.chat_recipients = chat_recipients;
    app.$data.chat_button_label = chat_button_label;
},