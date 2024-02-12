{% load static %}

/**
 * update the pixi players with new info
 */
setupPixi: function setupPixi(){    
    app.resetPixiApp();
    // PIXI.Loader.shared.add("{% static graph_sprite_sheet %}")
    //                   .add("{% static avatar_sprite_sheet %}")
    //                   .load(app.setupPixiSheets);

    PIXI.Assets.add({alias:'graph_sprite_sheet', src:'{% static graph_sprite_sheet %}'});

    let load_list = ['graph_sprite_sheet'];

    if(app.session.parameter_set.show_avatars=="True")
    {

        //load avatars from choice grid
        for(let i in app.session.parameter_set.parameter_set_avatars)
        {
            let avatar = app.session.parameter_set.parameter_set_avatars[i].avatar;

            if(avatar)
            {
                if(load_list.includes(avatar.label)) continue;

                PIXI.Assets.add({alias:avatar.label, src:"/static/avatars/" + avatar.file_name});
                load_list.push(avatar.label);
            }
        }

        //load avatars from players
        for(let i in app.session.parameter_set.parameter_set_players)
        {
            let avatar = app.session.parameter_set.parameter_set_players[i].avatar;

            if(load_list.includes(avatar.label)) continue;

            PIXI.Assets.add({alias:avatar.label, src:"/static/avatars/" + avatar.file_name});
            load_list.push(avatar.label);

        }

        // PIXI.Assets.add({alias:"Blank", src:"/static/avatars/blank.png"});
        // load_list.push("Blank");

        // PIXI.Assets.add({alias:'avatar_sprite_sheet', src:'{% static avatar_sprite_sheet %}'});
        // load_list.push('avatar_sprite_sheet');
    }

    const textures_promise = PIXI.Assets.load(load_list);

    textures_promise.then((textures) => {
        app.setupPixiSheets(textures);
    });
},

resetPixiApp: function resetPixiApp(){
    let canvas = document.getElementById('sd_graph_id');
    //     ctx = canvas.getContext('2d');

    // app.canvas_width = ctx.canvas.width;
    // app.canvas_height = ctx.canvas.height;

    pixi_app = new PIXI.Application({resizeTo : canvas,
                                               backgroundColor : 0xFFFFFF,
                                               autoResize: true,
                                               antialias: false,
                                               resolution: window.devicePixelRatio,
                                               view: canvas });

    app.canvas_width = canvas.width;
    app.canvas_height = canvas.height;

    pixi_app.stage.eventMode = 'passive';
    //pixi_app.stage.sortableChildren = true;

    //add background rectangle
    let container1 = new PIXI.Container();
    let container2 = new PIXI.Container();

    let background1 = new PIXI.Graphics();
    background1.beginFill(0xffffff);
    background1.drawRect(0, 0, canvas.width, canvas.height);
    background1.endFill();

    let background2 = new PIXI.Graphics();
    background2.beginFill(0xffffff);
    background2.drawRect(0, 0, canvas.width, canvas.height);
    background2.endFill();

    container1.addChild(background1);
    container2.addChild(background2);
    
    container2.eventMode = 'passive';
    background2.eventMode = 'static';
    //background2.buttonMode = true;
    background2.on("pointerup", app.handleStagePointerUp.bind(this))
               .on("pointermove", app.handleStagePointerMove.bind(this));

    pixi_app.stage.addChild(container1);
    pixi_app.stage.addChild(container2);

    //transfer line
    let transfer_line = new PIXI.Graphics();
    transfer_line.visible = false;
    pixi_transfer_line = transfer_line;
    pixi_app.stage.addChild(pixi_transfer_line);
},

