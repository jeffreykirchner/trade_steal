
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

    app.$data.grid_x = 11;
    app.$data.grid_y = 5;

    app.$data.canvas_scale_height = app.$data.canvas_height / app.$data.grid_y;
    app.$data.canvas_scale_width = app.$data.canvas_width / app.$data.grid_x;
    app.$data.canvas_scale = app.$data.canvas_scale_height /  app.$data.house_sprite.height;

    app.$data.pixi_loaded = true;
    app.setupPixiPlayers();

    //layout for testing
    app.setupGrid();
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
        let houseContainer = new PIXI.Container();

        pt = app.getLocationCordinates(session_players[i].parameter_set_player.location);

        //house texture
        let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["House0000"]);

        sprite.x = 0;
        sprite.y = 0;
        sprite.tint = 0xD3D3D3;

        houseContainer.addChild(sprite)

        //house label texture
        let houseLabel = new PIXI.Text(session_players[i].parameter_set_player.id_label,{fontFamily : 'Arial',
                                                                                         fontWeight:'bold',
                                                                                         fontSize: 48,
                                                                                         align : 'center'});
        houseLabel.anchor.set(0.5);
        houseLabel.x = sprite.width / 2;
        houseLabel.y = 50;

        houseContainer.addChild(houseLabel)

        houseContainer.x = pt.x;
        houseContainer.y = pt.y;
        houseContainer.pivot.set(houseContainer.width/2, houseContainer.height/2);
        houseContainer.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);
    
        session_players[i].houseContainer = houseContainer;
        app.$data.pixi_app.stage.addChild(session_players[i].houseContainer);

    }
    
},

/**
 * location grid for layout
 */
setupGrid(){
    x = app.$data.canvas_scale_width;
    y = app.$data.canvas_scale_height;

    for(let i=0;i<app.$data.grid_x-1; i++)
    {
        for(let i=0;i<app.$data.grid_y-1; i++)
        {
            const gr  = new PIXI.Graphics();
            gr.beginFill(0x000000);
            gr.drawCircle(x, y, 6);
            gr.endFill();
            gr.pivot.set(3,3);
            
            app.$data.pixi_app.stage.addChild(gr);

            y+=app.$data.canvas_scale_height;
        }

        x += app.$data.canvas_scale_width;
        y = app.$data.canvas_scale_height;

    }

   
},

destroyPixiPlayers(){
    for(let i=0;i<session_players.length;i++)
    {
        session_players[i].houseContainer.destroy();
    }
},

getLocationCordinates(index){

    let y=0;
    let x=0;

    if(index<=4)
    {
        x = app.$data.canvas_scale_width*5;
        y += index * (app.$data.canvas_scale_height);
    }
    else
    {
        x = app.$data.canvas_scale_width*6;
        y += (index-4) * (app.$data.canvas_scale_height);
    }    

    return {x:x, y:y};
},