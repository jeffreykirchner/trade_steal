/** copy parameters from another period
*/
sendImportParameters(){
    
    app.working = true;
    app.send_message("import_parameters", {"session_id" : app.session_id,
                                          "formData" : {session:app.session_import},});
},

/** show parameters copied from another period 
*/
takeImportParameters(){
    //app.cancelModal=false;
    //app.clear_main_form_errors();

    if(message_data.status.status == "success")
    {
        app.take_get_Session(message_data);       
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
showImportParameters:function(){
    
   app.importParametersModal.show();
},

/** hide edit session modal
*/
hideImportParameters:function(){
    
},

/** send request to download parameters to a file 
*/
sendDownloadParameters(){
    
    app.working = true;
    app.send_message("download_parameters", {"session_id" : app.session_id,});
},

/** download parameter set into a file 
 @param message_data {json} result of file request, either sucess or fail with errors
*/
takeDownloadParameters(message_data){

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
uploadParameterset:function(){  

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

                app.uploadParametersetMessaage = response.data.message.message;
                app.session = response.data.session;
                app.uploadParametersetButtonText= 'Upload <i class="fas fa-upload"></i>';
                location.reload();

            })
            .catch(function (error) {
                console.log(error);
                app.searching=false;
            });                        
},

//direct upload button click
uploadAction:function(){
    if(app.upload_file == null)
        return;

    app.uploadParametersetMessaage = "";
    app.uploadParametersetButtonText = '<i class="fas fa-spinner fa-spin"></i>';

    if(app.upload_mode == "parameters")
    {
        this.uploadParameterset();
    }
    else
    {
        
    }

},

//file upload
handleFileUpload:function(){
    app.upload_file = this.$refs.file.files[0];
    app.upload_file_name = app.upload_file.name;
},

/** show upload parameters modal
*/
showUploadParameters:function(upload_mode){
    app.upload_mode = upload_mode;
    app.uploadParametersetMessaage = "";

    app.parameterSetModal.show();
},

/**hide upload parameters modal
*/
hideUploadParameters:function(){
},