
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

    session_players = app.$data.session.session_players;

    //setup pixi houses
    for(let i=0;i<session_players.length;i++)
    {
        app.setupSingleHoue(i);
    }

    //setup pixi fields
    for(let i=0;i<session_players.length;i++)
    {
        app.setupSingleField(i);
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
                                                                            fill: parameter_set.good_one_rgb_color,
                                                                            align : 'center'});

    goodOneLabel.anchor.set(0.5);
    goodOneLabel.x = sprite.width / 2;
    goodOneLabel.y = 185;
    goodOneLabel.name = "good_one_label"

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
    goodTwoLabel.name = "good_two_label"

    container.addChild(goodTwoLabel)

    container.x = pt.x;
    container.y = pt.y;
    container.pivot.set(container.width/2, container.height/2);
    container.interactive=true
    container.buttonMode = true;
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
    for(let i=0;i<session_players.length;i++)
    {
        session_players[i].houseContainer.destroy();
        session_players[i].fieldContainer.destroy();
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
    app.turnOffHighlights();

    session_players[index].fieldContainer.getChildByName("highlight").visible=true;
    app.$data.pixi_transfer_source = session_players[index].fieldContainer;
    app.updatePixiTransfer(event.offsetX , event.offsetY); 
},

/**
 *pointer up on field
 */
handleFieldPointerUp(index){
    console.log('Field ' + (index+1).toString() + ' up');
    app.setContainerAsTarget(session_players[index].fieldContainer);
    app.showTransferModal(session_players[index].fieldContainer);
},

handleFieldPointerOver(index){
    console.log('Field ' + (index+1).toString() + ' Over');
    app.setContainerAsTarget(session_players[index].fieldContainer);
},

handleFieldPointerOut(index){
    console.log('Field ' + (index+1).toString() + ' Out');

    if(session_players[index].fieldContainer ==  app.$data.pixi_transfer_target)
    {
        app.$data.pixi_transfer_target = null;
        session_players[index].fieldContainer.getChildByName("highlight").visible=false;
    }
},

/**
 *pointer down on house
 */
handleHousePointerDown(index){
    console.log('House ' + (index+1).toString() + ' down');
    app.turnOffHighlights();

    session_players[index].houseContainer.getChildByName("highlight").visible=true;
    app.$data.pixi_transfer_source = session_players[index].houseContainer;
    app.updatePixiTransfer(event.offsetX , event.offsetY);    
},

/**
 *pointer up on house
 */
handleHousePointerUp(index){
    console.log('House ' + (index+1).toString() + ' up');
    app.setContainerAsTarget(session_players[index].houseContainer);
    app.showTransferModal(session_players[index].houseContainer);
},

handleHousePointerOver(index){
    console.log('House ' + (index+1).toString() + ' Over');
    app.setContainerAsTarget(session_players[index].houseContainer);
},

/**set specified container as trasnfer target target
*/
setContainerAsTarget(container)
{
    if(app.$data.pixi_transfer_line.visible)
    {
        if(container !=  app.$data.pixi_transfer_source)
        {
            app.$data.pixi_transfer_target = container;
            container.getChildByName("highlight").visible=true;
        }       
    }
},

/** show transfer modal when mouse up on valid target
*/
showTransferModal(container){
    if(!app.$data.pixi_transfer_line.visible ||
       container ==  app.$data.pixi_transfer_source ||
       app.$data.pixi_transfer_source == null ||
       app.$data.pixi_transfer_target == null)
    {
        app.turnOffHighlights();
        return;
    } 
},


handleHousePointerOut(index){
    console.log('House ' + (index+1).toString() + ' Out');

    if(session_players[index].houseContainer ==  app.$data.pixi_transfer_target)
    {
        app.$data.pixi_transfer_target = null;
        session_players[index].houseContainer.getChildByName("highlight").visible=false;
    }
},

/**
 *pointer up on stage
 */
 handleStagePointerUp(){
    console.log('Stage up: ' + event);
    app.turnOffHighlights();
},

turnOffHighlights(){
    for(let i=0;i<session_players.length;i++)
    {
        session_players[i].houseContainer.getChildByName("highlight").visible=false;
        session_players[i].fieldContainer.getChildByName("highlight").visible=false;
    }

    app.$data.pixi_transfer_line.visible=false;
},

/**
 * pointer move over stage
 */
handleStagePointerMove(){
    if(app.$data.pixi_transfer_line.visible)
    {
        app.updatePixiTransfer(event.offsetX, event.offsetY);
    }
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
    
    app.$data.working = true;
    app.sendMessage("move_goods", {"sessionID" : app.$data.sessionID,
                                   "formData" : $("#moveGoodsForm").serializeArray(),});
},

/** take result of moving goods
*/
takeMoveGoods(){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#moveGoodsModal').modal('hide');            
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

}