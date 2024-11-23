
/**show edit parameter set type
 */
 show_edit_parameterset_type:function show_edit_parameterset_type(index){
    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.parameterset_type_before_edit = Object.assign({}, app.session.parameter_set.parameter_set_types[index]);
    app.parameterset_type_before_edit_index = index;
    app.current_parameterset_type = app.session.parameter_set.parameter_set_types[index];

    app.edit_tarameterset_type_modal.show();
},

/** hide edit parmeter set type
*/
hide_edit_parameterset_type:function hide_edit_parameterset_type(){
    if(app.cancel_modal)
    {
        Object.assign(app.session.parameter_set.parameter_set_types[app.parameterset_type_before_edit_index], app.parameterset_type_before_edit);
        app.parameterset_type_before_edit=null;
    }
},

/** update parameterset type settings
*/
send_update_parameterset_type: function send_update_parameterset_type(){
    
    app.working = true;
    app.send_message("update_parameterset_type", {"session_id" : app.session_id,
                                                 "parameterset_type_id" : app.current_parameterset_type.id,
                                                 "formData" : app.current_parameterset_type,});
},

/** handle result of updating parameter set type
*/
take_update_parameterset_type: function take_update_parameterset_type(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.edit_tarameterset_type_modal.hide();         
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},

