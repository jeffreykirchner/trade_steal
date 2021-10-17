/** send update to number of buyers or sellers 
 * @param type : BUYER or SELLER
 * @param adjustment : 1 or -1
*/
sendUpdateSubjectCount(type, adjustment){
    app.$data.cancelModal = false;
    app.$data.working = true;
    app.sendMessage("update_subject_count", {"sessionID" : app.$data.sessionID,
                                                "current_visible_period" : app.$data.current_visible_period,
                                                "type" : type,
                                                "adjustment" : adjustment});
},

/** send update to number of periods
 * @param adjustment : 1 or -1
*/
sendUpdatePeriodCount(adjustment){
    app.$data.cancelModal = false;
    app.$data.working = true;
    app.sendMessage("update_period_count", {"sessionID" : app.$data.sessionID,
                                            "adjustment" : adjustment});
},

/** send update to number of periods
*/
sendUpdateValuecost(){
    
    app.$data.working = true;
    app.sendMessage("update_valuecost", {"sessionID" : app.$data.sessionID,
                                         "id" : app.$data.current_valuecost.id,
                                         "formData" : $("#valuecostForm").serializeArray(),});
},

/** take update valuecost
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdateValuecost(messageData){
    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#valuecostModal').modal('hide');    
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** update the current visible period
 * @param adjustment : 1 or -1
*/
updateCurrentPeriod(adjustment){
    
    if(adjustment == 1)
    {
        if(app.$data.current_visible_period < app.$data.session.parameter_set.number_of_periods)
        {
            app.$data.current_visible_period += 1;
        }
    }
    else
    {
        if(app.$data.current_visible_period > 1)
        {
            app.$data.current_visible_period -= 1;
        }
    }

    Vue.nextTick(app.update_sdgraph_canvas());

},

/** shift the values or costs in the current period from one buyer or seller to the next
 * @param valueOrCost : 'value' or 'cost'
 * @param valueOrCost : 'up' or 'down'
*/
shiftValueOrCost(valueOrCost, direction){
    app.$data.working = true;
    app.sendMessage("shift_value_or_cost", {"sessionID" : app.$data.sessionID,
                                            "currentPeriod" : app.$data.current_visible_period,
                                            "valueOrCost" : valueOrCost,
                                            "direction" : direction,});
},

/** shift the values or costs in the current period from one buyer or seller to the next
 * @param valueOrCost : 'value' or 'cost'
 * @param valueOrCost : 'up' or 'down'
*/
addToValueOrCost(valueOrCost){
    app.$data.working = true;
    amount = 0;
    if (valueOrCost == 'value')
        amount = app.$data.add_to_value_amount;
    else
        amount = app.$data.add_to_cost_amount;

    app.sendMessage("add_to_all_values_or_costs", {"sessionID" : app.$data.sessionID,
                                            "currentPeriod" : app.$data.current_visible_period,
                                            "valueOrCost" : valueOrCost,
                                            "amount" : amount,});
},

/** copy values or costs from pervious period
 * @param valueOrCost : 'value' or 'cost'
 * @param valueOrCost : 'up' or 'down'
*/
    copyValueOrCost(valueOrCost){
    app.$data.working = true;
    app.sendMessage("copy_value_or_cost", {"sessionID" : app.$data.sessionID,
                                            "currentPeriod" : app.$data.current_visible_period,
                                            "valueOrCost" : valueOrCost});
},

/** send update to number of periods
*/
sendUpdatePeriod(){
    
    app.$data.working = true;
    app.sendMessage("update_period", {"sessionID" : app.$data.sessionID,
                                      "periodID" : app.$data.session.parameter_set.periods[app.$data.current_visible_period-1].id,
                                      "formData" : $("#periodForm").serializeArray(),});
},

/** take update period
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeUpdatePeriod(messageData){
    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#editPeriodModal').modal('hide');    
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** copy parameters from another period
*/
sendImportParameters(){
    
    app.$data.working = true;
    app.sendMessage("import_parameters", {"sessionID" : app.$data.sessionID,
                                            "formData" : $("#importParametersForm").serializeArray(),});
},

