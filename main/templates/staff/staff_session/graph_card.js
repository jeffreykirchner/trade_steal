
{% load static %}
/**
 * Actions
 */

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
                                               antialias: true,
                                               resolution: devicePixelRatio,
                                               view: canvas });

    app.$data.canvas_width = canvas.width;
    app.$data.canvas_height = canvas.height;

    //add background rectangle
    let background = new PIXI.Graphics();
    background.beginFill(0xffffff);
    background.drawRect(0, 0, canvas.width, canvas.height);
    background.endFill();

    background.interactive = true;
    background.on("pointerup", (event) => { app.handleStagePointerUp() })
    background.on("pointermove", (event) => { app.handleStagePointerMove() })
    app.$data.pixi_app.stage.addChild(background);

    //transfer line
    let transfer_line = new PIXI.Graphics();
    transfer_line.visible = false;
    app.$data.pixi_transfer_line = transfer_line;
    app.$data.pixi_app.stage.addChild(app.$data.pixi_transfer_line);

    //sprite sheet
    PIXI.Loader.shared.add("{% static 'sprite_sheet.json' %}").load(app.setupPixiSheets);
},

/** load pixi sprite sheets
*/
setupPixiSheets(){
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

    session_players = app.$data.session.session_players;

    //setup pixi houses
    for(let i=0;i<session_players.length;i++)
    {
        if(session_players[i].parameter_set_player.town.toString() == app.$data.current_town){
            app.setupSingleHoue(i);
        } 
    }

    //setup pixi fields
    for(let i=0;i<session_players.length;i++)
    {
        if(session_players[i].parameter_set_player.town.toString() == app.$data.current_town){
             app.setupSingleField(i);
        }
    }
},

/**setup house container for player
 * @param index : int
 */
setupSingleHoue(index){
    let container = new PIXI.Container();

    pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'house');

    session_player = session_players[index];
    parameter_set_player = session_player.parameter_set_player;
    parameter_set = app.$data.session.parameter_set;

    //house texture
    let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["House0000"]);

    sprite.x = 0;
    sprite.y = 0;
    sprite.name = "house_texture"
    sprite.tint = 0xD3D3D3;

    container.addChild(sprite)

    //highlight
    let highlight = new PIXI.Graphics();
    highlight.beginFill(0xF7DC6F);
    highlight.drawRoundedRect(-sprite.width * 0.05, -sprite.height * 0.05, sprite.width + sprite.width * 0.1, sprite.height + sprite.height * 0.1, 20);
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
    let goodOneLabel = new PIXI.Text(session_player.good_one_house.toString(),{fontFamily : 'Arial',
                                                                            fontWeight:'bold',
                                                                            fontSize: 100,
                                                                            fill: parameter_set.good_a_rgb_color,
                                                                            align : 'center'});

    goodOneLabel.anchor.set(0.5);
    goodOneLabel.x = sprite.width / 2;
    goodOneLabel.y = 185;
    goodOneLabel.name = "good_a_label"

    container.addChild(goodOneLabel)

    //good one label
    let goodTwoLabel = new PIXI.Text(session_player.good_two_house.toString(),{fontFamily : 'Arial',
                                                                                    fontWeight:'bold',
                                                                                    fontSize: 100,
                                                                                    fill: parameter_set.good_b_rgb_color,
                                                                                    align : 'center'});

    goodTwoLabel.anchor.set(0.5);
    goodTwoLabel.x = sprite.width / 2;
    goodTwoLabel.y = 300;
    goodTwoLabel.name = "good_b_label"

    container.addChild(goodTwoLabel)

    container.x = pt.x;
    container.y = pt.y;
    container.pivot.set(container.width/2, container.height/2);
    container.interactive=true
    container.buttonMode = true;
    container.name = {type : 'house',
                      user_id: session_players[index].id,
                      modal_label: "House " + parameter_set_player.id_label,
                      good_one_color: parameter_set.good_a_rgb_color,
                      good_two_color: parameter_set.good_b_rgb_color, 
                      good_a_label : parameter_set.good_a_label,
                      good_b_label : parameter_set.good_b_label};
    container.on('pointerdown', (event) => { app.handleHousePointerDown(index) })
             .on('pointerup', (event) => { app.handleHousePointerUp(index) })
             .on('pointerover', (event) => { app.handleHousePointerOver(index) })
             .on('pointerout', (event) => { app.handleHousePointerOut(index) });

    container.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);

    session_players[index].houseContainer = container;
    app.$data.pixi_app.stage.addChild(session_players[index].houseContainer);
},

/**setup field container for player
 * @param index : int
 */
