
/**show edit parameter set type
 */
 showEditParametersetType:function(index){
    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.parametersetTypeBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_types[index]);
    app.parametersetTypeBeforeEditIndex = index;
    app.current_parameterset_type = app.session.parameter_set.parameter_set_types[index];

    app.editParametersetTypeModal.show();
},

/** hide edit parmeter set type
*/
hideEditParametersetType:function(){
    if(app.cancel_modal)
    {
        Object.assign(app.session.parameter_set.parameter_set_types[app.parametersetTypeBeforeEditIndex], app.parametersetTypeBeforeEdit);
        app.parametersetTypeBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateParametersetType(){
    
    app.working = true;
    app.send_message("update_parameterset_type", {"session_id" : app.session_id,
                                                 "parameterset_type_id" : app.current_parameterset_type.id,
                                                 "formData" : app.current_parameterset_type,});
},

/** handle result of updating parameter set type
*/
takeUpdateParametersetType(message_data){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.editParametersetTypeModal.hide();         
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},

