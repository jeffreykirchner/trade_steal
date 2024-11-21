

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

    app.sendMessage("update_parameterset", {"sessionID" : app.sessionID,
                                            "formData" : form_data,});
},

/** handle result of updating parameter set
*/
takeUpdateParameterset(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.take_get_Session(messageData);       
        app.editParametersetModal.hide();           
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

