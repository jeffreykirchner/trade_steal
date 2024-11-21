
/**show edit parameter set type
 */
 showEditParametersetType:function(index){
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetTypeBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_types[index]);
    app.parametersetTypeBeforeEditIndex = index;
    app.current_parameterset_type = app.session.parameter_set.parameter_set_types[index];

    app.editParametersetTypeModal.show();
},

/** hide edit parmeter set type
*/
hideEditParametersetType:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_types[app.parametersetTypeBeforeEditIndex], app.parametersetTypeBeforeEdit);
        app.parametersetTypeBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateParametersetType(){
    
    app.working = true;
    app.send_message("update_parameterset_type", {"sessionID" : app.sessionID,
                                                 "parameterset_type_id" : app.current_parameterset_type.id,
                                                 "formData" : app.current_parameterset_type,});
},

/** handle result of updating parameter set type
*/
takeUpdateParametersetType(message_data){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(message_data.status.value == "success")
    {
        app.take_get_Session(message_data);       
        app.editParametersetTypeModal.hide();         
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(message_data.status.errors);
    } 
},