/** load pixi sprite sheets
*/
setupPixiSheets: function setupPixiSheets(textures){
    pixi_textures = textures;

    app.house_sheet = textures.graph_sprite_sheet;
    app.avatar_sheet = textures.avatar_sprite_sheet;
    app.house_sprite = new PIXI.Sprite(app.house_sheet.textures["House0000"]);

    app.grid_x = 11;
    app.grid_y = 5;

    app.grid_y_padding = 30;

    app.canvas_scale_height = app.canvas_height / app.grid_y;
    app.canvas_scale_width = app.canvas_width / app.grid_x;
    app.canvas_scale = (app.canvas_scale_height /  app.house_sprite.height) * (1/window.devicePixelRatio);

    app.pixi_loaded = true;
    app.setupPixiPlayers();

    //layout for testing
    //app.setupGrid();
},

/**
 * setup pixi players
 */
setupPixiPlayers: function setupPixiPlayers(){

    if(!app.pixi_loaded) return;
    if(!app.session.parameter_set.show_avatars=="True") return;

    let session_players = app.session.session_players;
    let session = app.session;
    let session_player = app.session_player;

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
    if(app.session.parameter_set.show_avatars == "True")
    {
        for(let i=0;i<session_players.length;i++)
        {
            app.setupSingleAvatar(i);
        }
    }

    if(app.is_subject)
        app.setFieldHouseVisbility(app.session.started);
},

/**setup house container for player
 * @param index : int
 */
