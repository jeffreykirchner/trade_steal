
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//vue app
var app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chatSocket : "",
                    reconnecting : true,
                    working : false,
                    first_load_done : false,          //true after software is loaded for the first time
                    sessionID : {{session.id}},
                    session : {
                        current_period : 1,
                        started : false,
                        locked : true,
                        start_date : "---",
                        current_period : 0,
                        finished : false,                        
                        parameter_set : {
                            id : 0,
                            period_count : 0,
                            period_length_production : 0,
                            period_length_trade : 0,
                            break_period_frequency : 0,
                            good_one_label : "",
                            good_two_label : "",
                            good_one_rgb_color : '#000000',
                            good_two_rgb_color : '#000000',
                            parameter_set_types : [{good_one_amount:""},
                                                   {good_one_amount:""}],                               
                        },
                        session_periods : [],
                    },
                   
                    downloadParametersetButtonText:'Download <i class="fas fa-download"></i>',
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
                    },
                    current_parameter_set_player_group : {
                        id : 0,
                        group_number : 0,
                        period :0,
                    },
                    parameterset_form_ids: {{parameterset_form_ids|safe}},
                    parameterset_type_form_ids: {{parameterset_type_form_ids|safe}},
                    parameterset_player_form_ids: {{parameterset_player_form_ids|safe}},
                    parameterset_player_group_form_ids: {{parameterset_player_group_form_ids|safe}},
                    upload_file: null,
                    upload_file_name:'Choose File',
                    uploadParametersetButtonText:'Upload  <i class="fas fa-upload"></i>',
                    uploadParametersetMessaage:'',
                    show_parameters:false,
                    import_parameters_message : "",
                    move_to_next_period_text : 'Move to next period <i class="fas fa-fast-forward"></i>',
 
                }},
    methods: {

        /** fire when websocket connects to server
        */
        handleSocketConnected(){            
            app.sendGetSession();
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        takeMessage(data) {
            app.first_load_done = true;

            console.log(data);

            messageType = data.message.messageType;
            messageData = data.message.messageData;

            switch(messageType) {                
                case "get_session":
                    app.takeGetSession(messageData);
                    break;
                case "update_session":
                    app.takeUpdateSession(messageData);
                    break;
                case "update_parameterset":
                    app.takeUpdateParameterset(messageData);
                    break;         
                case "update_parameterset_type":
                    app.takeUpdateParametersetType(messageData);
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
                case "start_experiment":
                    app.takeStartExperiment(messageData);
                    break;
                case "reset_experiment":
                    app.takeResetExperiment(messageData);
                    break;
                case "next_period":
                    app.takeNextPeriod(messageData);
                    break;   
            }

            app.working = false;
            //Vue.nextTick(app.update_sdgraph_canvas());
        },

        /** send websocket message to server
        *    @param messageType {string} type of message sent to server
        *    @param messageText {json} body of message being sent to server
        */
        sendMessage(messageType, messageText) {
            

            app.$data.chatSocket.send(JSON.stringify({
                    'messageType': messageType,
                    'messageText': messageText,
                }));
        },

        /** take create new session
        *    @param messageData {json} session day in json format
        */
        takeGetSession(messageData){
            
            app.$data.session = messageData.session;

            if(app.$data.session.started)
            {
                app.$data.show_parameters = false;

                if(app.$data.session.finished)
                {
                    app.$data.session.current_period = 1;
                }
                else
                {
                    
                }
            }
            else
            {
                app.$data.show_parameters = true;
            }

            app.updateMoveOnButtonText();
        },

        /**update text of move on button based on current state
         */
        updateMoveOnButtonText(){
            if(app.$data.session.finished)
            {
                app.$data.move_to_next_period_text = '** Experiment complete **';
            }
            else if(app.$data.session.started)
            {
                if(app.$data.session.current_period == app.$data.session.parameter_set.number_of_periods)
                {
                    app.$data.move_to_next_period_text = 'Complete experiment <i class="fas fa-flag-checkered"></i>';
                }
                else
                {
                    app.$data.move_to_next_period_text = 'Move to next period <i class="fas fa-fast-forward"></i>';
                }
            }
        },

        /** send winsock request to get session info
        */
        sendGetSession(){
            app.sendMessage("get_session",{"sessionID" : app.$data.sessionID});
        },

        /** send session update form   
        */
        sendUpdateSession(){
            app.$data.cancelModal = false;
            app.$data.working = true;
            app.sendMessage("update_session",{"formData" : $("#sessionForm").serializeArray(),
                                              "sessionID" : app.$data.sessionID});
        },

        /** take update session reponse
         * @param messageData {json} result of update, either sucess or fail with errors
        */
        takeUpdateSession(messageData){
            app.clearMainFormErrors();

            if(messageData.status == "success")
            {
                app.takeGetSession(messageData);       
                $('#editSessionModal').modal('hide');    
            } 
            else
            {
                app.$data.cancelModal=true;                           
                app.displayErrors(messageData.errors);
            } 
        },

        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },

        {%include "staff/staff_session/parameters_card.js"%}
        {%include "staff/staff_session/control_card.js"%}
        {%include "staff/staff_session/session_card.js"%}
    
        
        /** clear form error messages
        */
        clearMainFormErrors(){
            
            for(var item in app.$data.session)
            {
                $("#id_" + item).attr("class","form-control");
                $("#id_errors_" + item).remove();
            }

            s = app.$data.parameterset_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.$data.parameterset_type_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.$data.parameterset_player_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }

            s = app.$data.parameterset_player_group_form_ids;
            for(var i in s)
            {
                $("#id_" + s[i]).attr("class","form-control");
                $("#id_errors_" + s[i]).remove();
            }
        },

        /** display form error messages
        */
        displayErrors(errors){
            for(var e in errors)
            {
                $("#id_" + e).attr("class","form-control is-invalid")
                var str='<span id=id_errors_'+ e +' class="text-danger">';
                
                for(var i in errors[e])
                {
                    str +=errors[e][i] + '<br>';
                }

                str+='</span>';
                $("#div_id_" + e).append(str); 

                var elmnt = document.getElementById("div_id_" + e);
                elmnt.scrollIntoView(); 

            }
        }, 

    },

    mounted(){
        $('#editSessionModal').on("hidden.bs.modal", this.hideEditSession); 
        $('#importParametersModal').on("hidden.bs.modal", this.hideImportParameters); 
        $('#editParametersetModal').on("hidden.bs.modal", this.hideEditParameterset);
        $('#editParametersetTypeModal').on("hidden.bs.modal", this.hideEditParametersetType);
        $('#editParametersetPlayerModal').on("hidden.bs.modal", this.hideEditParametersetPlayer);
        $('#editParametersetPlayerGroupModal').on("hidden.bs.modal", this.hideEditParametersetPlayerGroup);
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

//setup pixi app
app.$data.pixi_app = new PIXI.Application({resizeTo : document.getElementById('sd_graph_id'),
                                     backgroundColor : 0xFFFFFF,
                                     autoResize: true,
                                     resolution: devicePixelRatio,
                                     view: document.getElementById('sd_graph_id') });

// Create the sprite and add it to the stage
app.$data.sprite = PIXI.Sprite.from('/static/houseYou.bmp');
app.$data.pixi_app.stage.addChild(app.$data.sprite);

  