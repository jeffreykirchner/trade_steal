

/**show edit paramter set
 */
show_edit_parameterset:function show_edit_parameterset(){
    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.paramterset_before_edit = Object.assign({}, app.session.parameter_set);

    app.edit_parameterset_modal.show();
},

/** hide edit session modal
*/
hide_edit_parameterset:function hide_edit_parameterset(){
    if(app.cancel_modal)
    {
        Object.assign(app.session.parameter_set, app.paramterset_before_edit);
        app.paramterset_before_edit=null;
    }
},

/** update parameterset settings
*/
send_update_parameterset: function send_update_parameterset(){
    
    app.working = true;

    let form_data = {}

    for(i=0;i<app.parameterset_form_ids.length;i++)
    {
        v=app.parameterset_form_ids[i];
        form_data[v]=app.session.parameter_set[v];
    }

    app.send_message("update_parameterset", {"session_id" : app.session_id,
                                            "formData" : form_data,});
},

/** handle result of updating parameter set
*/
take_update_parameterset: function take_update_parameterset(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.edit_parameterset_modal.hide();           
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},

