 /**
 * take update player groups
 * @param messageData {json} session day in json format
 */
  takeUpdateConnectionStatus(messageData){
            
    if(messageData.status.value == "success")
    {
        let result = messageData.status.result;
        let session_players = app.$data.session.session_players;

        for(let i=0; i<session_players.length; i++)
        {
            if(session_players[i].id == result.id)
            {
                session_players[i].connected_count = result.connected_count;
            }
        }
    }
},

/**
 * take update player groups
 * @param messageData {json} session day in json format
 */
 takeUpdateGroups(messageData){
    
    if(messageData.status.status == "success")
    {
        let group_list = messageData.status.group_list;
        let session_players = app.$data.session.session_players;

        for(let i=0; i<session_players.length; i++)
        {
            for(let j=0; j<group_list.length; j++)
            {
                if(session_players[i].id == group_list[j].id)
                {
                    session_players[i].group_number = group_list[j].group_number;
                    break;
                }
            }
        }
    }
},