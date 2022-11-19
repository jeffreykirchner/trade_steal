{% load static %}

/**
 * update the pixi players with new info
 */
setupPixi(){    
    app.resetPixiApp();
    PIXI.Loader.shared.add("{% static graph_sprite_sheet %}")
                      .add("{% static avatar_sprite_sheet %}")
                      .load(app.setupPixiSheets);
},

resetPixiApp(){
    let canvas = document.getElementById('sd_graph_id');
    //     ctx = canvas.getContext('2d');

    // app.$data.canvas_width = ctx.canvas.width;
    // app.$data.canvas_height = ctx.canvas.height;

    app.$data.pixi_app = new PIXI.Application({resizeTo : canvas,
                                               backgroundColor : 0xFFFFFF,
                                               autoResize: true,
                                               antialias: false,
                                               resolution: 1,
                                               view: canvas });

    app.canvas_width = canvas.width;
    app.canvas_height = canvas.height;

    //add background rectangle
    let background = new PIXI.Graphics();
    background.beginFill(0xffffff);
    background.drawRect(0, 0, canvas.width, canvas.height);
    background.endFill();

    background.interactive = true;
    background.on("pointerup", app.handleStagePointerUp)
              .on("pointermove", app.handleStagePointerMove);
    app.$data.pixi_app.stage.addChild(background);

    //transfer line
    let transfer_line = new PIXI.Graphics();
    transfer_line.visible = false;
    app.$data.pixi_transfer_line = transfer_line;
    app.$data.pixi_app.stage.addChild(app.$data.pixi_transfer_line);
},

/** load pixi sprite sheets
*/
setupPixiSheets(){
    app.$data.house_sheet = PIXI.Loader.shared.resources["{% static parameters.graph_sprite_sheet %}"].spritesheet;
    app.$data.avatar_sheet = PIXI.Loader.shared.resources["{% static parameters.avatar_sprite_sheet %}"].spritesheet;
    app.$data.house_sprite = new PIXI.Sprite(app.$data.house_sheet.textures["House0000"]);

    app.$data.grid_x = 11;
    app.$data.grid_y = 5;

    app.$data.grid_y_padding = 30;

    app.canvas_scale_height = app.canvas_height / app.$data.grid_y;
    app.canvas_scale_width = app.canvas_width / app.$data.grid_x;
    app.$data.canvas_scale = app.canvas_scale_height /  app.$data.house_sprite.height;

    app.$data.pixi_loaded = true;
    app.setupPixiPlayers();

    //layout for testing
    //app.setupGrid();
},

/**
 * setup pixi players
 */
setupPixiPlayers(){

    if(!app.$data.pixi_loaded) return;
    if(!app.$data.session.parameter_set.show_avatars=="True") return;

    let session_players = app.$data.session.session_players;
    let session = app.$data.session;
    let session_player = app.$data.session_player;

    //setup pixi houses
    for(let i=0;i<session_players.length;i++)
    {        
        app.setupSingleHouse(i);
    }

    //setup pixi fields
    for(let i=0;i<session_players.length;i++)
    {
        app.setupSingleField(i);
    }

    //setup pixi avatars
    if(app.$data.session.parameter_set.show_avatars == "True")
    {
        for(let i=0;i<session_players.length;i++)
        {
            app.setupSingleAvatar(i);
        }
    }

    if(app.is_subject)
        app.setFieldHouseVisbility(app.$data.session.started);
},

/**setup house container for player
 * @param index : int
 */
