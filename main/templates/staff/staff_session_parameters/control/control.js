/** copy parameters from another period
*/
send_import_parameters(){
    
    if(!app.session_import) return;
    
    app.working = true;
    app.send_message("import_parameters", {"session_id" : app.session_id,
                                          "formData" : {session:app.session_import},});
},

/** show parameters copied from another period 
*/
take_import_parameters(){
    //app.cancel_modal=false;
    //app.clear_main_form_errors();

    if(message_data.status.status == "success")
    {
        app.take_get_session(message_data);       
        app.import_parameters_message = message_data.status.message;
        location.reload();    
    } 
    else
    {
        app.import_parameters_message = message_data.status.message;
    } 
},

/** show edit session modal
*/
show_import_parameters:function(){
    
   app.import_parameters_modal.show();
},

/** hide edit session modal
*/
hide_import_parameters:function(){
    
},

/** send request to download parameters to a file 
*/
send_download_parameters(){
    
    app.working = true;
    app.send_message("download_parameters", {"session_id" : app.session_id,});
},

/** download parameter set into a file 
 @param message_data {json} result of file request, either sucess or fail with errors
*/
take_download_parameters(message_data){

    if(message_data.status == "success")
    {                  
        console.log(message_data.parameter_set);

        var downloadLink = document.createElement("a");
        var jsonse = JSON.stringify(message_data.parameter_set);
        var blob = new Blob([jsonse], {type: "application/json"});
        var url = URL.createObjectURL(blob);
        downloadLink.href = url;
        downloadLink.download = "Exchange_Specialization_Session_" + app.session.id + "_Parameter_Set.json";

        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);                     
    } 

    app.working = false;
},

/**upload a parameter set file
*/
upload_parameterset:function(){  

    let formData = new FormData();
    formData.append('file', app.upload_file);

    axios.post('/staff-session/{{id}}/parameters', formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                    }
                } 
            )
            .then(function (response) {     

                app.upload_parameterset_messaage = response.data.message.message;
                app.session = response.data.session;
                app.upload_parameterset_button_text= 'Upload <i class="fas fa-upload"></i>';
                location.reload();

            })
            .catch(function (error) {
                console.log(error);
                app.searching=false;
            });                        
},

//direct upload button click
upload_action:function(){
    if(app.upload_file == null)
        return;

    app.upload_parameterset_messaage = "";
    app.upload_parameterset_button_text = '<i class="fas fa-spinner fa-spin"></i>';

    if(app.upload_mode == "parameters")
    {
        this.upload_parameterset();
    }
    else
    {
        
    }

},

//file upload
handle_file_upload:function(){
    app.upload_file = this.$refs.file.files[0];
    app.upload_file_name = app.upload_file.name;
},

/** show upload parameters modal
*/
show_upload_parameters:function(upload_mode){
    app.upload_mode = upload_mode;
    app.upload_parameterset_messaage = "";

    app.parameterSetModal.show();
},

/**hide upload parameters modal
*/
hide_upload_parameters:function(){
},