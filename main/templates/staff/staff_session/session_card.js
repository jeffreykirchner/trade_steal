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