setupSingleHouse(index){
    let session_players = app.$data.session.session_players;
    let session_player = session_players[index];

    if(session_players[index].parameter_set_player.town.toString() != app.$data.current_town) return;

    if(session_player.houseContainer)
    {
        session_player.houseContainer.destroy();
        session_player.houseContainer=null;
    }

    let container = new PIXI.Container();
    
    let parameter_set_player = session_player.parameter_set_player;
    let parameter_set = app.$data.session.parameter_set;

    let pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'house');

    let y_location_good_one = 0;
    let y_location_good_two = 0;
    let y_location_good_three = 0;

    //y locations of goods
    if(parameter_set.good_count == 2){
        y_location_good_one = 185;
        y_location_good_two = 300;
    }
    else{
        y_location_good_one = 130;
        y_location_good_two = 230;
        y_location_good_three = 330;
    }
    
    //house texture
    let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["House0000"]);

    sprite.x = 0;
    sprite.y = 0;
    sprite.name = "house_texture"

    
    if(typeof app.$data.session_player != 'undefined' && session_players[index].player_number == app.$data.session_player.player_number){
        sprite.tint = app.$data.owner_color;
    }
    else{
        sprite.tint = app.$data.other_color;
    }

    container.addChild(sprite)

    //highlight
    let highlight = new PIXI.Graphics();
    highlight.beginFill(0xF7DC6F);
    highlight.drawRoundedRect(-sprite.width * 0.04, -sprite.height * 0.04, sprite.width + sprite.width * 0.08, sprite.height + sprite.height * 0.08, 20);
    highlight.name = "highlight";
    highlight.endFill();
    highlight.visible=false;
    container.addChildAt(highlight, 0)

    //house label texture
    let label = new PIXI.Text(parameter_set_player.id_label,{fontFamily : 'Arial',
                                                             fontWeight:'bold',
                                                             fontSize: 48,
                                                             align : 'center'});
    label.anchor.set(0.5);
    label.x = sprite.width / 2;
    label.y = 50;
    label.name = "id_label"

    container.addChild(label);

    //good one label   
    container.addChild(app.createGoodLabel(session_player.good_one_house.toString(),
                                           "good_a_label",
                                           parameter_set_player.good_one.rgb_color,
                                           sprite.width / 2,
                                           y_location_good_one))

    //good two label
    container.addChild(app.createGoodLabel(session_player.good_two_house.toString(),
                                           "good_b_label",
                                           parameter_set_player.good_two.rgb_color,
                                           sprite.width / 2,
                                           y_location_good_two))

    //good three label
    if(parameter_set.good_count == 3){
        container.addChild(app.createGoodLabel(session_player.good_three_house.toString(),
                                               "good_c_label",
                                               parameter_set_player.good_three.rgb_color,
                                               sprite.width / 2,
                                               y_location_good_three))
    }


    container.x = pt.x;
    container.y = pt.y;
    container.pivot.set(container.width/2, container.height/2);
    container.interactive=true
    container.buttonMode = true;
    container.name = {type : 'house',
                      index : index, 
                      user_id: session_players[index].id,
                      modal_label: "House " + parameter_set_player.id_label,

                      good_one_color: parameter_set_player.good_one.rgb_color,
                      good_two_color: parameter_set_player.good_two.rgb_color,
                      good_three_color: parameter_set_player.good_three.rgb_color,

                      good_a_label : parameter_set_player.good_one.label,
                      good_b_label : parameter_set_player.good_two.label,
                      good_c_label : parameter_set_player.good_three.label,};

    if(app.$data.is_subject)  //only subject screen can move items
        if(app.$data.session.parameter_set.allow_stealing == "True" || session_players[index].id == app.$data.session_player.id)
            container.on('pointerdown', app.handleHousePointerDown.bind(this, index));

    container.on('pointerup', app.handleHousePointerUp.bind(this, index))
             .on('pointerover', app.handleHousePointerOver.bind(this, index))
             .on('pointerout', app.handleHousePointerOut.bind(this, index));

    container.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);

    session_players[index].houseContainer = container;
    app.$data.pixi_app.stage.addChild(session_players[index].houseContainer);
},

/**
 * return a pixi good label
 * @param amount : int : amount of good to be displayed
 * @param label_name : string : name of label in container
 * @param rgb_color : string : rgb color of label
 * @param x_location : float : x location of label within container
 * @param y_location : float : y location of label within container
 */
