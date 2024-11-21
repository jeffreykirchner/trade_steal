

/**show edit paramter set
 */
showEditParameterset:function(){
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.paramtersetBeforeEdit = Object.assign({}, app.session.parameter_set);

    app.editParametersetModal.show();
},

/** hide edit session modal
*/
hideEditParameterset:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set, app.paramtersetBeforeEdit);
        app.paramtersetBeforeEdit=null;
    }
},

/** update parameterset settings
*/
sendUpdateParameterset(){
    
    app.working = true;

    let form_data = {}

    for(i=0;i<app.parameterset_form_ids.length;i++)
    {
        v=app.parameterset_form_ids[i];
        form_data[v]=app.session.parameter_set[v];
    }

    app.send_message("update_parameterset", {"sessionID" : app.sessionID,
                                            "formData" : form_data,});
},

/** handle result of updating parameter set
*/
takeUpdateParameterset(message_data){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(message_data.status.value == "success")
    {
        app.take_get_Session(message_data);       
        app.editParametersetModal.hide();           
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(message_data.status.errors);
    } 
},

