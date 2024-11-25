/**
 * get the parameter set player from the player id
*/
get_parameter_set_player_from_player_id: function get_parameter_set_player_from_player_id(player_id)
{
    try 
    {
        let session_player = app.find_session_player(player_id);
    
        return app.session.parameter_set.parameter_set_players[session_player.parameter_set_player_id];
    }
    catch (error) {
        return {id_label:null};
    }
},

 /**
  * return session player that has specified id
  */
 find_session_player: function find_session_player(id){

    if(id in app.session.session_players)
    {
        return app.session.session_players[id];
    }

    return null;
 },

/**
 * return session player index that has specified id
 */
find_session_player_index: function find_session_player_index(id){

    
    for(let i=0; i<app.session.session_players_order.length; i++)
    {
        let session_player_id = app.session.session_players_order[i];
        if(app.session.session_players[session_player_id].id == id)
        {
            return i;
        }
    }

    return null;
},
