/**
 *pointer down on field
 */
 handleFieldPointerDown(index){
    //console.log('Field ' + (index+1).toString() + ' down');
    app.handleContainerDown(session_players[index].fieldContainer);
},

/**
 *pointer up on field
 */
handleFieldPointerUp(index){
    //console.log('Field ' + (index+1).toString() + ' up');
    app.handleContainerUp(session_players[index].fieldContainer);
},

/**
 *pointer move over field
 */
handleFieldPointerOver(index){
    //console.log('Field ' + (index+1).toString() + ' Over');
    app.setContainerAsTarget(session_players[index].fieldContainer);
},

/**
 *pointer move off field
 */
handleFieldPointerOut(index){
    //console.log('Field ' + (index+1).toString() + ' Out');
    app.removeContainerTarget(session_players[index].fieldContainer);
},

/**
 *pointer down on house
 */
handleHousePointerDown(index){
    //console.log('House ' + (index+1).toString() + ' down');
    app.handleContainerDown(session_players[index].houseContainer);
},

/**
 *pointer up on house
 */
handleHousePointerUp(index){
   //console.log('House ' + (index+1).toString() + ' up');
    app.handleContainerUp(session_players[index].houseContainer);
},

/**
 *pointer over house
 */
handleHousePointerOver(index){
    //console.log('House ' + (index+1).toString() + ' Over');
    app.setContainerAsTarget(session_players[index].houseContainer);
},

/**
 *pointer move off house
 */
handleHousePointerOut(index){
    //console.log('House ' + (index+1).toString() + ' Out');
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

/**
 * turn off highlights around all containers
 */
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

/**
 * update transfer line
 */
updatePixiTransfer(target_x, target_y){
    transfer_line = app.$data.pixi_transfer_line;
    source = app.$data.pixi_transfer_source;

    transfer_line.clear();

    transfer_line.visible=true;
    transfer_line.lineStyle({width:10, color:0xF7DC6F, alpha:1, alignment:0.5, cap:PIXI.LINE_CAP.SQUARE});
    transfer_line.moveTo(target_x, target_y);
    transfer_line.lineTo(source.x, source.y);
},