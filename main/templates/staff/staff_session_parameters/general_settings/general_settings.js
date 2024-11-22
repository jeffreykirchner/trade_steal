

/**show edit paramter set
 */
showEditParameterset:function(){
    app.clear_main_form_errors();
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

    app.send_message("update_parameterset", {"session_id" : app.session_id,
                                            "formData" : form_data,});
},

/** handle result of updating parameter set
*/
takeUpdateParameterset(message_data){
    //app.cancelModal=false;
    //app.clear_main_form_errors();

    app.cancelModal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_Session(message_data);       
        app.editParametersetModal.hide();           
    } 
    else
    {
        app.cancelModal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},