createGoodLabel(amount, label_name, rgb_color, x_location, y_location){

    amount = Math.round(amount);

    let goodOneLabel = new PIXI.Text(amount,{fontFamily : 'Arial',
                                            fontWeight:'bold',
                                            fontSize: 100,
                                            fill: rgb_color,
                                            dropShadow : true,
                                            dropShadowBlur : 5,
                                            align : 'center'});

    goodOneLabel.anchor.set(0.5);
    goodOneLabel.x = x_location;
    goodOneLabel.y = y_location;
    goodOneLabel.name = label_name;

    return goodOneLabel;
},

/**setup field container for player
 * @param index : int
 */
setupSingleField(index){
    let session_players = app.$data.session.session_players;
    let session_player = session_players[index];

    if(session_players[index].parameter_set_player.town.toString() != app.$data.current_town) return;

    if(session_player.fieldContainer)
    {
        session_player.fieldContainer.destroy();
        session_player.fieldContainer=null;
    }

    let container = new PIXI.Container();

    let parameter_set_player = session_player.parameter_set_player;
    let parameter_set = app.$data.session.parameter_set;

    let pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'field');

    //field texture
    let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["Field0000"]);

    sprite.x = 0;
    sprite.y = 0;
    if(typeof app.$data.session_player != 'undefined' && session_players[index].player_number == app.$data.session_player.player_number){
        sprite.tint = app.$data.owner_color;
    }
    else{
        sprite.tint = app.$data.other_color;
    }    
    container.addChild(sprite)

    //highlight
    let highlight = new PIXI.Graphics();
    highlight.beginFill(0xF7DC6F);
    highlight.drawRoundedRect(-sprite.width * 0.04, -sprite.height * 0.04, sprite.width + sprite.width * 0.08, sprite.height + sprite.height * 0.08, 20);
    highlight.name = "highlight";
    highlight.endFill();
    highlight.visible=false;
    container.addChildAt(highlight, 0)

    //field id label texture
    let label = new PIXI.Text(parameter_set_player.id_label,{fontFamily : 'Arial',
                                                                    fontWeight:'bold',
                                                                    fontSize: 48,
                                                                    align : 'center'});
    label.anchor.set(0.5);
    label.x = sprite.width - 25;
    label.y = 35;

    container.addChild(label);

    //field group label texture
    if(!app.$data.is_subject){    
        let label_group = new PIXI.Text("G" + session_player.group_number,{fontFamily : 'Arial',
                                                                fontWeight:'bold',
                                                                fontSize: 40,
                                                                align : 'center'});
        //label_group.anchor.set(0.5);
        label_group.x = 10;
        label_group.y = 8;

        container.addChild(label_group);
    }

    //good one label
    container.addChild(app.createGoodLabel(session_player.good_one_field.toString(),
                                           "good_a_label",
                                           parameter_set_player.good_one.rgb_color,
                                           sprite.width / 2,
                                           sprite.height / 4))

    //good two label
    container.addChild(app.createGoodLabel(session_player.good_two_field.toString(),
                                           "good_b_label",
                                           parameter_set_player.good_two.rgb_color,
                                           sprite.width / 2,
                                           sprite.height / 4 * 3))

    container.x = pt.x;
    container.y = pt.y;
    container.name = {type : 'field',
                      index:index,
                      user_id: session_players[index].id,
                      modal_label: "Field " + parameter_set_player.id_label,
                      
                      good_one_color: parameter_set_player.good_one.rgb_color,
                      good_two_color: parameter_set_player.good_two.rgb_color, 

                      good_a_label : parameter_set_player.good_one.label,
                      good_b_label : parameter_set_player.good_two.label};

    container.pivot.set(container.width/2, container.height/2);
    container.hitArea = new PIXI.Rectangle(0, 0, container.width, container.height);    
    
    container.interactive = true;
    container.buttonMode = true;

    //prevent stealing    
    if(app.$data.is_subject)  //only subject screen can move items
        if(app.$data.session.parameter_set.allow_stealing == "True" || session_players[index].id == app.$data.session_player.id)
            container.on('pointerdown', app.handleFieldPointerDown.bind(this, index));

    container.on('pointerup', app.handleFieldPointerUp.bind(this, index))
             .on('pointerover', app.handleFieldPointerOver.bind(this, index))
             .on('pointerout', app.handleFieldPointerOut.bind(this, index));
    
    container.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);

    session_players[index].fieldContainer = container;
    app.$data.pixi_app.stage.addChild(session_players[index].fieldContainer);
},

