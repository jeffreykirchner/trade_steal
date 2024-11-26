/**show edit parameter set good
 */
 show_edit_parameterset_good:function show_edit_parameterset_good(good_id, index){

    app.clear_main_form_errors();
    app.cancel_modal=true;
    app.parameterset_good_before_edit = Object.assign({}, app.session.parameter_set.parameter_set_goods[index]);
    app.parameterset_good_edit_index = index;
    app.parameterset_good_before_edit_index = good_id;
    app.current_parameter_set_good = app.session.parameter_set.parameter_set_goods[index];

    app.edit_parameterset_good_modal.show();
},

/** hide edit parmeter set good
*/
hide_edit_parametersetGood:function hide_edit_parametersetGood(){
    if(app.cancel_modal)
    {
        Object.assign(app.session.parameter_set.parameter_set_goods[app.parameterset_good_edit_index],
                      app.parameterset_good_before_edit);
        app.parameterset_good_before_edit=null;
    }
},

/** update parameterset good settings
*/
send_update_parameterset_good: function send_update_parameterset_good(){
    
    app.working = true;
    app.send_message("update_parameterset_good", {"session_id" : app.session_id,
                                                 "parameterset_good_id" : app.current_parameter_set_good.id,
                                                 "formData" : app.current_parameter_set_good,});
},

/** handle result of updating parameter set good
*/
take_update_parameterset_good: function take_update_parameterset_good(message_data){

    app.cancel_modal=false;
    app.clear_main_form_errors();

    if(message_data.status.value == "success")
    {
        app.take_get_session(message_data);       
        app.edit_parameterset_good_modal.hide();       
        location.reload();    
    } 
    else
    {
        app.cancel_modal=true;                           
        app.display_errors(message_data.status.errors);
    } 
},