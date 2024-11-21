
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
    app.sendMessage("update_parameterset_type", {"sessionID" : app.sessionID,
                                                 "parameterset_type_id" : app.current_parameterset_type.id,
                                                 "formData" : app.current_parameterset_type,});
},

/** handle result of updating parameter set type
*/
takeUpdateParametersetType(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.take_get_Session(messageData);       
        app.editParametersetTypeModal.hide();         
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