setupSingleField(index){
    let container = new PIXI.Container();

    pt = app.getLocationCordinates(session_players[index].parameter_set_player.location, 'field');

    session_player = session_players[index];
    parameter_set_player = session_player.parameter_set_player;
    parameter_set = app.$data.session.parameter_set;

    //house texture
    let sprite = PIXI.Sprite.from(app.$data.house_sheet.textures["Field0000"]);

    sprite.x = 0;
    sprite.y = 0;
    sprite.tint = 0xD3D3D3;    
    container.addChild(sprite)

    //highlight
    let highlight = new PIXI.Graphics();
    highlight.beginFill(0xF7DC6F);
    highlight.drawRoundedRect(-sprite.width * 0.05, -sprite.height * 0.05, sprite.width + sprite.width * 0.1, sprite.height + sprite.height * 0.1, 20);
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
    label.x = sprite.width - 25;
    label.y = 35;

    container.addChild(label);

    //good one label
    let goodOneLabel = new PIXI.Text(session_player.good_one_field.toString(),{fontFamily : 'Arial',
                                                                            fontWeight:'bold',
                                                                            fontSize: 100,
                                                                            fill: parameter_set.good_a_rgb_color,
                                                                            align : 'center'});

    goodOneLabel.anchor.set(0.5);
    goodOneLabel.x = sprite.width / 2;
    goodOneLabel.y = sprite.height / 4;

    container.addChild(goodOneLabel)

    //good two label
    let goodTwoLabel = new PIXI.Text(session_player.good_two_field.toString(),{fontFamily : 'Arial',
                                                                                    fontWeight:'bold',
                                                                                    fontSize: 100,
                                                                                    fill: parameter_set.good_b_rgb_color,
                                                                                    align : 'center'});

    goodTwoLabel.anchor.set(0.5);
    goodTwoLabel.x = sprite.width / 2;
    goodTwoLabel.y = sprite.height / 4 * 3;

    container.addChild(goodTwoLabel)

    container.x = pt.x;
    container.y = pt.y;
    container.name = {type : 'field',
                      user_id: session_players[index].id,
                      modal_label: "Field " + parameter_set_player.id_label,
                      good_one_color: parameter_set.good_a_rgb_color,
                      good_two_color: parameter_set.good_b_rgb_color, 
                      good_a_label : parameter_set.good_a_label,
                      good_b_label : parameter_set.good_b_label};

    container.pivot.set(container.width/2, container.height/2);
    container.hitArea = new PIXI.Rectangle(0, 0, container.width, container.height);    
    
    container.interactive=true
    container.buttonMode = true;
    container.on('pointerdown', (event) => { app.handleFieldPointerDown(index) })
             .on('pointerup', (event) => { app.handleFieldPointerUp(index) })
             .on('pointerover', (event) => { app.handleFieldPointerOver(index) })
             .on('pointerout', (event) => { app.handleFieldPointerOut(index) });
    //container.on('pointermove', (event) => { app.handleFieldPointerEnter(i) });
    
    container.scale.set(app.$data.canvas_scale, app.$data.canvas_scale);

    session_players[index].fieldContainer = container;
    app.$data.pixi_app.stage.addChild(session_players[index].fieldContainer);
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
 
/**destroy house and field containers
 */
destroyPixiPlayers(){
    session_players = app.$data.session.session_players;
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

/**
 *pointer down on field
 */
handleFieldPointerDown(index){
    console.log('Field ' + (index+1).toString() + ' down');
    app.handleContainerDown(session_players[index].fieldContainer);
},

/**
 *pointer up on field
 */
handleFieldPointerUp(index){
    console.log('Field ' + (index+1).toString() + ' up');
    app.handleContainerUp(session_players[index].fieldContainer);
},

/**
 *pointer move over field
 */
handleFieldPointerOver(index){
    console.log('Field ' + (index+1).toString() + ' Over');
    app.setContainerAsTarget(session_players[index].fieldContainer);
},

/**
 *pointer move off field
 */
handleFieldPointerOut(index){
    console.log('Field ' + (index+1).toString() + ' Out');
    app.removeContainerTarget(session_players[index].fieldContainer);
},

/**
 *pointer down on house
 */
handleHousePointerDown(index){
    console.log('House ' + (index+1).toString() + ' down');
    app.handleContainerDown(session_players[index].houseContainer);
},

/**
 *pointer up on house
 */
handleHousePointerUp(index){
    console.log('House ' + (index+1).toString() + ' up');
    app.handleContainerUp(session_players[index].houseContainer);
},

/**
 *pointer over house
 */
handleHousePointerOver(index){
    console.log('House ' + (index+1).toString() + ' Over');
    app.setContainerAsTarget(session_players[index].houseContainer);
},

/**
 *pointer move off house
 */
handleHousePointerOut(index){
    console.log('House ' + (index+1).toString() + ' Out');
    app.removeContainerTarget(session_players[index].houseContainer);
},

/**
 * handle container mouse down
 */
handleContainerDown(container){
    app.turnOffHighlights();

    container.getChildByName("highlight").visible=true;
    app.$data.pixi_transfer_source = container;
    app.updatePixiTransfer(event.offsetX , event.offsetY);
},

/**
 * handle container mouse up
 */
handleContainerUp(container){
    app.setContainerAsTarget(container);
    app.showTransferModal(container);
},

/**set specified container as trasnfer target target
*/
setContainerAsTarget(container)
{
    if(app.$data.pixi_transfer_line.visible && !app.pixi_modal_open)
    {
        if(container !=  app.$data.pixi_transfer_source)
        {
            app.$data.pixi_transfer_target = container;
            container.getChildByName("highlight").visible=true;
        }       
    }
},

/**remove container target when pointer moves off of it
*/
removeContainerTarget(container){
    if(container ==  app.$data.pixi_transfer_target && !app.pixi_modal_open)
    {
        app.$data.pixi_transfer_target = null;
        container.getChildByName("highlight").visible=false;
    }
},

/**
 *pointer up on stage
 */
 handleStagePointerUp(){
    console.log('Stage up: ' + event);
    app.turnOffHighlights();
},

/**
 * pointer move over stage
 */
 handleStagePointerMove(){
    if(app.$data.pixi_transfer_line.visible && !app.pixi_modal_open)
    {
        app.updatePixiTransfer(event.offsetX, event.offsetY);
    }
},

/** show transfer modal when mouse up on valid target
*/
showTransferModal(container){

    if(app.pixi_modal_open) return;

    if(!app.$data.pixi_transfer_line.visible ||
       container ==  app.$data.pixi_transfer_source ||
       app.$data.pixi_transfer_source == null ||
       app.$data.pixi_transfer_target == null)
    {
        app.turnOffHighlights();
        return;
    } 

    app.$data.transfer_source_modal_string = app.$data.pixi_transfer_source.name.modal_label;
    app.$data.transfer_target_modal_string = app.$data.pixi_transfer_target.name.modal_label;

    app.$data.transfer_modal_good_one_rgb = app.$data.pixi_transfer_source.name.good_one_color;
    app.$data.transfer_modal_good_two_rgb = app.$data.pixi_transfer_source.name.good_two_color;

    app.$data.transfer_modal_good_one_name = app.$data.pixi_transfer_source.name.good_a_label;
    app.$data.transfer_modal_good_two_name = app.$data.pixi_transfer_source.name.good_b_label;

    app.$data.pixi_modal_open = true;
    app.$data.cancelModal=true;

    var myModal = new bootstrap.Modal(document.getElementById('moveGoodsModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** show transfer modal
*/
hideTransferModal:function(){
    if(app.$data.cancelModal)
    {
       
    }

    app.$data.pixi_modal_open = false;
    app.turnOffHighlights();
},

turnOffHighlights(){
    if(app.pixi_modal_open) return;

    session_players = app.$data.session.session_players;
    
    for(let i=0;i<session_players.length;i++)
    {
        if(session_players[i].houseContainer)
            if(session_players[i].houseContainer.getChildByName("highlight"))
                session_players[i].houseContainer.getChildByName("highlight").visible=false;

        if(session_players[i].fieldContainer)
            if(session_players[i].fieldContainer.getChildByName("highlight"))
                session_players[i].fieldContainer.getChildByName("highlight").visible=false;
    }

    app.$data.pixi_transfer_line.visible=false;
},

updatePixiTransfer(target_x, target_y){
    transfer_line = app.$data.pixi_transfer_line;
    source = app.$data.pixi_transfer_source;

    transfer_line.clear();

    transfer_line.visible=true;
    transfer_line.lineStyle({width:10, color:0xF7DC6F, alpha:1, alignment:0.5, cap:PIXI.LINE_CAP.SQUARE});
    transfer_line.moveTo(target_x, target_y);
    transfer_line.lineTo(source.x, source.y);
},


/**
 * Actions
 */

/** show the move goods modal
*/
sendMoveGoods(){
    
    if(app.$data.working == true) return;
    if(!app.$data.pixi_transfer_source) return;
    if(!app.$data.pixi_transfer_target) return; 



    app.$data.working = true;
    app.sendMessage("move_goods", {"sessionID" : app.$data.sessionID,
                                   "sourceType" : app.$data.pixi_transfer_source.name.type.toString(),
                                   "sourceID" : app.$data.pixi_transfer_source.name.user_id.toString(),
                                   "targetType" : app.$data.pixi_transfer_target.name.type.toString(),
                                   "targetID" : app.$data.pixi_transfer_target.name.user_id.toString(),
                                   "formData" : $("#moveGoodsForm").serializeArray(),});
},

/** take result of moving goods
*/
takeMoveGoods(messageData){
    //app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeUpdateGoods(messageData);       
        $('#moveGoodsModal').modal('hide');

        app.$data.transfer_good_one_amount = 0;  
        app.$data.transfer_good_two_amount = 0;            
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    }
},

/**
 * take update to good counts
 */
takeUpdateGoods(){
    results = messageData.status.result;

    for(let r=0; r<results.length; r++){
        player_id = results[r].id;

        for(let p=0; p<app.$data.session.session_players.length; p++)
        {
            player = app.$data.session.session_players[p];

            if(player.id == player_id)
            {
                player.good_one_house = results[r].good_one_house;
                player.good_two_house = results[r].good_two_house;

                player.good_one_field = results[r].good_one_field;
                player.good_two_field = results[r].good_two_field;

                player.houseContainer.destroy();
                player.fieldContainer.destroy();

                app.setupSingleHoue(p);
                app.setupSingleField(p);

                break;
            }
        }
    }
},

/**
 * change the town shown
 */
change_town_view(){
    app.destroyPixiPlayers();
    app.setupPixiPlayers();
},