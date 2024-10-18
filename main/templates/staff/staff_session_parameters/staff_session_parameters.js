
{% load static %}

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    first_load_done : false,          //true after software is loaded for the first time
                    helpText : "Loading ...",
                    sessionID : {{session.id}},
                    session : {{session_json|safe}},
                       
                    valuecost_modal_label:'Edit Value or Cost',
                    current_parameterset_type:{                       //json attached to parameterset type edit modal
                        id:0,
                        good_one_amount:0,
                        good_two_amount:0,
                        good_one_production_1:0,
                        good_one_production_2:0,
                        good_one_production_3:0,
                        good_two_production_1:0,
                        good_two_production_2:0,
                        good_two_production_3:0,
                    },
                    current_parameter_set_player : {
                        id:0,
                        id_label:"",
                        location:1,      
                        subject_type:"",            
                        good_one:{id:0},
                        good_two:{id:0},
                        good_three:{id:0},
                        avatar:{id:0},
                        parameter_set_type:{id:0},     
                    },
                    current_parameter_set_player_group : {
                        id : 0,
                        group_number : 0,
                        period :0,
                    },
                    current_parameter_set_good:{
                        id : 0,
                        label : 0,
                        rgb_color :0,
                    },
                    current_parameter_set_avatar:{
                        id : 0,
                        grid_location_row : 0,
                        grid_location_col : 0,
                        avatar : {id:0},
                    },

                    parameterset_form_ids: {{parameterset_form_ids|safe}},
                    parameterset_type_form_ids: {{parameterset_type_form_ids|safe}},
                    parameterset_player_form_ids: {{parameterset_player_form_ids|safe}},
                    parameterset_player_group_form_ids: {{parameterset_player_group_form_ids|safe}},
                    parameterset_good_form_ids: {{parameterset_good_form_ids|safe}},
                    parameterset_avatar_form_ids: {{parameterset_avatar_form_ids|safe}},

                    upload_file: null,
                    upload_file_name:'Choose File',
                    uploadParametersetButtonText:'Upload  <i class="fas fa-upload"></i>',
                    uploadParametersetMessaage:'',
                    // show_parameters:false,
                    import_parameters_message : "",

                    importParametersModal : null,
                    editParametersetModal : null,
                    editParametersetTypeModal : null,
                    editParametersetPlayerModal : null,
                    editParametersetPlayerGroupModal : null,
                    editParametersetGoodModal : null,
                    editAvatarsModal : null,
                    parameterSetModal : null,

                    //form paramters
                    session_import : null,

                }},
    methods: {

        /** fire when websocket connects to server
        */
        handleSocketConnected(){            
            // app.sendGetSession();
            if(!app.first_load_done)
            {
                Vue.nextTick(() => {
                    app.do_first_load();
                });
            }
        },

        handle_socket_connection_try: function handle_socket_connection_try(){         
            
            return true;
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        takeMessage(data) {

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            messageType = data.message.messageType;
            messageData = data.message.messageData;

            switch(messageType) {                
                case "get_session":
                    app.takeGetSession(messageData);
                    break;
                case "update_parameterset":
                    app.takeUpdateParameterset(messageData);
                    break;         
                case "update_parameterset_type":
                    app.takeUpdateParametersetType(messageData);
                    break;    
                case "update_parameterset_good":
                    app.takeUpdateParametersetGood(messageData);
                    break; 
                case "update_parameterset_player":
                    app.takeUpdateParametersetPlayer(messageData);
                    break;     
                case "remove_parameterset_player":
                    app.takeRemoveParameterSetPlayer(messageData);
                    break;
                case "add_parameterset_player":
                    app.takeAddParameterSetPlayer(messageData);
                    break;
                case "update_parameterset_player_group":
                    app.takeUpdateParametersetPlayerGroup(messageData);
                    break;
                case "copy_group_forward":
                    app.takeCopyGroupForward(messageData);
                    break;
                case "import_parameters":
                    app.takeImportParameters(messageData);
                    break;
                case "download_parameters":
                    app.takeDownloadParameters(messageData);
                    break;
                case "update_parameterset_avatar":
                    app.takeUpdateParametersetAvatar(messageData);
                    break;
                case "help_doc":
                    app.takeLoadHelpDoc(messageData);
                    break;
            }

            // if(!app.first_load_done)
            // {
            //     if(!app.session.started)
            //     {
            //         app.show_parameters = true;
            //     }
            // }

            

            app.working = false;
            //Vue.nextTick(app.update_sdgraph_canvas());
        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage(messageType, messageText) {
            

            app.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        do_first_load: function do_first_load()
        {
            
            app.importParametersModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('importParametersModal'), {keyboard: false})
            app.editParametersetModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editParametersetModal'), {keyboard: false})
            app.editParametersetTypeModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editParametersetTypeModal'), {keyboard: false})
            app.editParametersetPlayerModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editParametersetPlayerModal'), {keyboard: false})
            app.editParametersetPlayerGroupModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editParametersetPlayerGroupModal'), {keyboard: false})
            app.editParametersetGoodModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editParametersetGoodModal'), {keyboard: false})
            app.editAvatarsModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editAvatarsModal'), {keyboard: false})
            app.parameterSetModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('parameterSetModal'), {keyboard: false})

            document.getElementById('importParametersModal').addEventListener('hidden.bs.modal', app.hideImportParameters);
            document.getElementById('editParametersetModal').addEventListener('hidden.bs.modal', app.hideEditParameterset);
            document.getElementById('editParametersetTypeModal').addEventListener('hidden.bs.modal', app.hideEditParametersetType);
            document.getElementById('editParametersetPlayerModal').addEventListener('hidden.bs.modal', app.hideEditParametersetPlayer);
            document.getElementById('editParametersetPlayerGroupModal').addEventListener('hidden.bs.modal', app.hideEditParametersetPlayerGroup);
            document.getElementById('editParametersetGoodModal').addEventListener('hidden.bs.modal', app.hideEditParametersetGood);
            document.getElementById('editAvatarsModal').addEventListener('hidden.bs.modal', app.hideEditParametersetAvatar);
            document.getElementById('parameterSetModal').addEventListener('hidden.bs.modal', app.hideParameterSet);

            app.first_load_done = true;
        },

        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession(messageData){
            
            app.session = messageData.session;

            if(!app.first_load_done)
            {
                Vue.nextTick(() => {
                    app.do_first_load();
                });
            }

            if(app.session.started)
            {
                
            }
            else
            {
                
            }                     
        },

        /** send winsock request to get session info
        */
        // sendGetSession(){
        //     app.sendMessage("get_session",{"sessionID" : app.sessionID});
        // },

        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },

        {%include "staff/staff_session_parameters/general_settings/general_settings.js"%}
        {%include "staff/staff_session_parameters/good_settings/good_settings.js"%}
        {%include "staff/staff_session_parameters/control/control.js"%}
        {%include "staff/staff_session_parameters/player_types/player_type.js"%}
        {%include "staff/staff_session_parameters/players/players.js"%}
        {%include "staff/staff_session_parameters/avatars/avatars.js"%}
        {%include "js/help_doc.js"%}
    
        /** clear form error messages
        */
        clearMainFormErrors(){
            
            for(let item in app.session)
            {
                let e = document.getElementById("id_errors_" + item);
                if(e) e.remove();
            }

            s = app.parameterset_form_ids;
            for(let i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = app.parameterset_type_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = app.parameterset_player_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = app.parameterset_player_group_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = app.parameterset_good_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }

            s = app.parameterset_avatar_form_ids;
            for(var i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }
        },

        /** display form error messages
        */
        displayErrors(errors){
            for(let e in errors)
                {
                    //e = document.getElementById("id_" + e).getAttribute("class", "form-control is-invalid")
                    let str='<span id=id_errors_'+ e +' class="text-danger">';
                    
                    for(let i in errors[e])
                    {
                        str +=errors[e][i] + '<br>';
                    }

                    str+='</span>';

                    document.getElementById("div_id_" + e).insertAdjacentHTML('beforeend', str);
                    document.getElementById("div_id_" + e).scrollIntoView(); 
                }
        }, 
    },

    mounted(){
       
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  