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
        downloadLink.download = "Trade_Steal_Session_" + app.$data.session.id + "_Parameter_Set.json";

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
                //Vue.nextTick(app.update_sdgraph_canvas());

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

/**show edit paramter set
 */
showEditParameterset:function(){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.paramtersetBeforeEdit = Object.assign({}, app.$data.session.parameter_set);

    var myModal = new bootstrap.Modal(document.getElementById('editParametersetModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit session modal
*/
hideEditParameterset:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session.parameter_set, app.$data.paramtersetBeforeEdit);
        app.$data.paramtersetBeforeEdit=null;
    }
},

/** update parameterset settings
*/
sendUpdateParameterset(){
    
    app.$data.working = true;
    app.sendMessage("update_parameterset", {"sessionID" : app.$data.sessionID,
                                            "formData" : $("#parametersetForm").serializeArray(),});
},

/** handle result of updating parameter set
*/
takeUpdateParameterset(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#editParametersetModal').modal('hide');            
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/**show edit parameter set type
 */
 showEditParametersetType:function(index){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.parametersetTypeBeforeEdit = Object.assign({}, app.$data.session.parameter_set.parameter_set_types[index]);
    app.$data.parametersetTypeBeforeEditIndex = index;
    app.$data.current_parameterset_type = app.$data.session.parameter_set.parameter_set_types[index];

    var myModal = new bootstrap.Modal(document.getElementById('editParametersetTypeModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit parmeter set type
*/
hideEditParametersetType:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session.parameter_set.parameter_set_types[app.$data.parametersetTypeBeforeEditIndex], app.$data.parametersetTypeBeforeEdit);
        app.$data.parametersetTypeBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateParametersetType(){
    
    app.$data.working = true;
    app.sendMessage("update_parameterset_type", {"sessionID" : app.$data.sessionID,
                                                 "parameterset_type_id" : app.$data.current_parameterset_type.id,
                                                 "formData" : $("#parametersetTypeForm").serializeArray(),});
},

/** handle result of updating parameter set type
*/
takeUpdateParametersetType(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#editParametersetTypeModal').modal('hide');            
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/**show edit parameter set player
 */
 showEditParametersetPlayer:function(index){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.parametersetPlayerBeforeEdit = Object.assign({}, app.$data.session.parameter_set.parameter_set_players[index]);
    app.$data.parametersetPlayerBeforeEditIndex = index;
    app.$data.current_parameter_set_player = app.$data.session.parameter_set.parameter_set_players[index];

    var myModal = new bootstrap.Modal(document.getElementById('editParametersetPlayerModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetPlayer:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session.parameter_set.parameter_set_players[app.$data.parametersetPlayerBeforeEditIndex], app.$data.parametersetPlayerBeforeEdit);
        app.$data.parametersetPlayerBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateParametersetPlayer(){
    
    app.$data.working = true;
    app.sendMessage("update_parameterset_player", {"sessionID" : app.$data.sessionID,
                                                   "paramterset_player_id" : app.$data.current_parameter_set_player.id,
                                                   "formData" : $("#parametersetPlayerForm").serializeArray(),});
},

/** handle result of updating parameter set player
*/
takeUpdateParametersetPlayer(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#editParametersetPlayerModal').modal('hide');        
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/**show edit parameter set player group
 */
 showEditParametersetPlayerGroup:function(player_id, period_id){
    app.clearMainFormErrors();
    app.$data.cancelModal=true;
    app.$data.parametersetPlayerGroupBeforeEdit = Object.assign({}, app.$data.session.parameter_set.parameter_set_players[player_id].period_groups[period_id]);
    app.$data.parametersetPlayerBeforeEditIndex = player_id;
    app.$data.parametersetPlayerGroupBeforeEditIndex = period_id;
    app.$data.current_parameter_set_player_group = app.$data.session.parameter_set.parameter_set_players[player_id].period_groups[period_id];

    var myModal = new bootstrap.Modal(document.getElementById('editParametersetPlayerGroupModal'), {
        keyboard: false
        })

    myModal.toggle();
},

/** hide edit parmeter set player group
*/
hideEditParametersetPlayerGroup:function(){
    if(app.$data.cancelModal)
    {
        Object.assign(app.$data.session.parameter_set.parameter_set_players[app.$data.parametersetPlayerBeforeEditIndex].period_groups[app.$data.parametersetPlayerGroupBeforeEditIndex],
                      app.$data.parametersetPlayerGroupBeforeEdit);
        app.$data.parametersetPlayerBeforeEdit=null;
    }
},

/** update parameterset player group settings
*/
sendUpdateParametersetPlayerGroup(){
    
    app.$data.working = true;
    app.sendMessage("update_parameterset_player_group", {"sessionID" : app.$data.sessionID,
                                                   "paramterset_player_group_id" : app.$data.current_parameter_set_player_group.id,
                                                   "formData" : $("#parametersetPlayerGroupForm").serializeArray(),});
},

/** handle result of updating parameter set player group
*/
takeUpdateParametersetPlayerGroup(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        $('#editParametersetPlayerGroupModal').modal('hide');            
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** copy specified period's groups forward to future groups
*/
sendCopyGroupForward(period_number){
    app.$data.working = true;
    app.sendMessage("copy_group_forward", {"sessionID" : app.$data.sessionID,
                                           "period_number" : period_number,});
                                                   
},

/** handle result of copying groups forward
*/
takeCopyGroupForward(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();

    app.takeGetSession(messageData);   
},

/** copy specified period's groups forward to future groups
*/
sendRemoveParameterSetPlayer(){

    app.$data.working = true;
    app.sendMessage("remove_parameterset_player", {"sessionID" : app.$data.sessionID,
                                                   "paramterset_player_id" : app.$data.current_parameter_set_player.id,});
                                                   
},

/** handle result of copying groups forward
*/
takeRemoveParameterSetPlayer(messageData){
    app.$data.cancelModal=false;
    //app.clearMainFormErrors();
    app.takeGetSession(messageData);   
    $('#editParametersetPlayerModal').modal('hide');
},

/** copy specified period's groups forward to future groups
*/
sendAddParameterSetPlayer(player_id){
    app.$data.working = true;
    app.sendMessage("add_parameterset_player", {"sessionID" : app.$data.sessionID});
                                                   
},

/** handle result of copying groups forward
*/
takeAddParameterSetPlayer(messageData){
    //app.$data.cancelModal=false;
    //app.clearMainFormErrors();
    app.takeGetSession(messageData); 
},