/** show parameters copied from another period 
*/
takeImportParameters(){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    if(messageData.status.status == "success")
    {
        app.$data.current_visible_period = 1;
        app.takeGetSession(messageData);       
        app.$data.import_parameters_message = messageData.status.message;
        //$('#importParametersModal').modal('hide');    
    } 
    else
    {
        app.$data.import_parameters_message = messageData.status.message;
    } 
},

/** send request to download parameters to a file 
*/
sendDownloadParameters(){
    
    app.$data.working = true;
    app.sendMessage("download_parameters", {"sessionID" : app.$data.sessionID,});
},

/** download parameter set into a file 
 @param messageData {json} result of file request, either sucess or fail with errors
*/
takeDownloadParameters(messageData){

    if(messageData.status == "success")
    {                  
        console.log(messageData.parameter_set);

        var downloadLink = document.createElement("a");
        var jsonse = JSON.stringify(messageData.parameter_set);
        var blob = new Blob([jsonse], {type: "application/json"});
        var url = URL.createObjectURL(blob);
        downloadLink.href = url;
        downloadLink.download = "Double_Auction_Session_" + app.$data.session.id + "_Parameter_Set.json";

        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);                     
    } 

    app.$data.working = false;
},

/**upload a parameter set file
*/
uploadParameterset:function(){  

    let formData = new FormData();
    formData.append('file', app.$data.upload_file);

    axios.post('/staff-session/{{id}}/', formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                    }
                } 
            )
            .then(function (response) {     

                app.$data.uploadParametersetMessaage = response.data.message.message;
                app.$data.session = response.data.session;
                app.$data.uploadParametersetButtonText= 'Upload <i class="fas fa-upload"></i>';
                Vue.nextTick(app.update_sdgraph_canvas());

            })
            .catch(function (error) {
                console.log(error);
                app.$data.searching=false;
            });                        
},

//direct upload button click
uploadAction:function(){
    if(app.$data.upload_file == null)
        return;

    app.$data.uploadParametersetMessaage = "";
    app.$data.uploadParametersetButtonText = '<i class="fas fa-spinner fa-spin"></i>';

    if(app.$data.upload_mode == "parameters")
    {
        this.uploadParameterset();
    }
    else
    {
        
    }

},

handleFileUpload:function(){
    app.$data.upload_file = this.$refs.file.files[0];
    app.$data.upload_file_name = app.$data.upload_file.name;
},

/** show upload parameters modal
*/
showUploadParameters:function(upload_mode){
    app.$data.upload_mode = upload_mode;
    app.$data.uploadParametersetMessaage = "";

    var myModal = new bootstrap.Modal(document.getElementById('parameterSetModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/**hide upload parameters modal
*/
hideUploadParameters:function(){
},

/** show edit valuecost modal
*/
showEditValuecost:function(value_cost, type){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.sessionBeforeEdit = Object.assign({}, app.$data.session);

    app.$data.current_valuecost = Object.assign({}, value_cost);

    if(type == "value")
    {
        app.$data.valuecost_modal_label = "Edit value";
    }
    else
    {
        app.$data.valuecost_modal_label = "Edit cost";
    }


    var myModal = new bootstrap.Modal(document.getElementById('valuecostModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit valuecost modal
*/
hideEditValuecost:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session, app.$data.sessionBeforeEdit);
        app.$data.sessionBeforeEdit=null;
    }
},

/** show edit session modal
*/
showEditSession:function(){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.sessionBeforeEdit = Object.assign({}, app.$data.session);

    
    var myModal = new bootstrap.Modal(document.getElementById('editSessionModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit session modal
*/
hideEditSession:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session, app.$data.sessionBeforeEdit);
        app.$data.sessionBeforeEdit=null;
    }
},

/** show edit session modal
*/
showEditPeriod:function(){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.periodBeforeEdit = Object.assign({}, app.$data.session.parameter_set.periods[app.$data.current_visible_period-1]);

    var myModal = new bootstrap.Modal(document.getElementById('editPeriodModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit session modal
*/
hideEditPeriod:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session.parameter_set.periods[app.$data.current_visible_period-1], app.$data.periodBeforeEdit);
        app.$data.periodBeforeEdit=null;
    }
},

/** show edit session modal
*/
showImportParameters:function(){
    
    var myModal = new bootstrap.Modal(document.getElementById('importParametersModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit session modal
*/
hideImportParameters:function(){
    
},
        
       

  