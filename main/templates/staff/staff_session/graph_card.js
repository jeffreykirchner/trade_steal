
{% load static %}
/**
 * update the pixi players with new info
 */
setupPixi(){
    let canvas = document.getElementById('sd_graph_id');
    //     ctx = canvas.getContext('2d');

    // app.$data.canvas_width = ctx.canvas.width;
    // app.$data.canvas_height = ctx.canvas.height;

    app.$data.pixi_app = new PIXI.Application({resizeTo : canvas,
                                               backgroundColor : 0xFFFFFF,
                                               autoResize: true,
                                               resolution: devicePixelRatio,
                                               view: canvas });

    app.$data.canvas_width = canvas.width;
    app.$data.canvas_height = canvas.height;
    
    PIXI.Loader.shared.add("{% static 'sprite_sheet.json' %}").load(app.setupPixiSheets);
},

setupPixiSheets()
{
    app.$data.house_sheet = PIXI.Loader.shared.resources["{% static 'sprite_sheet.json' %}"].spritesheet;
    app.$data.house_sprite = new PIXI.Sprite(app.$data.house_sheet.textures["House0000"]);

    app.$data.canvas_scale_height = app.$data.canvas_height / 5;
    app.$data.canvas_scale = app.$data.canvas_scale_height /  app.$data.house_sprite.height;

    app.$data.pixi_loaded = true;
    app.setupPixiPlayers();
},

updatePixiPlayers(){
   
},

/**
 * setup pixi players
 */
setupPixiPlayers(){

    if(!app.$data.pixi_loaded) return;

    //PIXI.utils.destroyTextureCache();

    session_players = app.$data.session.session_players;

    //sheet = PIXI.Loader.shared.resources["/static/house.json"].spritesheet;;

    for(let i=0;i<session_players.length;i++)
    {
        pt = app.getLocationCordinates(session_players[i].parameter_set_player.location);

        session_players[i].sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["House0000"]);
        //session_players[i].sprite = app.$data.house_sprite;

        session_players[i].sprite.x = pt.x;
        session_players[i].sprite.y = pt.y;
        session_players[i].sprite.tint = 0xD3D3D3;
        session_players[i].sprite.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);

        app.$data.pixi_app.stage.addChild(session_players[i].sprite);

    }
    
},

getLocationCordinates(index){

    let x=0;
    let y=20;

    if(index<=4)
    {
        x = 20;
        y += index * (app.$data.canvas_scale_height+10);
    }
    else
    {
        x = 400;
        y += (index-4) * (app.$data.canvas_scale_height+10);
    }    
    
    return {x:x, y:y-100};
},