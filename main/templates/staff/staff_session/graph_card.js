
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

    app.$data.grid_y_padding = 30;

    app.$data.canvas_scale_height = app.$data.canvas_height / app.$data.grid_y;
    app.$data.canvas_scale_width = app.$data.canvas_width / app.$data.grid_x;
    app.$data.canvas_scale = app.$data.canvas_scale_height /  app.$data.house_sprite.height;

    app.$data.pixi_loaded = true;
    app.setupPixiPlayers();

    //layout for testing
    //app.setupGrid();
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

    //setup pixi houses
    for(let i=0;i<session_players.length;i++)
    {
        let container = new PIXI.Container();

        pt = app.getLocationCordinates(session_players[i].parameter_set_player.location, 'house');

        session_player = session_players[i];
        parameter_set_player = session_player.parameter_set_player;
        parameter_set = app.$data.session.parameter_set;

        //house texture
        let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["House0000"]);

        sprite.x = 0;
        sprite.y = 0;
        sprite.interactive = true;
        sprite.buttonMode = true;
        sprite.tint = 0xD3D3D3;
        sprite.on('pointerdown', (event) => { app.handleHouseClick(i) });

        container.addChild(sprite)

        //house label texture
        let label = new PIXI.Text(parameter_set_player.id_label,{fontFamily : 'Arial',
                                                                      fontWeight:'bold',
                                                                      fontSize: 48,
                                                                      align : 'center'});
        label.anchor.set(0.5);
        label.x = sprite.width / 2;
        label.y = 50;

        container.addChild(label);

        //good one label
        let goodOneLabel = new PIXI.Text(session_player.good_one_house.toString(),{fontFamily : 'Arial',
                                                                              fontWeight:'bold',
                                                                              fontSize: 100,
                                                                              fill: parameter_set.good_one_rgb_color,
                                                                              align : 'center'});

        goodOneLabel.anchor.set(0.5);
        goodOneLabel.x = sprite.width / 2;
        goodOneLabel.y = 185;

        container.addChild(goodOneLabel)

        //good one label
        let goodTwoLabel = new PIXI.Text(session_player.good_two_house.toString(),{fontFamily : 'Arial',
                                                                                        fontWeight:'bold',
                                                                                        fontSize: 100,
                                                                                        fill: parameter_set.good_two_rgb_color,
                                                                                        align : 'center'});

        goodTwoLabel.anchor.set(0.5);
        goodTwoLabel.x = sprite.width / 2;
        goodTwoLabel.y = 300;

        container.addChild(goodTwoLabel)

        container.x = pt.x;
        container.y = pt.y;
        container.pivot.set(container.width/2, container.height/2);
        container.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);
    
        session_players[i].houseContainer = container;
        app.$data.pixi_app.stage.addChild(session_players[i].houseContainer);

    }

    //setup pixi fields
    for(let i=0;i<session_players.length;i++)
    {
        let container = new PIXI.Container();

        pt = app.getLocationCordinates(session_players[i].parameter_set_player.location, 'field');

        session_player = session_players[i];
        parameter_set_player = session_player.parameter_set_player;
        parameter_set = app.$data.session.parameter_set;

        //house texture
        let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["Field0000"]);

        sprite.x = 0;
        sprite.y = 0;
        sprite.tint = 0xD3D3D3;
        sprite.interactive = true;
        sprite.buttonMode = true;
        sprite.on('pointerdown', (event) => { app.handleFieldClick(i) });

        container.addChild(sprite)

        //house label texture
        let label = new PIXI.Text(parameter_set_player.id_label,{fontFamily : 'Arial',
                                                                      fontWeight:'bold',
                                                                      fontSize: 48,
                                                                      align : 'center'});
        label.anchor.set(0.5);
        label.x = sprite.width - 25;
        label.y = 35;

        container.addChild(label);

        //good one label
        let goodOneLabel = new PIXI.Text(session_player.good_one_field.toString(),{fontFamily : 'Arial',
                                                                              fontWeight:'bold',
                                                                              fontSize: 100,
                                                                              fill: parameter_set.good_one_rgb_color,
                                                                              align : 'center'});

        goodOneLabel.anchor.set(0.5);
        goodOneLabel.x = sprite.width / 2;
        goodOneLabel.y = sprite.height / 4;

        container.addChild(goodOneLabel)

        //good one label
        let goodTwoLabel = new PIXI.Text(session_player.good_two_field.toString(),{fontFamily : 'Arial',
                                                                                        fontWeight:'bold',
                                                                                        fontSize: 100,
                                                                                        fill: parameter_set.good_two_rgb_color,
                                                                                        align : 'center'});

        goodTwoLabel.anchor.set(0.5);
        goodTwoLabel.x = sprite.width / 2;
        goodTwoLabel.y = sprite.height / 4 * 3;

        container.addChild(goodTwoLabel)

        container.x = pt.x;
        container.y = pt.y;
        container.pivot.set(container.width/2, container.height/2);
        container.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);
    
        session_players[i].fieldContainer = container;
        app.$data.pixi_app.stage.addChild(session_players[i].fieldContainer);
    }
},

/**
 * location grid for layout
 */
setupGrid(){
    x = app.$data.canvas_scale_width;
    y = app.$data.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale);

    for(let i=0;i<app.$data.grid_x-1; i++)
    {
        for(let i=0;i<app.$data.grid_y-1; i++)
        {
            const gr  = new PIXI.Graphics();
            gr.beginFill(0x000000);
            gr.drawCircle(x, y, 6);
            gr.endFill();
            
            app.$data.pixi_app.stage.addChild(gr);

            y+=app.$data.canvas_scale_height;
            y+=app.$data.grid_y_padding*app.$data.canvas_scale;
        }

        x += app.$data.canvas_scale_width;
        y = app.$data.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale);
    }
},

destroyPixiPlayers(){
    for(let i=0;i<session_players.length;i++)
    {
        session_players[i].houseContainer.destroy();
        session_players[i].fieldContainer.destroy();
    }
},

getLocationCordinates(index, field_or_house){

    let y=0;
    let x=0;

    if(index<=4)
    {
        if(field_or_house == "house")
            x = app.$data.canvas_scale_width * 3;
        else
            x = app.$data.canvas_scale_width * 2;

        y += index * (app.$data.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale));
    }
    else
    {
        if(field_or_house == "house")
            x = app.$data.canvas_scale_width * 8;
        else
            x = app.$data.canvas_scale_width * 9;

        y += (index-4) * (app.$data.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale));
    }    

    return {x:x, y:y};
},

handleFieldClick(index){
    alert('Field ' + (index+1).toString() + ' clicked');
},

handleHouseClick(index){
    alert('House ' + (index+1).toString() + ' clicked');
},