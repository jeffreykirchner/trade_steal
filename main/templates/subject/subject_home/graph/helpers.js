/**
 * get the parameter set player from the player id
*/
get_parameter_set_player_from_player_id: function get_parameter_set_player_from_player_id(player_id)
{
    try 
    {
        let session_player = app.findSessionPlayer(player_id);
    
        return app.session.parameter_set.parameter_set_players[session_player.parameter_set_player_id];
    }
    catch (error) {
        return {id_label:null};
    }
},

 /**
  * return session player that has specified id
  */
 findSessionPlayer: function findSessionPlayer(id){

    // let session_players = this.session.session_players;
    // for(let i=0; i<session_players.length; i++)
    // {
    //     if(session_players[i].id == id)
    //     {
    //         return session_players[i];
    //     }
    // }

    if(id in app.session.session_players)
    {
        return app.session.session_players[id];
    }

    return null;
 },

/**
 * return session player index that has specified id
 */
findSessionPlayerIndex: function findSessionPlayerIndex(id){

    let session_players = app.session.session_players;
    for(let i=0; i<session_players.length; i++)
    {
        if(session_players[i].id == id)
        {
            return i;
        }
    }

    return null;
},
