/**show edit paramter set avatar
 */
 show_edit_parameterset_avatar: function show_edit_parameterset_avatar(index){
    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.paramterset_avatar_before_edit = Object.assign({}, app.session.parameter_set.parameter_set_avatars[index]);
    app.paramterset_avatar_before_edit_avatar = Object.assign({}, app.session.parameter_set.parameter_set_avatars[index].avatar);
    app.paramterset_avatar_before_edit_index = index;
    app.current_parameter_set_avatar = Object.assign({}, app.session.parameter_set.parameter_set_avatars[index]);

    if(!app.current_parameter_set_avatar.avatar)
    {
        app.current_parameter_set_avatar.avatar = {id:-1}
    }

    app.edit_avatars_modal.show();
},

/** hide edit session modal
*/
hide_edit_parameterset_avatar: function hide_edit_parameterset_avatar(){
    if(app.cancel_modal)
    {
       // Object.assign(app.session.parameter_set.parameter_set_avatars[app.paramterset_avatar_before_edit_index], app.paramterset_avatar_before_edit);

        // if(app.current_parameter_set_avatar.avatar)
        //     if(app.current_parameter_set_avatar.avatar.id == -1)
        //         app.session.parameter_set.parameter_set_avatars[app.paramterset_avatar_before_edit_index].avatar = null;
    }
},

/** update parameterset avatar 
*/
send_update_parameterset_avatar: function send_update_parameterset_avatar(){
    
    app.working = true;

    app.send_message("update_parameterset_avatar", {"session_id" : app.session_id,
                                                   "parameterset_avatar_id" : app.session.parameter_set.parameter_set_avatars[app.paramterset_avatar_before_edit_index].id,
                                                   "formData" : {"avatar" : app.current_parameter_set_avatar.avatar.id}});
},

/** handle result of updating parameter set
*/
take_update_parameterset_avatar: function take_update_parameterset_avatar(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.session.parameter_set = message_data.status.result;
        app.edit_avatars_modal.hide();           
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},