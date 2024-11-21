/**show edit parameter set good
 */
 showEditParametersetGood:function(good_id, index){

    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetGoodBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_goods[index]);
    app.parametersetGoodEditIndex = index;
    app.parametersetGoodBeforeEditIndex = good_id;
    app.current_parameter_set_good = app.session.parameter_set.parameter_set_goods[index];

    app.editParametersetGoodModal.show();
},

/** hide edit parmeter set good
*/
hideEditParametersetGood:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_goods[app.parametersetPlayerBeforeEditIndex],
                      app.parametersetGoodBeforeEdit);
        app.parametersetGoodBeforeEdit=null;
    }
},

/** update parameterset good settings
*/
sendUpdateParametersetGood(){
    
    app.working = true;
    app.send_message("update_parameterset_good", {"sessionID" : app.sessionID,
                                                 "parameterset_good_id" : app.current_parameter_set_good.id,
                                                 "formData" : app.current_parameter_set_good,});
},

/** handle result of updating parameter set good
*/
takeUpdateParametersetGood(message_data){

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(message_data.status.value == "success")
    {
        app.take_get_Session(message_data);       
        app.editParametersetGoodModal.hide();       
        location.reload();    
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(message_data.status.errors);
    } 
},