setupSingleHouse: function setupSingleHouse(index){
    let session_players = app.session.session_players;
    let session_player = session_players[index];

    if(session_players[index].parameter_set_player.town.toString() != app.current_town) return;

    if(house_containers[index])
    {
        house_containers[index].destroy();
        house_containers[index]=null;
    }

    let container = new PIXI.Container();
    
    let parameter_set_player = session_player.parameter_set_player;
    let parameter_set = app.session.parameter_set;

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
    let sprite = PIXI.Sprite.from(app.house_sheet.textures["House0000"]);

    sprite.x = 0;
    sprite.y = 0;
    sprite.name = "house_texture"

    
    if(typeof app.session_player != 'undefined' && session_players[index].player_number == app.session_player.player_number){
        sprite.tint = app.owner_color;
    }
    else{
        sprite.tint = app.other_color;
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
    container.eventMode = 'static';
    //container.buttonMode = true;
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

    if(app.is_subject)  //only subject screen can move items
        if(app.session.parameter_set.allow_stealing == "True" || session_players[index].id == app.session_player.id)
            container.on('pointerdown', app.handleHousePointerDown.bind(this, index));

    container.on('pointerup', app.handleHousePointerUp.bind(this, index))
             .on('pointerover', app.handleHousePointerOver.bind(this, index))
             .on('pointerout', app.handleHousePointerOut.bind(this, index))
             .on('pointermove', app.handleHousePointerMove.bind(this, index));

    container.scale.set(app.canvas_scale, app.canvas_scale);

    house_containers[index] = container;
    pixi_app.stage.addChild(house_containers[index]);
},

/**
 * return a pixi good label
 * @param amount : int : amount of good to be displayed
 * @param label_name : string : name of label in container
 * @param rgb_color : string : rgb color of label
 * @param x_location : float : x location of label within container
 * @param y_location : float : y location of label within container
 */
createGoodLabel: function createGoodLabel(amount, label_name, rgb_color, x_location, y_location){

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
setupSingleField: function setupSingleField(index){
    let session_players = app.session.session_players;
    let session_player = session_players[index];

    if(session_players[index].parameter_set_player.town.toString() != app.current_town) return;

    if(field_containers[index])
    {
        field_containers[index].destroy();
        field_containers[index]=null;
    }

    let container = new PIXI.Container();

    let parameter_set_player = session_player.parameter_set_player;
    let parameter_set = app.session.parameter_set;

    let pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'field');

    //field texture
    let sprite = PIXI.Sprite.from(app.house_sheet.textures["Field0000"]);

    sprite.x = 0;
    sprite.y = 0;
    if(typeof app.session_player != 'undefined' && session_players[index].player_number == app.session_player.player_number){
        sprite.tint = app.owner_color;
    }
    else{
        sprite.tint = app.other_color;
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
    if(!app.is_subject){    
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
    
    container.eventMode = 'static';
    //container.buttonMode = true;

    //prevent stealing    
    if(app.is_subject)  //only subject screen can move items
        if(app.session.parameter_set.allow_stealing == "True" || session_players[index].id == app.session_player.id)
            container.on('pointerdown', app.handleFieldPointerDown.bind(this, index));

    container.on('pointerup', app.handleFieldPointerUp.bind(this, index))
             .on('pointerover', app.handleFieldPointerOver.bind(this, index))
             .on('pointerout', app.handleFieldPointerOut.bind(this, index))
             .on('pointermove', app.handleFieldPointerMove.bind(this, index));
    
    container.scale.set(app.canvas_scale, app.canvas_scale);

    field_containers[index] = container;
    pixi_app.stage.addChild(field_containers[index]);
},

/**setup avatar container for player */
setupSingleAvatar: function setupSingleAvatar(index){

    let session_players = app.session.session_players;
    let session_player = session_players[index];

    if(session_players[index].parameter_set_player.town.toString() != app.current_town) return;
    if(!session_players[index].avatar && !session_players[index].parameter_set_player.avatar) return;

    if(avatar_containers[index])
    {
        avatar_containers[index].destroy();
        avatar_containers[index]=null;
    }

    let container = new PIXI.Container();

    let parameter_set_player = session_player.parameter_set_player;
    let parameter_set = app.session.parameter_set;

    let pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'avatar');
    
    let sprite = null;

    if(session_players[index].avatar)
    {
        pixi_textures[session_players[index].avatar.label].baseTexture.mipmap = PIXI.MIPMAP_MODES.ON;
        sprite = new PIXI.Sprite(pixi_textures[session_players[index].avatar.label]);
    }
    else
    {
        pixi_textures[session_players[index].parameter_set_player.avatar.label].baseTexture.mipmap = PIXI.MIPMAP_MODES.ON;
        sprite = new PIXI.Sprite(pixi_textures[session_players[index].parameter_set_player.avatar.label]);
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

    avatar_containers[index] = container2;
    pixi_app.stage.addChildAt(avatar_containers[index],2);
},
/**
 * location grid for layout
 */
setupGrid: function setupGrid(){
    x = app.canvas_scale_width;
    y = app.canvas_scale_height + (app.grid_y_padding*app.canvas_scale);

    for(let i=0;i<app.grid_x-1; i++)
    {
        for(let i=0;i<app.grid_y-1; i++)
        {
            const gr  = new PIXI.Graphics();
            gr.beginFill(0x000000);
            gr.drawCircle(x, y, 6);
            gr.endFill();
            
            pixi_app.stage.addChild(gr);

            y+=app.canvas_scale_height;
            y+=app.grid_y_padding*app.canvas_scale;
        }

        x += app.canvas_scale_width;
        y = app.canvas_scale_height + (app.grid_y_padding*app.canvas_scale);
    }
},
 
/**destroy house and field containers
 */
destroyPixiPlayers: function destroyPixiPlayers(){
    let session_players = app.session.session_players;
    
    for(let i=0;i<session_players.length;i++)
    {
        if(house_containers[i])
        {
            house_containers[i].destroy();
            house_containers[i] = null;
        }

        if(field_containers[i])
        {
            field_containers[i].destroy();
            field_containers[i] = null;
        }

        if(avatar_containers[i])
        {
            avatar_containers[i].destroy();
            avatar_containers[i] = null;
        }
    }
},

/** location of house and fields
 */
getLocationCordinates: function getLocationCordinates(index, field_or_house){

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

        y += index * (app.canvas_scale_height + (app.grid_y_padding*app.canvas_scale));
    }
    else
    {
        if(field_or_house == "house")
            x = app.canvas_scale_width * 8;
        else if (field_or_house == "field")
            x = app.canvas_scale_width * 9;
        else
            x = app.canvas_scale_width * 10;

        y += (index-4) * (app.canvas_scale_height + (app.grid_y_padding*app.canvas_scale));
    }    

    x *= (1/window.devicePixelRatio);
    y *= (1/window.devicePixelRatio);

    return {x:x, y:y};
},