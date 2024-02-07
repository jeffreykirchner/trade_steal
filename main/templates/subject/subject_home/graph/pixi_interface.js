/**
 *pointer down on field
 */
 handleFieldPointerDown(index, event){
    //console.log('Field ' + (index+1).toString() + ' down');
    let session_players = app.session.session_players;
    app.handleContainerDown(field_containers[index], event);
},

/**
 *pointer up on field
 */
handleFieldPointerUp(index, event){
    //console.log('Field ' + (index+1).toString() + ' up');
    if(app.session.parameter_set.allow_stealing == "False")
    {
        app.turnOffHighlights();
        return;
    }

    let session_players = app.session.session_players;
    app.handleContainerUp(field_containers[index], event);
},

/**
 *pointer move over field
 */
handleFieldPointerOver(index, event){
    //console.log('Field ' + (index+1).toString() + ' Over');
    let session_players = app.session.session_players;
    app.setContainerAsTarget(field_containers[index], event);
},

handleFieldPointerMove(index, event){
    //console.log('House ' + (index+1).toString() + ' move');
    app.handleStagePointerMove(event);
},

/**
 *pointer move off field
 */
handleFieldPointerOut(index, event){
    //console.log('Field ' + (index+1).toString() + ' Out');
    let session_players = app.session.session_players;
    app.removeContainerTarget(field_containers[index], event);
},

/**
 *pointer down on house
 */
handleHousePointerDown(index, event){
    //console.log('House ' + (index+1).toString() + ' down');
    let session_players = app.session.session_players;
    app.handleContainerDown(house_containers[index], event);
},

/**
 *pointer up on house
 */
handleHousePointerUp(index, event){
   //console.log('House ' + (index+1).toString() + ' up');
   let session_players = app.session.session_players;
   app.handleContainerUp(house_containers[index], event);
},

/**
 *pointer over house
 */
handleHousePointerOver(index, event){
    //console.log('House ' + (index+1).toString() + ' Over');
    let session_players = app.session.session_players;
    app.setContainerAsTarget(house_containers[index], event);
   
},

handleHousePointerMove(index, event){
    //console.log('House ' + (index+1).toString() + ' move');
    app.handleStagePointerMove(event);
},

/**
 *pointer move off house
 */
handleHousePointerOut(index, event){
    //console.log('House ' + (index+1).toString() + ' Out');
    let session_players = app.session.session_players;
    app.removeContainerTarget(house_containers[index], event);
},

/**
 * handle container mouse down
 */
handleContainerDown(container, event){
    app.turnOffHighlights();

    if(app.session.finished) return;

    container.getChildByName("highlight").visible=true;
    pixi_transfer_source = container;
    app.updatePixiTransfer(event.data.global.x , event.data.global.y);
    app.transfer_in_progress = true;
},

/**
 * handle container mouse up
 */
handleContainerUp(container, event){
    if(app.session.finished) return;
        
    app.setContainerAsTarget(container, event);
    app.showTransferModal(container, event);
},

/**set specified container as trasnfer target target
*/
setContainerAsTarget(container, event)
{
    if(pixi_transfer_line.visible && !app.pixi_modal_open)
    {
        if(container !=  pixi_transfer_source)
        {
            pixi_transfer_target = container;
            container.getChildByName("highlight").visible=true;
        }       
    }
},

/**remove container target when pointer moves off of it
*/
removeContainerTarget(container, event){
    if(container ==  pixi_transfer_target && !app.pixi_modal_open)
    {
        pixi_transfer_target = null;
        container.getChildByName("highlight").visible=false;
    }
},

/**
 *pointer up on stage
 */
 handleStagePointerUp(event){
    //console.log('Stage up: ' + event);
    app.turnOffHighlights();
},

/**
 * pointer move over stage
 */
handleStagePointerMove(event){
    if(pixi_transfer_line.visible && !app.pixi_modal_open)
    {
        //console.log('stage move over: ' + event.data.global.x + ' ' + event.data.global.y);
        app.updatePixiTransfer(event.data.global.x, event.data.global.y);
    }
},

/**
 * turn off highlights around all containers
 */
turnOffHighlights(){
    if(app.pixi_modal_open) return;

    let session_players = app.session.session_players;
    
    for(let i=0;i<session_players.length;i++)
    {
        if(house_containers[i])
            if(house_containers[i].getChildByName("highlight"))
                house_containers[i].getChildByName("highlight").visible=false;

        if(field_containers[i])
            if(field_containers[i].getChildByName("highlight"))
                field_containers[i].getChildByName("highlight").visible=false;
    }

    pixi_transfer_line.visible=false;
    app.transfer_in_progress = false;
},

/**
 * update transfer line
 */
updatePixiTransfer(target_x, target_y){
    transfer_line = pixi_transfer_line;
    source = pixi_transfer_source;

    if(!source.x) return;
    if(!source.y) return;
    if(!transfer_line) return;
    if(!target_x) return;
    if(!target_y) return;

    transfer_line.clear();

    transfer_line.visible=true;
    transfer_line.lineStyle({width:10, color:0xF7DC6F, alpha:1, alignment:0.5, cap:PIXI.LINE_CAP.SQUARE});
    transfer_line.moveTo(target_x, target_y);
    transfer_line.lineTo(source.x, source.y);
},