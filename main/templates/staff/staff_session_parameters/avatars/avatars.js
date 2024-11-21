/**show edit paramter set avatar
 */
 showEditParametersetAvatar(index){
    app.clearMainFormErrors();
    this.cancelModal=true;
    this.paramtersetAvatarBeforeEdit = Object.assign({}, this.session.parameter_set.parameter_set_avatars[index]);
    this.paramtersetAvatarBeforeEditAvatar = Object.assign({}, this.session.parameter_set.parameter_set_avatars[index].avatar);
    this.paramtersetAvatarBeforeEditIndex = index;
    this.current_parameter_set_avatar = Object.assign({}, this.session.parameter_set.parameter_set_avatars[index]);

    if(!this.current_parameter_set_avatar.avatar)
    {
        this.current_parameter_set_avatar.avatar = {id:-1}
    }

    app.editAvatarsModal.show();
},

/** hide edit session modal
*/
hideEditParametersetAvatar(){
    if(this.cancelModal)
    {
       // Object.assign(this.session.parameter_set.parameter_set_avatars[this.paramtersetAvatarBeforeEditIndex], this.paramtersetAvatarBeforeEdit);

        // if(this.current_parameter_set_avatar.avatar)
        //     if(this.current_parameter_set_avatar.avatar.id == -1)
        //         this.session.parameter_set.parameter_set_avatars[this.paramtersetAvatarBeforeEditIndex].avatar = null;
    }
},

/** update parameterset avatar 
*/
sendUpdateParametersetAvatar(){
    
    app.working = true;

    app.send_message("update_parameterset_avatar", {"sessionID" : app.sessionID,
                                                   "parameterset_avatar_id" : this.session.parameter_set.parameter_set_avatars[this.paramtersetAvatarBeforeEditIndex].id,
                                                   "formData" : {"avatar" : this.current_parameter_set_avatar.avatar.id}});
},

/** handle result of updating parameter set
*/
takeUpdateParametersetAvatar(message_data){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    this.cancelModal=false;
    app.clearMainFormErrors();

    if(message_data.status.value == "success")
    {
        app.session.parameter_set = message_data.status.result;
        app.editAvatarsModal.hide();           
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(message_data.status.errors);
    } 
},