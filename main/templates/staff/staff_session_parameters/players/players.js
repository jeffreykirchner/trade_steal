/**show edit parameter set player
 */
 show_edit_parameterset_player:function show_edit_parameterset_player(index){
    
    if(app.session.started) return;
    
    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.parameterset_player_before_edit = Object.assign({}, app.session.parameter_set.parameter_set_players[index]);
    app.parameterset_player_before_edit.good_one =  Object.assign({}, app.session.parameter_set.parameter_set_players[index].good_one);
    app.parameterset_player_before_edit.good_two =  Object.assign({}, app.session.parameter_set.parameter_set_players[index].good_two);
    app.parameterset_player_before_edit.good_three =  Object.assign({}, app.session.parameter_set.parameter_set_players[index].good_three);
    app.parameterset_player_before_edit.parameter_set_type =  Object.assign({}, app.session.parameter_set.parameter_set_players[index].parameter_set_type);
    app.parameterset_player_before_edit.avatar =  Object.assign({}, app.session.parameter_set.parameter_set_players[index].avatar);

    app.parameterset_player_before_edit_index = index;
    app.current_parameter_set_player = app.session.parameter_set.parameter_set_players[index];
    

    app.edit_parameterset_player_modal.show()
},

/** hide edit parmeter set player
*/
hide_edit_parameterset_player:function hide_edit_parameterset_player(){
    if(app.cancel_modal)
    {
        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index], app.parameterset_player_before_edit);

        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index].good_one, app.parameterset_player_before_edit.good_one);
        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index].good_two, app.parameterset_player_before_edit.good_two);
        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index].good_three, app.parameterset_player_before_edit.good_three);
        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index].parameter_set_type, app.parameterset_player_before_edit.parameter_set_type);
        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index].avatar, app.parameterset_player_before_edit.avatar);

        app.parameterset_player_before_edit=null;
    }
},

/** update parameterset type settings
*/
send_update_parameterset_player: function send_update_parameterset_player(){
    
    app.working = true;

    app.send_message("update_parameterset_player", {"session_id" : app.session_id,
                                                   "paramterset_player_id" : app.current_parameter_set_player.id,
                                                   "formData" : app.current_parameter_set_player,});
},

/** handle result of updating parameter set player
*/
take_update_parameterset_player: function take_update_parameterset_player(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.edit_parameterset_player_modal.hide();     
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},

/**show edit parameter set player group
 */
 show_edit_parameterset_player_group:function show_edit_parameterset_player_group(player_id, period_id){
     
    if(app.session.started) return;

    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.parameterset_player_group_before_edit = Object.assign({}, app.session.parameter_set.parameter_set_players[player_id].period_groups[period_id]);
    app.parameterset_player_before_edit_index = player_id;
    app.parameterset_player_group_before_edit_index = period_id;
    app.current_parameter_set_player_group = app.session.parameter_set.parameter_set_players[player_id].period_groups[period_id];

    app.edit_parameterset_player_group_modal.show();
},

/** hide edit parmeter set player group
*/
hide_edit_parameterset_player_group:function hide_edit_parameterset_player_group(){
    if(app.cancel_modal)
    {
        Object.assign(app.session.parameter_set.parameter_set_players[app.parameterset_player_before_edit_index].period_groups[app.parameterset_player_group_before_edit_index],
                      app.parameterset_player_group_before_edit);
        app.parameterset_player_before_edit=null;
    }
},

/** update parameterset player group settings
*/
send_update_parameterset_player_group: function send_update_parameterset_player_group(){
    
    app.working = true;
    app.send_message("update_parameterset_player_group", {"session_id" : app.session_id,
                                                   "paramterset_player_group_id" : app.current_parameter_set_player_group.id,
                                                   "formData" : app.current_parameter_set_player_group,});
},

/** handle result of updating parameter set player group
*/
take_update_parameterset_player_group: function take_update_parameterset_player_group(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.edit_parameterset_player_group_modal.hide();            
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},

/** copy specified period's groups forward to future groups
*/
send_copy_group_forward: function send_copy_group_forward(period_number){
    app.working = true;
    app.send_message("copy_group_forward", {"session_id" : app.session_id,
                                           "period_number" : period_number,});
                                                   
},

/** handle result of copying groups forward
*/
take_copy_group_forward: function take_copy_group_forward(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.take_get_session(message_data);   
},

/** copy specified period's groups forward to future groups
*/
send_remove_parameterset_player: function send_remove_parameterset_player(){

    app.working = true;
    app.send_message("remove_parameterset_player", {"session_id" : app.session_id,
                                                   "paramterset_player_id" : app.current_parameter_set_player.id,});
                                                   
},

/** handle result of copying groups forward
*/
take_remove_parameterset_player: function take_remove_parameterset_player(message_data){
    app.cancel_modal=false;
    //app.clear_main_form_errors();
    app.take_get_session(message_data);   
    app.edit_parameterset_player_modal.hide();
},

/** copy specified period's groups forward to future groups
*/
send_add_parameterset_player: function send_add_parameterset_player(player_id){
    app.working = true;
    app.send_message("add_parameterset_player", {"session_id" : app.session_id});
                                                   
},

/** handle result of copying groups forward
*/
take_add_parameterset_player: function take_add_parameterset_player(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();
    app.take_get_session(message_data); 
},
