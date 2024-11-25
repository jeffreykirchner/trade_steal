/**
 *pointer down on field
 */
 handle_field_pointer_down: function handle_field_pointer_down(index, event){
    //console.log('Field ' + (index+1).toString() + ' down');
    app.handle_container_down(field_containers[index], event);
},

/**
 *pointer up on field
 */
handle_field_pointer_up: function handle_field_pointer_up(index, event){
    //console.log('Field ' + (index+1).toString() + ' up');
    if(app.session.parameter_set.allow_stealing == "False")
    {
        app.turn_off_highlights();
        return;
    }
    app.handle_container_up(field_containers[index], event);
},

/**
 *pointer move over field
 */
handle_field_pointer_over: function handle_field_pointer_over(index, event){
    //console.log('Field ' + (index+1).toString() + ' Over');
    app.set_container_as_target(field_containers[index], event);
},

handle_field_pointer_move: function handle_field_pointer_move(index, event){
    //console.log('House ' + (index+1).toString() + ' move');
    app.handle_stage_pointer_move(event);
},

/**
 *pointer move off field
 */
handle_field_pointer_out: function handle_field_pointer_out(index, event){
    //console.log('Field ' + (index+1).toString() + ' Out');
    app.remove_container_target(field_containers[index], event);
},

/**
 *pointer down on house
 */
handle_house_pointer_down: function handle_house_pointer_down(index, event){
    //console.log('House ' + (index+1).toString() + ' down');
    app.handle_container_down(house_containers[index], event);
},

/**
 *pointer up on house
 */
handle_house_pointer_up: function handle_house_pointer_up(index, event){
   //console.log('House ' + (index+1).toString() + ' up');
   app.handle_container_up(house_containers[index], event);
},

/**
 *pointer over house
 */
handle_house_pointer_over: function handle_house_pointer_over(index, event){
    //console.log('House ' + (index+1).toString() + ' Over');
    app.set_container_as_target(house_containers[index], event);
},

handle_house_pointer_move: function handle_house_pointer_move(index, event){
    //console.log('House ' + (index+1).toString() + ' move');
    app.handle_stage_pointer_move(event);
},

/**
 *pointer move off house
 */
handle_house_pointer_out: function handle_house_pointer_out(index, event){
    //console.log('House ' + (index+1).toString() + ' Out');
    app.remove_container_target(house_containers[index], event);
},

/**
 * handle container mouse down
 */
handle_container_down: function handle_container_down(container, event){
    app.turn_off_highlights();

    if(app.session.finished) return;

    container.getChildByName("highlight").visible=true;
    pixi_transfer_source = container;
    app.update_pixi_transfer(event.data.global.x , event.data.global.y);
    app.transfer_in_progress = true;
},

/**
 * handle container mouse up
 */
handle_container_up: function handle_container_up(container, event){
    if(app.session.finished) return;
        
    app.set_container_as_target(container, event);
    app.show_transfer_modal(container, event);
},

/**set specified container as trasnfer target target
*/
set_container_as_target: function set_container_as_target(container, event)
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
remove_container_target: function remove_container_target(container, event){
    if(container ==  pixi_transfer_target && !app.pixi_modal_open)
    {
        pixi_transfer_target = null;
        container.getChildByName("highlight").visible=false;
    }
},

/**
 *pointer up on stage
 */
 handle_stage_pointer_up: function handle_stage_pointer_up(event){
    //console.log('Stage up: ' + event);
    app.turn_off_highlights();
},

/**
 * pointer move over stage
 */
handle_stage_pointer_move: function handle_stage_pointer_move(event){
    if(pixi_transfer_line.visible && !app.pixi_modal_open)
    {
        //console.log('stage move over: ' + event.data.global.x + ' ' + event.data.global.y);
        app.update_pixi_transfer(event.data.global.x, event.data.global.y);
    }
},

/**
 * turn off highlights around all containers
 */
turn_off_highlights: function turn_off_highlights(){
    if(app.pixi_modal_open) return;

    
    for(let i=0;i<app.session.session_players_order.length;i++)
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
update_pixi_transfer: function update_pixi_transfer(target_x, target_y){
    transfer_line = pixi_transfer_line;
    source = pixi_transfer_source;

    try {
        transfer_line.clear();

        transfer_line.visible=true;
        transfer_line.lineStyle({width:10, color:0xF7DC6F, alpha:1, alignment:0.5, cap:PIXI.LINE_CAP.SQUARE});
        transfer_line.moveTo(target_x, target_y);
        transfer_line.lineTo(source.x, source.y);
      } catch (error) {
        transfer_line.clear();
        transfer_line.visible=false;
        app.turn_off_highlights();
      }    
},