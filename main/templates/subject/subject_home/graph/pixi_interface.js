/**
 *pointer down on field
 */
 handleFieldPointerDown(index, event){
    //console.log('Field ' + (index+1).toString() + ' down');
    let session_players = app.$data.session.session_players;
    app.handleContainerDown(session_players[index].fieldContainer, event);
},

/**
 *pointer up on field
 */
handleFieldPointerUp(index, event){
    //console.log('Field ' + (index+1).toString() + ' up');
    if(app.$data.session.parameter_set.allow_stealing == "False")
    {
        app.turnOffHighlights();
        return;
    }

    let session_players = app.$data.session.session_players;
    app.handleContainerUp(session_players[index].fieldContainer, event);
},

/**
 *pointer move over field
 */
handleFieldPointerOver(index, event){
    //console.log('Field ' + (index+1).toString() + ' Over');
    let session_players = app.$data.session.session_players;
    app.setContainerAsTarget(session_players[index].fieldContainer, event);
},

/**
 *pointer move off field
 */
handleFieldPointerOut(index, event){
    //console.log('Field ' + (index+1).toString() + ' Out');
    let session_players = app.$data.session.session_players;
    app.removeContainerTarget(session_players[index].fieldContainer, event);
},

/**
 *pointer down on house
 */
handleHousePointerDown(index, event){
    //console.log('House ' + (index+1).toString() + ' down');
    let session_players = app.$data.session.session_players;
    app.handleContainerDown(session_players[index].houseContainer, event);
},

/**
 *pointer up on house
 */
handleHousePointerUp(index, event){
   //console.log('House ' + (index+1).toString() + ' up');
   let session_players = app.$data.session.session_players;
   app.handleContainerUp(session_players[index].houseContainer, event);
},

/**
 *pointer over house
 */
handleHousePointerOver(index, event){
    //console.log('House ' + (index+1).toString() + ' Over');
    let session_players = app.$data.session.session_players;
    app.setContainerAsTarget(session_players[index].houseContainer, event);
},

/**
 *pointer move off house
 */
handleHousePointerOut(index, event){
    //console.log('House ' + (index+1).toString() + ' Out');
    let session_players = app.$data.session.session_players;
    app.removeContainerTarget(session_players[index].houseContainer, event);
},

/**
 * handle container mouse down
 */
handleContainerDown(container, event){
    app.turnOffHighlights();

    container.getChildByName("highlight").visible=true;
    app.$data.pixi_transfer_source = container;
    app.updatePixiTransfer(event.data.global.x , event.data.global.y);
},

/**
 * handle container mouse up
 */
handleContainerUp(container, event){
    app.setContainerAsTarget(container, event);
    app.showTransferModal(container, event);
},

/**set specified container as trasnfer target target
*/
setContainerAsTarget(container, event)
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
removeContainerTarget(container, event){
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
    //console.log('Stage up: ' + event);
    app.turnOffHighlights();
},

/**
 * pointer move over stage
 */
 handleStagePointerMove(event){
    if(app.$data.pixi_transfer_line.visible && !app.pixi_modal_open)
    {
        app.updatePixiTransfer(event.data.global.x, event.data.global.y);
    }
},

/**
 * turn off highlights around all containers
 */
turnOffHighlights(){
    if(app.pixi_modal_open) return;

    let session_players = app.$data.session.session_players;
    
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