/**setup avatar container for player */
setupSingleAvatar(index){

    let session_players = app.$data.session.session_players;
    let session_player = session_players[index];

    if(session_players[index].parameter_set_player.town.toString() != app.$data.current_town) return;
    if(!session_players[index].avatar && !session_players[index].parameter_set_player.avatar) return;

    if(session_player.avatarContainer)
    {
        session_player.avatarContainer.destroy();
        session_player.avatarContainer=null;
    }

    let container = new PIXI.Container();

    let parameter_set_player = session_player.parameter_set_player;
    let parameter_set = app.$data.session.parameter_set;

    let pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'avatar');
    
    let sprite = null;

    if(session_players[index].avatar)
    {
        sprite = PIXI.Sprite.from(this.avatar_sheet.textures[session_players[index].avatar.file_name]);
    }
    else
    {
        sprite = PIXI.Sprite.from(this.avatar_sheet.textures[session_players[index].parameter_set_player.avatar.file_name]);
    }
    
    sprite.x = 0;
    sprite.y = 0;   
    container.addChild(sprite);

    let scale = (app.canvas_width/9) / container.width;

    container.pivot.set(container.width/2, container.height/2);
    container.scale.set(scale, scale);

    let container2 = new PIXI.Container();
    container2.x = pt.x;
    container2.y = pt.y;
    container2.addChild(container);

    //avatar label texture
    let label = new PIXI.Text(parameter_set_player.id_label,{fontFamily : 'Arial',
        fontWeight:'bold',
        fontSize: 15,
        align : 'center'});

    label.anchor.set(0.5);
    label.x = container2.width/2 -20;
    label.y = -container2.height/2 + 20;

    container2.addChild(label);

    session_players[index].avatarContainer = container2;
    app.$data.pixi_app.stage.addChild(session_players[index].avatarContainer);
},
/**
 * location grid for layout
 */
setupGrid(){
    x = app.canvas_scale_width;
    y = app.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale);

    for(let i=0;i<app.$data.grid_x-1; i++)
    {
        for(let i=0;i<app.$data.grid_y-1; i++)
        {
            const gr  = new PIXI.Graphics();
            gr.beginFill(0x000000);
            gr.drawCircle(x, y, 6);
            gr.endFill();
            
            app.$data.pixi_app.stage.addChild(gr);

            y+=app.canvas_scale_height;
            y+=app.$data.grid_y_padding*app.$data.canvas_scale;
        }

        x += app.canvas_scale_width;
        y = app.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale);
    }
},
 
/**destroy house and field containers
 */
destroyPixiPlayers(){
    let session_players = app.$data.session.session_players;
    
    for(let i=0;i<session_players.length;i++)
    {
        if(session_players[i].houseContainer)
        {
            session_players[i].houseContainer.destroy();
            session_players[i].houseContainer = null;
        }

        if(session_players[i].fieldContainer)
        {
            session_players[i].fieldContainer.destroy();
            session_players[i].fieldContainer = null;
        }

        if(session_players[i].avatarContainer)
        {
            session_players[i].avatarContainer.destroy();
            session_players[i].avatarContainer = null;
        }
    }
},

/** location of house and fields
 */
getLocationCordinates(index, field_or_house){

    let y=0;
    let x=0;

    if(index<=4)
    {
        if(field_or_house == "house")
            x = app.canvas_scale_width * 3;
        else if (field_or_house == "field")
            x = app.canvas_scale_width * 2;
        else
            x = app.canvas_scale_width * 1;

        y += index * (app.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale));
    }
    else
    {
        if(field_or_house == "house")
            x = app.canvas_scale_width * 8;
        else if (field_or_house == "field")
            x = app.canvas_scale_width * 9;
        else
            x = app.canvas_scale_width * 10;

        y += (index-4) * (app.canvas_scale_height + (app.$data.grid_y_padding*app.$data.canvas_scale));
    }    

    return {x:x, y:y};
},