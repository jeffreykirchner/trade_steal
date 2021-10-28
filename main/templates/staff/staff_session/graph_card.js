
{% load static %}
/**
 * update the pixi players with new info
 */
updatePixiPlayers(){
   
},

/**
 * setup pixi players
 */
setupPixiPlayers(){

    PIXI.utils.destroyTextureCache();

    session_players = app.$data.session.session_players;

    for(let i=0;i<session_players.length;i++)
    {
        pt = app.getLocationCordinates(session_players[i].parameter_set_player.location);

        session_players[i].sprite = PIXI.Sprite.from('{% static 'houseYou.bmp'%}');

        session_players[i].sprite.x = pt.x;
        session_players[i].sprite.y = pt.y;

        app.$data.pixi_app.stage.addChild(session_players[i].sprite);
    }
    
},

getLocationCordinates(index){

    let x=0;
    let y=20;

    if(index<=4)
    {
        x = 20;
        y += index * 100;
    }
    else
    {
        x = 400;
        y += (index-4) * 100;
    }    
    
    return {x:x, y:y-100};
},