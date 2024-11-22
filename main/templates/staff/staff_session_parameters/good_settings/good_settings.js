/**show edit parameter set good
 */
 showEditParametersetGood:function(good_id, index){

    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.parametersetGoodBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_goods[index]);
    app.parametersetGoodEditIndex = index;
    app.parametersetGoodBeforeEditIndex = good_id;
    app.current_parameter_set_good = app.session.parameter_set.parameter_set_goods[index];

    app.editParametersetGoodModal.show();
},

/** hide edit parmeter set good
*/
hideEditParametersetGood:function(){
    if(app.cancel_modal)
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
    app.send_message("update_parameterset_good", {"session_id" : app.session_id,
                                                 "parameterset_good_id" : app.current_parameter_set_good.id,
                                                 "formData" : app.current_parameter_set_good,});
},

/** handle result of updating parameter set good
*/
takeUpdateParametersetGood(message_data){

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.editParametersetGoodModal.hide();       
        location.reload();    
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},