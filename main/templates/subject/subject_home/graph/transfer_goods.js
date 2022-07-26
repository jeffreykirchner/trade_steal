/** show transfer modal when mouse up on valid target
*/
showTransferModal(container){

    if(app.pixi_modal_open) return;

    if(!app.$data.pixi_transfer_line.visible ||
       container ==  app.$data.pixi_transfer_source ||
       app.$data.pixi_transfer_source == null ||
       app.$data.pixi_transfer_target == null)
    {
        app.turnOffHighlights();
        return;
    } 

    parameter_set = app.$data.session.parameter_set;

    app.$data.transfer_source_modal_string = app.$data.pixi_transfer_source.name.modal_label;
    app.$data.transfer_target_modal_string = app.$data.pixi_transfer_target.name.modal_label;

    app.$data.transfer_modal_good_one_rgb = app.$data.pixi_transfer_source.name.good_one_color;
    app.$data.transfer_modal_good_two_rgb = app.$data.pixi_transfer_source.name.good_two_color;

    app.$data.transfer_modal_good_one_name = app.$data.pixi_transfer_source.name.good_a_label;
    app.$data.transfer_modal_good_two_name = app.$data.pixi_transfer_source.name.good_b_label;

    app.$data.pixi_modal_open = true;
    app.$data.cancelModal=true;

    if(parameter_set.good_count == 2 || app.$data.pixi_transfer_source.name.type == "field")
    {
        var myModal = new bootstrap.Modal(document.getElementById('moveTwoGoodsModal'), {
            keyboard: false
            })
    }
    else
    {
        app.$data.transfer_modal_good_three_rgb = app.$data.pixi_transfer_source.name.good_three_color;
        app.$data.transfer_modal_good_three_name = app.$data.pixi_transfer_source.name.good_c_label;

        var myModal = new bootstrap.Modal(document.getElementById('moveThreeGoodsModal'), {
            keyboard: false
            })
    }

    myModal.toggle();
},

/** hide transfer modal
*/
hideTransferModal:function(){
    
    app.clearMainFormErrors();

    if(app.$data.cancelModal)
    {
       app.$data.transfer_good_one_amount = 0;
       app.$data.transfer_good_two_amount = 0;
       app.$data.transfer_good_three_amount = 0;
    }

    app.$data.pixi_modal_open = false;
    app.turnOffHighlights();
},

sendMoveGoods(){
    
    if(this.working == true) return;
    if(!this.pixi_transfer_source) return;
    if(!this.pixi_transfer_target) return; 

    app.clearMainFormErrors();

    if(this.pixi_transfer_source.name.type == "house" &&
       this.session.parameter_set.good_count == 3)
    {
        if(this.transfer_good_one_amount == 0 && 
           this.transfer_good_two_amount == 0 &&
           this.transfer_good_three_amount == 0)
        {
            let errors = {transfer_good_one_amount_3g:["Invalid Entry."]};
            this.displayErrors(errors);
            return;
        }

        var form_data = $("#moveThreeGoodsForm").serializeArray();
    }
    else
    {
         if(this.transfer_good_one_amount == 0 && 
            this.transfer_good_two_amount == 0)
         {
             let errors = {transfer_good_one_amount_2g:["Invalid Entry."]};
             this.displayErrors(errors);
             return;
         }

        var form_data = $("#moveTwoGoodsForm").serializeArray();
    }

    this.working = true;
    app.sendMessage("move_goods", {"sourceType" : this.pixi_transfer_source.name.type.toString(),
                                   "sourceID" :  this.pixi_transfer_source.name.user_id.toString(),

                                   "targetType" : this.pixi_transfer_target.name.type.toString(),
                                   "targetID" : this.pixi_transfer_target.name.user_id.toString(),

                                   "formData" : form_data,});
},

/** take result of moving goods
*/
takeMoveGoods(messageData){
    //app.$data.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeUpdateGoods(messageData);    
        this.closeMoveModal();               
    } 
    else
    {
        app.$data.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    }
},

/**
 * close and reset the move modals
 */
closeMoveModal(){
    let e1 = document.getElementById('moveTwoGoodsModal');
    let modal = bootstrap.Modal.getInstance(e1);
    if(modal) modal.hide();

    let e2 = document.getElementById('moveThreeGoodsModal');
    let modal2 = bootstrap.Modal.getInstance(e2);
    if(modal2) modal2.hide();

    this.transfer_good_one_amount = 0;  
    this.transfer_good_two_amount = 0;  
    this.transfer_good_three_amount = 0;
},

/** take updated data from goods being moved by another player
*    @param messageData {json} session day in json format
*/
takeUpdateMoveGoods(messageData){
    app.takeUpdateGoods(messageData);
},

/** update good counts of players in list
*    @param messageData {json} session day in json format
*/
takeUpdateGoods(messageData){
    results = messageData.status.result;

    let session_player = this.session_player;

    for(let r=0; r<results.length; r++){
        player_id = results[r].id;
        
        //update session player
        if(this.is_subject)
        {
            if(player_id == session_player.id)
            {
                session_player.good_one_house = results[r].good_one_house;
                session_player.good_two_house = results[r].good_two_house;
                session_player.good_three_house = results[r].good_three_house;

                session_player.good_one_field = results[r].good_one_field;
                session_player.good_two_field = results[r].good_two_field; 

                if(results[r].notice)
                {
                    session_player.notices.push(results[r].notice);

                    //scroll to view
                    if(session_player.notices.length>0)
                    {
                        Vue.nextTick(() => {app.updateNoticeDisplayScroll()});        
                    }
                }
            }
        }

        player = this.findSessionPlayer(player_id);

        if(player)
        {
            player.good_one_house = results[r].good_one_house;
            player.good_two_house = results[r].good_two_house;
            player.good_three_house = results[r].good_three_house;

            player.good_one_field = results[r].good_one_field;
            player.good_two_field = results[r].good_two_field;               

            player_index = this.findSessionPlayerIndex(player_id);

            app.setupSingleHouse(player_index);
            app.setupSingleField(player_index);
        }        
    }

    if(this.is_subject) app.calcWaste();
},

/**
 * scroll notice text to the bottom
 */
updateNoticeDisplayScroll(){
    // if(this.session_player.notices.length==0) return;

    // var elmnt = document.getElementById("notice_id_" + app.$data.session_player.notices[app.$data.session_player.notices.length-1].id.toString());
    // elmnt.scrollIntoView(); 
},
